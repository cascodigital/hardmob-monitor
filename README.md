# hardmob-monitor

A small self-hosted service that publishes new threads from the HardMOB deals forum as a token-protected RSS feed, for anyone who follows deals in an RSS reader.

![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.11-3776AB) ![Status](https://img.shields.io/badge/status-maintained-blue)

## Overview

The [HardMOB](https://www.hardmob.com.br/) deals forum (section 407) has no usable RSS feed, so new
deals only show up by reloading the forum page. This service polls the forum listing, fetches the
first post of each new thread in the background and serves everything as a standard RSS 2.0 feed
that works with Tiny Tiny RSS, Feedly and other readers. It runs as two containers with Docker Compose.

## Features

- Polls the forum listing every 10 minutes and tracks threads in discovery order.
- Fetches the first post of each new thread in a background worker and uses it as the item description.
- Serves an RSS 2.0 feed with title, link, GUID, description and discovery date per item.
- Protects both the feed and the status endpoint with a shared token (`FEED_TOKEN`).
- Exposes a one-line status page with thread count, items with content and queue length.
- Ships with Docker Compose, including healthchecks and a bundled FlareSolverr container that the service uses to load forum pages.

## How it works

```
                 every 600 s                      queue of new thread URLs
 refresh_loop ──────────────► FlareSolverr ──► forum listing ──► fetch_worker
      │                        (container)                           │ first post HTML
      ▼                                                              ▼
 in-memory cache {url: title, description, discovered_at} ◄──────────┘
      │
      ▼
 Flask :8099   /feed?token=...  -> RSS 2.0
               /?token=...      -> status line
```

- Page loads go through a [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) container on the internal Compose network (`http://flaresolverr:8191/v1`), which renders the pages in a headless browser.
- Thread links are extracted with several vBulletin CSS selectors in order, so minor template changes do not break the listing.
- The worker waits 3 seconds between thread fetches to keep the load on the forum and on FlareSolverr low.
- State is kept in memory only; items are not persisted across restarts.

## Requirements

- Docker with the Compose plugin
- Outbound HTTPS access to `www.hardmob.com.br`
- An RSS reader that can subscribe to a URL with a query-string token

## Quick start

1. Clone and configure the token (any random string you choose):

   ```bash
   git clone https://github.com/cascodigital/hardmob-monitor.git
   cd hardmob-monitor/rss
   cp .env.example .env
   # edit FEED_TOKEN in .env
   ```

2. Start both containers:

   ```bash
   docker compose up -d
   ```

3. Check the status endpoint (the first refresh runs on startup):

   ```bash
   curl "http://localhost:8099/?token=YOUR_TOKEN"
   ```

   Then subscribe your reader to `http://localhost:8099/feed?token=YOUR_TOKEN`.

## Configuration

| Variable / key | Required | Default | Description |
|---|---|---|---|
| `FEED_TOKEN` (env / `.env`) | Yes | `change-me` | Shared token required on `/feed` and `/`; requests without it get HTTP 403 |
| `TZ` (compose) | No | `America/Sao_Paulo` | Container time zone |
| `REFRESH_INTERVAL` (`app.py`) | No | `600` | Seconds between listing refreshes |
| `FORUM_URL` (`app.py`) | No | forum section 407 | Forum listing to monitor |
| `FLARESOLVERR_URL` (`app.py`) | No | `http://flaresolverr:8191/v1` | FlareSolverr endpoint |

The service listens on port `8099` (published by `docker-compose.yml`).

## Usage

| Endpoint | What it returns |
|---|---|
| `GET /feed?token=...` | RSS 2.0 feed (`application/rss+xml`) |
| `GET /?token=...` | Status line, e.g. `HardMob RSS \| 40 threads \| 38 with content \| 2 queued` |

To reach the feed from outside your network, put it behind a reverse proxy or a tunnel (for example
Cloudflare Tunnel pointing a hostname to `http://<server>:8099`) and subscribe with the public URL plus
the token. Use a long random token, since it is the only access control.

## Limitations

- In-memory state: a restart empties the feed until the next refresh, and the item list grows without limit while the process runs.
- Only the first page of the forum listing is read on each refresh.
- The token travels in the query string, so it can end up in proxy and reader logs.
- Parsing depends on the forum's vBulletin markup; a layout change can produce an empty feed.
- Feed channel title and description are in Portuguese, matching the forum.
- Not affiliated with HardMOB. Use it in line with the site's terms of service and keep the polling interval reasonable.

## License

MIT — see [LICENSE](LICENSE).
