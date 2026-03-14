# OpenClaw Workspace

This directory is bind-mounted into the OpenClaw container at `/root/.openclaw/workspace`.
Changes here take effect after `docker compose restart openclaw` — no image rebuild needed.

---

## Files

| File | Purpose |
|---|---|
| `IDENTITY.md` | Agent name, persona, emoji, avatar |
| `SOUL.md` | Agent values and behavioural guidelines |
| `TOOLS.md` | Available tools and usage instructions |
| `BOOTSTRAP.md` | First-run instructions shown to the agent on startup |
| `HEARTBEAT.md` | Heartbeat / health-check configuration |
| `USER.md` | Information about the user the agent is working with |
| `.mcp.json` | Optional MCP server connections (add your own) |

---

## Skills

Custom skill playbooks live in `skills/<skill-name>/SKILL.md`.

Each skill has YAML frontmatter with a `name` and `description` (used for trigger matching),
followed by a Markdown playbook the agent follows when the skill is activated.

See `skills/example-skill/SKILL.md` for a minimal working example.

---

## Notes

- `.openclaw/` (workspace state) is generated at runtime — gitignored
- Secrets referenced in `.mcp.json` come from `.env` via environment variable substitution
