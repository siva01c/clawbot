# clawbot — IronClaw Agent Gateway

A ready-to-use Docker template for running an [IronClaw](https://github.com/nearai/ironclaw) agent gateway that reaches its tools through an internal MCP gateway.

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

# 3. Build the images (compiles IronClaw — the first build takes a while)
docker compose build

# 4. Start all services
docker compose up -d

# 5. Check it started
docker compose logs -f ironclaw
```

Open `http://localhost:<OPENCLAW_PORT>/` and sign in with `OPENCLAW_GATEWAY_TOKEN`.

---

## Environment Variables

Always create `.env` from the template: `cp .env.default .env`, then fill in real values.

All variables are defined in `.env.default`. Copy it to `.env` and fill in real values.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes* | — | OpenAI API key |
| `OPENCLAW_GATEWAY_TOKEN` | Yes | — | Secret token for gateway auth |
| `OPENCLAW_PORT` | No | `18790` | Host port for the gateway (via Nginx proxy) |
| `TARGET_ENV` | No | `dev` | Build stage (`dev` or `production`) |
| `AGENT_TOKEN_CLAWBOT` | Yes | — | ClawBot's own token for the MCP gateway (agent id `clawbot`); the same value must be registered with the gateway |
| `CLAWBOT_MCP_GATEWAY_URL` | No | `https://mcp-gateway.clawbot.internal:8443/mcp/post` | Internal HTTPS URL for MCP gateway |

*\* Not required if using a local model runner (configure `DMR_BASE_URL` instead)*

---

## Dashboard

The gateway dashboard is available at:
```
http://localhost:<OPENCLAW_PORT>/
```

The web UI token is `OPENCLAW_GATEWAY_TOKEN` from `.env`.

IronClaw runtime state, including session history, is stored in the named Docker volume `ironclaw-runtime` mounted at `/root/.ironclaw/reborn`. Use `docker compose restart ironclaw` for normal restarts. Avoid `docker compose down -v` if you want to keep session history.

---

## IronClaw Build

The image is built from upstream [nearai/ironclaw](https://github.com/nearai/ironclaw), pinned to one commit (`IRONCLAW_REF` in `docker/ironclaw/Dockerfile`), with the local changes in `patches/ironclaw/` applied on top:

- `0001-internal-mcp-gateway.patch` — the internal MCP gateway extension (`CLAWBOT_MCP_GATEWAY_URL` + `MCP_GATEWAY_TOKEN`); a tool description that fails the model-safety check is replaced with a neutral one instead of failing every turn,
- `0002-skip-redundant-model-override.patch` — no per-request model override when it names the configured model (`openai/gpt-5` = `gpt-5`).

To move to a newer IronClaw, bump `IRONCLAW_REF` and rebuild. If a patch no longer applies, rebase it on the new commit and regenerate it with `git diff`.

The proxy image (`target: proxy`) serves the web UI's `js/pages/logs/` directory from the IronClaw source, because the binary's embedded SPA does not include it.

The stack joins the external Docker network `agentic-ops`, where the MCP gateway runs. Create it (`docker network create agentic-ops`) if you run ClawBot without one.

---

## Extra Skills

`ironclaw/workspace/skills/` holds only the skills that belong to this repo. To give ClawBot more, mount them read-only from a local, gitignored `docker-compose.override.yml`:

```yaml
services:
  ironclaw:
    volumes:
      - /path/to/skills/my-skill:/root/.ironclaw/reborn/workspace/skills/my-skill:ro
```

---

## Customizing Your Agent

### Identity

Edit `ironclaw/workspace/IDENTITY.md` to define your agent's name, personality, and avatar.

### Skills

Skills are Markdown playbooks that tell the agent how to handle specific tasks.
They live in `ironclaw/workspace/skills/<skill-name>/SKILL.md`.

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

See `ironclaw/workspace/skills/example-skill/SKILL.md` for a working example.

### Models

Edit `ironclaw/config.toml` to configure model providers or change the default model.

---

## Useful Commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Restart ironclaw only
docker compose restart ironclaw

# View logs
docker compose logs -f ironclaw

# Get dashboard URL
docker compose logs ironclaw | grep "http://"
```

## Services

- `ironclaw-proxy` (Nginx reverse proxy for web UI + logs page) on `${OPENCLAW_PORT:-18790}`
- `ironclaw` (IronClaw gateway backend, internal port 18789)
- `mcp-tls` (TLS terminator for internal MCP gateway, internal port 8443)
- `openclaw-sandbox-browser` (headless Chrome, internal)

---

## GPU / Local Model Runner

See `docker-compose.gpu.yml` and `AGENTS.md` for instructions on enabling GPU-accelerated local models.

