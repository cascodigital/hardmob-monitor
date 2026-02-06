# HardMOB Monitor

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Author](https://img.shields.io/badge/Author-Casco%20Digital-orange)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)

Monitor de novos topicos no forum de promocoes do [HardMOB](https://www.hardmob.com.br/forumdisplay.php?f=407). Verifica a cada 10 minutos e envia notificacao via Telegram. Usa FlareSolverr para bypass de Cloudflare.

## Quick Start

1. Crie um bot no Telegram via [@BotFather](https://t.me/BotFather) e pegue o token + chat_id
2. Edite as credenciais em `monitor_hardmob.py`:
   ```python
   TELEGRAM_BOT_TOKEN = "seu_token"
   TELEGRAM_CHAT_ID = "seu_chat_id"
   ```
3. Execute:
   ```bash
   git clone https://github.com/cascodigital/hardmob-monitor.git
   cd hardmob-monitor
   docker compose up -d
   ```

## Personalizacao

```python
CHECK_INTERVAL = 600   # Intervalo em segundos (padrao: 10min)
FORUM_URL = "https://www.hardmob.com.br/forumdisplay.php?f=407"
```

## Stack

- Python 3.11 + BeautifulSoup4
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) (bypass Cloudflare)
- Telegram Bot API
- Docker Compose

## Aviso

Ferramenta de automacao pessoal. Sem afiliacao com HardMOB. Respeite os termos de servico do site.

---

Desenvolvido com 🐢 (e cafe) por **Casco Digital**.
