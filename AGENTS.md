# AGENTS.md — Developer Guide for clawbot

Instructions for AI agents and developers working on this repository.

---

## Repository Structure

```
clawbot/
├── docker/ironclaw/
│   ├── Dockerfile          # Multi-stage image (dev/production)
│   └── start.sh            # Container entrypoint — updates config, starts ironclaw serve
├── ironclaw/
│   ├── config.toml         # IronClaw gateway config (models, auth, webui)
│   └── workspace/          # Mounted into the container as the agent's working directory
│       ├── .mcp.json       # MCP server connections (Drupal, Apify, etc.)
│       ├── IDENTITY.md     # Agent name, persona, avatar
│       ├── SOUL.md         # Agent values and behavioural guidelines
│       ├── TOOLS.md        # Available tools and how to use them
│       ├── USER.md         # Info about the user (fill in as needed)
│       └── skills/         # Custom skill playbooks (SKILL.md per skill)
├── docker-compose.yml      # Main Compose file
├── docker-compose.gpu.yml  # GPU / vLLM variant
├── .env.default            # Template for .env — commit this, never commit .env
└── .env                    # Local secrets — gitignored
```

---

## Common Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Rebuild image (after changing Dockerfile or start.sh)
docker compose build ironclaw && docker compose up -d

# Restart ironclaw only (picks up workspace/ changes without rebuild)
docker compose restart ironclaw

# View logs
docker compose logs -f ironclaw
```

---

## Key Rules

- **Never edit `.env`** — it contains real secrets and is gitignored. Edit `.env.default` for template values.
- **`ironclaw/config.toml`** uses env var interpolation where appropriate — always use env vars, never hardcode secrets.
- **`ironclaw/workspace/`** is volume-mounted read-write — changes there take effect on `docker compose restart ironclaw` (no rebuild needed).
- **`docker/ironclaw/Dockerfile` and `start.sh`** require a full `docker compose build` to take effect.

---

## Making Changes

| What you changed | How to apply |
|---|---|
| `ironclaw/workspace/**` (skills, identity, config) | `docker compose restart ironclaw` |
| `ironclaw/config.toml` | `docker compose restart ironclaw` |
| `docker/ironclaw/start.sh` | `docker compose build ironclaw && docker compose up -d` |
| `docker/ironclaw/Dockerfile` | `docker compose build ironclaw && docker compose up -d` |
| `docker-compose.yml` | `docker compose up -d` |

---

## Testing Model Connectivity

```bash
# Test Docker Model Runner (local)
docker compose exec ironclaw sh -c 'curl -s --max-time 30 http://host.docker.internal:12434/api/tags | grep name'

# Test chat completion
curl -s http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"ai/gpt-oss-vllm","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```
