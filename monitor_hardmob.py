"""
HardMOB Forum Monitor

Monitora novos topicos no forum de Promocoes do HardMOB a cada 10 minutos.
Usa FlareSolverr para bypass de protecao Cloudflare e envia notificacoes
via Telegram Bot API quando detecta topicos novos.

Requisitos:
    - FlareSolverr rodando (porta 8191)
    - Bot Telegram configurado (token + chat_id)
    - requests, beautifulsoup4

Configuracao:
    Edite TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID e CHECK_INTERVAL abaixo.

Autor: Andre Kittler / Casco Digital
"""

import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TELEGRAM_BOT_TOKEN = "1111:22222222"
TELEGRAM_CHAT_ID = "333"

#FORUM_URL = "https://www.hardmob.com.br/forums/407-Promocoes"
FORUM_URL = "https://www.hardmob.com.br/forumdisplay.php?f=407"
FLARESOLVERR_URL = "http://flaresolverr:8191/v1"
CHECK_INTERVAL = 600

old_topics = set()

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("Notificacao enviada")
    except Exception as e:
        print(f"Erro ao enviar: {e}")

def get_topics():
    try:
        # Usa FlareSolverr para contornar Cloudflare
        payload = {
            "cmd": "request.get",
            "url": FORUM_URL,
            "maxTimeout": 60000
        }
        
        response = requests.post(
            FLARESOLVERR_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=65
        )
        
        if response.status_code != 200:
            print(f"Erro FlareSolverr: {response.status_code}")
            return []
        
        result = response.json()
        
        if result.get("status") != "ok":
            print(f"FlareSolverr erro: {result.get('message')}")
            return []
        
        html_content = result.get("solution", {}).get("response", "")
        
        if not html_content:
            print("HTML vazio retornado")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        selectors = [
            ".threadtitle a",
            "a.threadtitle",
            "h3.threadtitle a"
        ]
        
        topics = []
        for selector in selectors:
            links = soup.select(selector)
            if links:
                print(f"Seletor '{selector}' encontrou {len(links)} elementos")
                for link in links:
                    title = link.text.strip()
                    href = link.get('href', '')
                    if title and 'threads/' in href:
                        if not href.startswith('http'):
                            href = 'https://www.hardmob.com.br/' + href
                        topics.append({'title': title, 'url': href})
                break

        return topics
        
    except Exception as e:
        print(f"Erro ao buscar topicos: {e}")
        return []

def main():
    print("Iniciando monitor do HardMob (FlareSolverr)...")
    
    # Aguarda FlareSolverr iniciar
    print("Aguardando FlareSolverr...")
    time.sleep(10)
    
    try:
        topics = get_topics()
        for topic in topics:
            old_topics.add(topic['url'])
        print(f"{len(old_topics)} topicos carregados")
        send_telegram_message("Monitor do HardMob iniciado com FlareSolverr!")
    except Exception as e:
        print(f"Erro na carga inicial: {e}")
        send_telegram_message(f"Erro ao iniciar: {e}")
    
    while True:
        try:
            now = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{now}] Verificando...")
            
            topics = get_topics()
            new_count = 0
            
            for topic in topics:
                if topic['url'] not in old_topics:
                    print(f"[NOVO] {topic['title']}")
                    msg = f"<b>Novo topico - HardMob</b>\n\n{topic['title']}\n\n{topic['url']}"
                    send_telegram_message(msg)
                    old_topics.add(topic['url'])
                    new_count += 1
            
            if new_count == 0:
                print("Nenhum topico novo")
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado")
