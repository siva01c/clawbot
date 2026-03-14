# AGENTS.md — Developer Guide for clawbot

Instructions for AI agents and developers working on this repository.

---

## Repository Structure

```
clawbot/
├── docker/openclaw/
│   ├── Dockerfile          # Multi-stage image (dev/production)
│   └── start.sh            # Container entrypoint — updates openclaw, starts gateway, prints dashboard URL
├── openclaw/
│   ├── openclaw.json       # OpenClaw gateway config (models, plugins, browser, auth)
│   ├── extensions/         # Custom OpenClaw plugins (gitignored at runtime)
│   ├── identity/           # Device identity — generated at runtime, gitignored
│   └── workspace/          # Mounted into the container as the agent's working directory
│       ├── .mcp.json       # MCP server connections (Drupal, Apify, etc.)
│       ├── IDENTITY.md     # Agent name, persona, avatar
│       ├── SOUL.md         # Agent values and behavioural guidelines
│       ├── TOOLS.md        # Available tools and how to use them
│       ├── BOOTSTRAP.md    # First-run instructions for the agent
│       ├── HEARTBEAT.md    # Heartbeat / health-check config
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
docker compose build openclaw && docker compose up -d

# Restart openclaw only (picks up workspace/ changes without rebuild)
docker compose restart openclaw

# View logs
docker compose logs -f openclaw

# Get dashboard URL
docker compose logs openclaw | grep "http://"
```

---

## Key Rules

- **Never edit `.env`** — it contains real secrets and is gitignored. Edit `.env.default` for template values.
- **`openclaw/openclaw.json`** uses `${VAR}` substitution — always use env vars, never hardcode secrets.
- **`openclaw/workspace/`** is volume-mounted read-write — changes there take effect on `docker compose restart openclaw` (no rebuild needed).
- **`docker/openclaw/Dockerfile` and `start.sh`** require a full `docker compose build` to take effect.
- **`openclaw/identity/`** is generated at runtime — never commit it.

---

## Making Changes

| What you changed | How to apply |
|---|---|
| `openclaw/workspace/**` (skills, identity, config) | `docker compose restart openclaw` |
| `openclaw/openclaw.json` | `docker compose restart openclaw` |
| `docker/openclaw/start.sh` | `docker compose build openclaw && docker compose up -d` |
| `docker/openclaw/Dockerfile` | `docker compose build openclaw && docker compose up -d` |
| `docker-compose.yml` | `docker compose up -d` |

---

## Testing Model Connectivity

```bash
# Test Docker Model Runner (local)
docker compose exec openclaw sh -c 'curl -s --max-time 30 http://host.docker.internal:12434/api/tags | grep name'

# Test chat completion
curl -s http://localhost:12434/engines/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"ai/gpt-oss-vllm","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```
