<div align="center">

# HardMOB RSS Monitor

**RSS feed for new HardMOB promotions, with FlareSolverr-backed scraping.**

![Status](https://img.shields.io/badge/Status-Active-16A34A?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-2563EB?style=flat-square)
![Casco Digital](https://img.shields.io/badge/Casco-Digital-111827?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![RSS](https://img.shields.io/badge/RSS-Feed-FFA500?style=flat-square&logo=rss&logoColor=white)

</div>

---

Servidor RSS para novos topicos no forum de promocoes do [HardMOB](https://www.hardmob.com.br/forumdisplay.php?f=407). Usa FlareSolverr para bypass de Cloudflare e expoe um feed compativel com Tiny Tiny RSS, Feedly e outros leitores.

O conteudo do primeiro post de cada topico e buscado em background logo apos a descoberta, para que o leitor RSS receba titulo, link e descricao quando disponivel.

## Quick Start

```bash
git clone https://github.com/cascodigital/hardmob-monitor.git
cd hardmob-monitor/rss
cp .env.example .env
# edite FEED_TOKEN no .env
docker compose up -d
```

Feed:

```text
http://localhost:8099/feed?token=SEU_TOKEN
```

Status:

```text
http://localhost:8099/?token=SEU_TOKEN
```

## Configuracao

Defina o token de acesso por variavel de ambiente:

```bash
FEED_TOKEN="troque-este-token"
```

No Docker Compose, `FEED_TOKEN` e lido do ambiente ou de `.env`. Se nao for definido, o fallback e `change-me`, adequado apenas para teste local.

## Expondo com Cloudflare Tunnel

Crie um hostname no tunnel apontando para:

```text
http://<ip-do-servidor>:8099
```

Use a URL publica com o token:

```text
https://seudominio.com/feed?token=SEU_TOKEN
```

## Personalizacao

No codigo:

```python
REFRESH_INTERVAL = 600
FORUM_URL = "https://www.hardmob.com.br/forumdisplay.php?f=407"
```

## Stack

- Python 3.11 + BeautifulSoup4 + Flask
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)
- Docker Compose

## Aviso

Ferramenta de automacao pessoal. Sem afiliacao com HardMOB. Respeite os termos de servico do site.

---

Desenvolvido com Casco Digital.
