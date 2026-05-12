import threading
import time
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.etree.ElementTree import Element, SubElement, tostring

import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, request, abort

FORUM_URL = "https://www.hardmob.com.br/forumdisplay.php?f=407"
FLARESOLVERR_URL = "http://flaresolverr:8191/v1"
REFRESH_INTERVAL = 600
FEED_TOKEN = "hm0b-k1ttl3r-rss"

app = Flask(__name__)

# {url: {"title": str, "description": str, "fetched_at": datetime}}
_content_cache = {}
_items_order = []  # mantém ordem de descoberta
_lock = threading.Lock()
_fetch_queue = []
_queue_lock = threading.Lock()


def flare_get(url):
    resp = requests.post(
        FLARESOLVERR_URL,
        json={"cmd": "request.get", "url": url, "maxTimeout": 60000},
        headers={"Content-Type": "application/json"},
        timeout=65,
    )
    result = resp.json()
    if result.get("status") != "ok":
        return None
    return result.get("solution", {}).get("response", "")


def scrape_listing():
    html = flare_get(FORUM_URL)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    for selector in (".threadtitle a", "a.threadtitle", "h3.threadtitle a"):
        links = soup.select(selector)
        if links:
            items = []
            for link in links:
                title = link.text.strip()
                href = link.get("href", "")
                if title and "threads/" in href:
                    if not href.startswith("http"):
                        href = "https://www.hardmob.com.br/" + href
                    items.append({"title": title, "url": href})
            return items
    return []


def scrape_thread(url):
    html = flare_get(url)
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    # seletores vBulletin para o primeiro post
    for selector in (
        ".postrow:first-of-type .content",
        "#posts .postrow .content",
        ".postcontent",
        "div.content",
    ):
        el = soup.select_one(selector)
        if el and len(el.get_text(strip=True)) > 30:
            return str(el)
    return ""


def fetch_worker():
    while True:
        url = None
        with _queue_lock:
            if _fetch_queue:
                url = _fetch_queue.pop(0)
        if url:
            print(f"  [fetch] {url}")
            try:
                desc = scrape_thread(url)
                with _lock:
                    if url in _content_cache:
                        _content_cache[url]["description"] = desc
                        _content_cache[url]["fetched_at"] = datetime.now(timezone.utc)
            except Exception as e:
                print(f"  [fetch] erro: {e}")
            time.sleep(3)  # pausa entre fetches pra não martelas o FlareSolverr
        else:
            time.sleep(5)


def refresh_loop():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizando listagem...")
        try:
            items = scrape_listing()
            now = datetime.now(timezone.utc)
            new_urls = []
            with _lock:
                for item in items:
                    url = item["url"]
                    if url not in _content_cache:
                        _content_cache[url] = {
                            "title": item["title"],
                            "description": "",
                            "fetched_at": None,
                            "discovered_at": now,
                        }
                        _items_order.append(url)
                        new_urls.append(url)
                    else:
                        # atualiza título se mudou
                        _content_cache[url]["title"] = item["title"]
            with _queue_lock:
                for url in new_urls:
                    if url not in _fetch_queue:
                        _fetch_queue.append(url)
            print(f"  {len(items)} topicos, {len(new_urls)} novos para buscar conteudo")
        except Exception as e:
            print(f"Erro refresh: {e}")
        time.sleep(REFRESH_INTERVAL)


def build_rss():
    with _lock:
        order = list(_items_order)
        cache = {k: dict(v) for k, v in _content_cache.items()}

    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "HardMob Promocoes"
    SubElement(channel, "link").text = "https://www.hardmob.com.br/forums/407-Promocoes"
    SubElement(channel, "description").text = "Novos topicos em HardMob Promocoes"
    SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))

    for url in order:
        item_data = cache.get(url, {})
        entry = SubElement(channel, "item")
        SubElement(entry, "title").text = item_data.get("title", "")
        SubElement(entry, "link").text = url
        SubElement(entry, "guid", isPermaLink="true").text = url
        desc = item_data.get("description", "")
        if desc:
            SubElement(entry, "description").text = desc
        discovered = item_data.get("discovered_at")
        if discovered:
            SubElement(entry, "pubDate").text = format_datetime(discovered)

    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(rss, encoding="unicode").encode()


@app.route("/feed")
def feed():
    if request.args.get("token") != FEED_TOKEN:
        abort(403)
    return Response(build_rss(), mimetype="application/rss+xml")


@app.route("/")
def index():
    if request.args.get("token") != FEED_TOKEN:
        abort(403)
    with _lock:
        total = len(_content_cache)
        with_content = sum(1 for v in _content_cache.values() if v.get("description"))
    with _queue_lock:
        queued = len(_fetch_queue)
    return f"HardMob RSS | {total} topicos | {with_content} com conteudo | {queued} na fila"


if __name__ == "__main__":
    threading.Thread(target=refresh_loop, daemon=True).start()
    threading.Thread(target=fetch_worker, daemon=True).start()
    app.run(host="0.0.0.0", port=8099)
