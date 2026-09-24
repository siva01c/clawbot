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
│       ├── TOOLS.md        # Available tools and how to use them — gitignored (real container
│       │                   #   names); copy from TOOLS.md.example
│       ├── USER.md         # Info about the user — gitignored (personal data); copy from
│       │                   #   USER.md.example
│       ├── skills/redmine-time-tracking/projects.md
│       │                   # Directory -> Redmine project map — gitignored; copy from .example
│       └── skills/         # Custom skill playbooks (SKILL.md per skill)
├── docker-compose.yml      # Main Compose file
├── docker-compose.gpu.yml  # GPU / vLLM variant
├── .env.default            # Template for .env — commit this, never commit .env
└── .env                    # Local secrets — gitignored
```

> **Upgrading a checkout from before `TOOLS.md` / `USER.md` were untracked:** `git pull`
> deletes both from `ironclaw/workspace/`, because they are no longer in the repo. Save them
> first and put them back after:
>
> ```bash
> cp ironclaw/workspace/TOOLS.md ironclaw/workspace/USER.md /tmp/
> git pull
> cp /tmp/TOOLS.md /tmp/USER.md ironclaw/workspace/
> ```
>
> Forgot? `git show <commit-before-pull>:ironclaw/workspace/TOOLS.md` still has them. If the
> container starts without them, `start.sh` seeds them from the `.example` templates and logs a
> warning — the agent keeps running, but on placeholders until you fill the files in. The same
> goes for the Redmine project map, `ironclaw/workspace/skills/redmine-time-tracking/projects.md`
> (never tracked; copy `projects.md.example` and fill in your projects).

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
- **Task discipline:** substantive work needs its own Redmine issue, **claimed before you start** (`agent_lock` / `agent_lock_expires` custom fields + status *In progress*) so a second agent doesn't take the same issue — see "Claim before work" in `ironclaw/workspace/skills/redmine-time-tracking/SKILL.md`. A live lock held by someone else is left alone.
- **Time tracking:** after substantive work on a project, log hours to Redmine following `ironclaw/workspace/skills/redmine-time-tracking/SKILL.md` (activity "AI Agent"; log against the issue you claimed). The always-on trigger and rules live in `ironclaw/workspace/SOUL.md` → "Track Your Work"; the directory → project map is in that skill, § "Resolve the Redmine project".

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
