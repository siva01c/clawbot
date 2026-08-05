# TOOLS.md - Ecosystem Map

## MCP Servers

| Server | Container | Port | Tools | Use For |
|---|---|---|---|---|
| **`gateway`** | mcpserver-gateway | 8100 | 29 | **Unified entry point — all tools via single auth** |
| **`site-files`** | clawbot-openclaw-1 (local) | — | ~10 | **Read/write Hugo source at `/site`** |
| `ragchat` | ragchat-nginx-1 | 8080 | 21 | CMS content, RAG knowledge base, Drupal |
| `seobot` | seo-tools-mcp | 3001 | 3 | Website SEO audits, crawl reports |
| `osintbot` | osintbot-mcp | 8200 | — | LinkedIn (Apify)/OSINT research, prospect intel |
| `sales` | sales-assistant-assistant-1 | 8000 | 3 | Product Q&A, knowledge base search |

### Gateway tool naming

Tools routed through the gateway use `{server}__{tool}` format, e.g.:
- `seobot__crawl`, `seobot__get_report`, `seobot__list_reports`
- `osintbot__osintbot_investigate`, `osintbot__osintbot_plan`, `osintbot__osintbot_wiki_lookup`, `osintbot__osintbot_status`
- `sales__chat`, `sales__get_status`, `sales__search_knowledge`
- `ragchat__*` (21 tools — use gateway for all Drupal/KB operations)

## Skills

### Server skills
- `ragchat` — CMS and RAG queries (default for content tasks)
- `seo-tools` — SEO audits and crawl reports
- `osint-intel` — Person/company OSINT from LinkedIn data
- `sales-assistant` — Product questions and knowledge base search

### Workflow skills (multi-tool playbooks)
- `weekly-seo-audit` — Full SEO crawl → analyse → KB update → action plan
- `competitor-monitoring` — OSINT intel gathering → synthesise → feed KBs
- `support-escalation-review` — Find unanswered Qs → research → generate FAQs
- `new-client-onboarding` — Provision all 4 agents for a new e-commerce client
- `hugo-site-editor` — Read/write ludekkvapil.cz Hugo source, fix SEO front matter, create pages, rebuild site

## Docker Network

All containers on `nginx-proxy` bridge network.
OpenClaw container: `clawbot-openclaw-1`.
Reach services by container name over the network.

## Key URLs

- OpenClaw dashboard: http://127.0.0.1:18790
- **MCP Gateway: http://mcpserver-gateway:8100** (internal) / http://127.0.0.1:8100 (host)
- RagChat: http://ragchat-nginx-1:8080
- Sales assistant: http://sales-assistant-assistant-1:8000
- SEO crawler MCP: http://seo-tools-mcp:3001
- OSINT MCP: http://osintbot-mcp:8200
