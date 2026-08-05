# clawbot — OpenClaw Agent Gateway + Hugo

A ready-to-use Docker template for running an [OpenClaw](https://openclaw.dev) agent gateway together with the Hugo dev server for the ludekkvapil.cz site.

> **Note:** OSINT / LinkedIn research lives in the separate `osintbot` project, not here. The old Selenium/Gradio LinkedIn stack that used to run in `services/linkedin/` (ports 7860/7861) has been removed — it was superseded by osintbot's Apify-based tooling.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Compose v2
- An OpenAI API key **or** a local model runner (e.g. Docker Model Runner / Ollama)

---

## Quick Start

```bash
# 1. Copy the default env file and fill in your values
cp .env.default .env
# Edit .env — at minimum set OPENAI_API_KEY and OPENCLAW_GATEWAY_TOKEN

# 2. Generate TLS certificates for internal MCP gateway
sh mcp-tls/gen-certs.sh

# 3. Start all services
docker compose up -d

# 4. Get the dashboard URL (wait ~30s for startup + npm update)
docker compose logs openclaw | grep "http://"
```

Open the printed URL in your browser to connect to the gateway.

---

## Environment Variables

Always create `.env` from the template: `cp .env.default .env`, then fill in real values.

All variables are defined in `.env.default`. Copy it to `.env` and fill in real values.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes* | — | OpenAI API key |
| `OPENCLAW_GATEWAY_TOKEN` | Yes | — | Secret token for gateway auth |
| `OPENCLAW_PORT` | No | `18790` | Host port for the gateway (via Nginx proxy) |
| `HUGO_DEV_PORT` | No | `1313` | Host port mapped to Hugo dev server |
| `TARGET_ENV` | No | `dev` | Build stage (`dev` or `production`) |
| `MCP_GATEWAY_TOKEN` | Recommended | — | Bearer token expected by `mcpserver-gateway` |
| `CLAWBOT_MCP_GATEWAY_URL` | No | `https://mcp-gateway.clawbot.internal:8443/mcp/post` | Internal HTTPS URL for MCP gateway |

*\* Not required if using a local model runner (configure `DMR_BASE_URL` instead)*

---

## Dashboard

The gateway dashboard is available at:
```
http://localhost:<OPENCLAW_PORT>/
```

To get the tokenized URL (auto-opens connection):
```bash
docker compose exec -T openclaw openclaw dashboard --no-open 2>&1 | grep "http://"
```

Or check container logs — the URL is printed automatically on startup:
```bash
docker compose logs openclaw | grep "http://"
```

OpenClaw runtime state, including session history, is stored in the named Docker volume `openclaw-runtime` mounted at `/root/.openclaw`. Use `docker compose restart openclaw` for normal restarts. Avoid `docker compose down -v` if you want to keep session history.

---

## Hugo Site Access (OpenClaw + Browser)

The Hugo project is mounted into containers at `/site`.

- OpenClaw to Hugo dev URL (internal Docker DNS): `http://hugo:1313`
- Local browser to Hugo dev URL (host mapping): `http://localhost:<HUGO_DEV_PORT>/`
- The Hugo dev server runs as the `hugo` service in this Compose stack.

Run the Hugo dev server service:
```bash
docker compose up -d hugo
```

Run Hugo production build from OpenClaw container:
```bash
docker compose exec openclaw sh -c 'cd /site && hugo --minify --gc'
```

Quick connectivity check from OpenClaw to Hugo dev server:
```bash
docker compose exec openclaw sh -c 'curl -sI http://hugo:1313 | head -n 1'
```

---

## Customizing Your Agent

### Identity

Edit `openclaw/workspace/IDENTITY.md` to define your agent's name, personality, and avatar.

### Skills

Skills are Markdown playbooks that tell the agent how to handle specific tasks.
They live in `openclaw/workspace/skills/<skill-name>/SKILL.md`.

A minimal skill:

```markdown
---
name: my-skill
description: >-
  Describe when the agent should use this skill (used for trigger matching).
---

# My Skill

## Steps
1. Do this first
2. Then do this

## Triggers
Phrases that activate this skill: "run my skill", "do the thing".
```

See `openclaw/workspace/skills/example-skill/SKILL.md` for a working example.

### Models

Edit `openclaw/openclaw.json` to configure model providers, add Ollama models, or change the default model.

---

## Useful Commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart openclaw only
docker compose restart openclaw

# View logs
docker compose logs -f openclaw

# Get dashboard URL
docker compose logs openclaw | grep "http://"
```

## Services

- `ironclaw-proxy` (Nginx reverse proxy for web UI + logs) on `${OPENCLAW_PORT:-18790}`
- `ironclaw` (OpenClaw gateway backend, internal port 18789)
- `mcp-tls` (TLS terminator for internal MCP gateway, internal port 8443)
- `hugo` dev server on `${HUGO_DEV_PORT:-1313}`
- `openclaw-sandbox-browser` (headless Chrome, internal)

---

## GPU / Local Model Runner

See `docker-compose.gpu.yml` and `AGENTS.md` for instructions on enabling GPU-accelerated local models.

