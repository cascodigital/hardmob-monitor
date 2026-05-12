# HardMOB Monitor

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Author](https://img.shields.io/badge/Author-Casco%20Digital-orange)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat-square&logo=telegram&logoColor=white)
![RSS](https://img.shields.io/badge/RSS-Feed-FFA500?style=flat-square&logo=rss&logoColor=white)

Monitor de novos topicos no forum de promocoes do [HardMOB](https://www.hardmob.com.br/forumdisplay.php?f=407). Usa FlareSolverr para bypass de Cloudflare.

Disponivel em duas versoes:

| | Telegram | RSS |
|---|---|---|
| **Pasta** | `/` (raiz) | `rss/` |
| **Como funciona** | Scrapa a cada 10min e envia mensagem no Telegram | Serve feed RSS com conteudo dos posts para qualquer leitor |
| **Requer** | Bot Telegram | Leitor RSS (ex: Tiny Tiny RSS) |
| **Notificacao** | Push via Telegram | Pelo proprio leitor RSS |

---

## Opcao 1 — Telegram

Scrapa o forum a cada 10 minutos e envia uma mensagem via Telegram Bot API para cada topico novo.

### Quick Start

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

### Personalizacao

```python
CHECK_INTERVAL = 600   # Intervalo em segundos (padrao: 10min)
FORUM_URL = "https://www.hardmob.com.br/forumdisplay.php?f=407"
```

### Stack

- Python 3.11 + BeautifulSoup4
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) (bypass Cloudflare)
- Telegram Bot API
- Docker Compose

---

## Opcao 2 — RSS

Servidor RSS que expoe um feed compativel com qualquer leitor (Tiny Tiny RSS, Feedly, etc). Inclui o conteudo completo do primeiro post de cada topico. Novos topicos sao detectados a cada 10 minutos; o conteudo de cada thread e buscado em background logo apos a descoberta.

### Quick Start

```bash
git clone https://github.com/cascodigital/hardmob-monitor.git
cd hardmob-monitor/rss
docker compose up -d
```

O feed estara disponivel em `http://localhost:8099/feed?token=hm0b-k1ttl3r-rss`.

> **Troque o token** em `app.py` antes de expor publicamente:
> ```python
> FEED_TOKEN = "seu_token_secreto"
> ```

### Expondo com Cloudflare Tunnel

O `docker-compose.yml` do RSS se conecta a uma rede Docker externa chamada `hmob_hmob_network` (criada pelo compose da versao Telegram, que inclui o FlareSolverr). Se voce rodar o RSS standalone sem o Telegram, suba o FlareSolverr separadamente ou ajuste `FLARESOLVERR_URL` em `app.py` para o endereco do seu FlareSolverr.

Para expor com Cloudflare Tunnel, adicione um hostname no seu tunnel apontando para `http://<ip-do-servidor>:8099` e use a URL publica com o token:

```
https://seudominio.com/feed?token=seu_token_secreto
```

### Personalizacao

```python
REFRESH_INTERVAL = 600   # Intervalo de scrape em segundos (padrao: 10min)
FORUM_URL = "https://www.hardmob.com.br/forumdisplay.php?f=407"
FEED_TOKEN = "hm0b-k1ttl3r-rss"   # Token de acesso ao feed
```

### Stack

- Python 3.11 + BeautifulSoup4 + Flask
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) (bypass Cloudflare)
- Docker Compose

---

## Aviso

Ferramenta de automacao pessoal. Sem afiliacao com HardMOB. Respeite os termos de servico do site.

---

Desenvolvido com 🐢 (e cafe) por **Casco Digital**.
