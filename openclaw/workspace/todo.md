[Sun 2026-05-31 08:06 UTC] Protoject todo.md

# Agentic Ops — Step-by-Step Roadmap to Fully Agentic Company

> Goal: wire every project into a single OpenClaw-orchestrated agent crew that autonomously handles marketing, support, and market intel for e-commerce clients.

---

## PHASE 0 — nginx-proxy: shared reverse-proxy and network (~half a day)

> The `nginx-proxy/` project is the existing shared gateway. It runs `nginxproxy/nginx-proxy:1.6-alpine` + `acme-companion` for automatic TLS and creates the external Docker network `nginx-proxy` that every other project already references. This must be running before anything else.

### 0.1 — Start nginx-proxy (if not already running)

- [ ] Confirm the external network exists; create it if not:
 ```bash
 docker network inspect nginx-proxy >/dev/null 2>&1 || docker network create -d bridge nginx-proxy
 ```
- [ ] Copy env template and configure:
 ```bash
 cd nginx-proxy
 cp .env.dist .env
 # Set VIRTUAL_HOST and DEFAULT_EMAIL in .env
 ```
- [ ] Copy default templates:
 ```bash
 cp -r nginx-proxy/templates/* nginx-proxy/default-data/
 ```
- [ ] Start the proxy stack:
 ```bash
 docker compose up -d
 ```
- [ ] Verify: `docker ps` should show `nginx-proxy` and `nginx-acme` containers running

### 0.2 — Register each service as a virtual host

Each project gets a `VIRTUAL_HOST` entry so nginx-proxy auto-generates its upstream config. Add or confirm these environment variables in each project's `docker-compose.yml`:

| Project | `VIRTUAL_HOST` | `VIRTUAL_PORT` |
|---|---|---|
| ragchat | `ragchat.local` | `80` |
| seo-crawler | `seo.local` | `3000` |
| OSINT | `osint.local` | `7860` |
| sales-assistant | `sales.local` | `8000` |
| mcpserver | `mcpserver.local` | `80` |
| clawbot | `clawbot.local` | `18789` |

- [ ] Add `VIRTUAL_HOST`, `VIRTUAL_PORT`, `VIRTUAL_PROTO=http`, `VIRTUAL_NETWORK=nginx-proxy` env vars to any project that is missing them
- [ ] Ensure every project's `docker-compose.yml` includes:
 ```yaml
 networks:
 nginx-proxy:
 external: true
 ```
 (ragchat, ragbot, mcpserver, OSINT already have this — check seo-crawler, sales-assistant, clawbot)

### 0.3 — Local /etc/hosts entries (dev only)

- [ ] Add to `/etc/hosts`:
 ```
 127.0.0.1 ragchat.local seo.local osint.local sales.local mcpserver.local clawbot.local
 ```

### 0.4 — Shared secrets file

- [ ] Create `.env.shared` at workspace root with all MCP tokens (generated in Phase 1):
 ```bash
 # placeholder — fill in during Phase 1
 RAGCHAT_MCP_TOKEN=
 SEO_MCP_TOKEN=
 OSINT_MCP_TOKEN=
 SALES_MCP_TOKEN=
 MCP_GATEWAY_TOKEN=
 ```
- [ ] Reference `.env.shared` from each project's compose file via `env_file`

---

## PHASE 1 — Expose each specialist as an MCP server (~3–5 days)

### 1.1 ragchat — register existing MCP endpoint

- [ ] Verify `ragchat/drupal/modules/custom/ragchat/ragchat.routing.yml` exposes `/api/mcp` (already implemented per sprint 4)
- [ ] Confirm the route requires token auth (not `_access: 'TRUE'`)
- [ ] Generate an MCP gateway token and store it in `.env.shared` as `RAGCHAT_MCP_TOKEN`
- [ ] Test: `curl -H "Authorization: Bearer $RAGCHAT_MCP_TOKEN" http://ragchat.local:8080/api/mcp/tools`

### 1.2 seo-crawler — add MCP HTTP wrapper

- [ ] Create `seo-crawler/src/mcp-server.ts` — an Express endpoint that exposes:
 - `crawl(url, options)` → triggers a crawl job, returns job ID
 - `get_report(job_id)` → returns crawl results JSON
 - `compare_sitemap(url)` → runs incremental comparison, returns diff
- [ ] Add MCP server as a new service in `seo-crawler/docker-compose.yml` (port 3000)
- [ ] Add bearer token middleware (read from env `SEO_MCP_TOKEN`)
- [ ] Write a Jest test for each tool endpoint
- [ ] Store `SEO_MCP_TOKEN` in `.env.shared`

### 1.3 OSINT — add MCP HTTP endpoint

- [ ] Add `FastAPI` routes to `OSINT/linkedin_tool.py` (or a new `osint_mcp.py`):
 - `POST /mcp/tools/scrape_competitor` → runs `scrape` for given LinkedIn handle
 - `POST /mcp/tools/query_intel` → runs RAG query against `posts.json` / chromadb
 - `GET /mcp/tools` → returns tool manifest (MCP discovery)
- [ ] Add bearer token auth middleware (env `OSINT_MCP_TOKEN`)
- [ ] Expose port 7860 in `OSINT/docker-compose.yml`
- [ ] Store `OSINT_MCP_TOKEN` in `.env.shared`
- [ ] Test with `curl -X POST http://localhost:7861/mcp/tools/query_intel -d '{"question":"top competitor products"}'`

### 1.4 sales-assistant — expose chat and product tools

- [ ] Add `/mcp/tools` GET endpoint to `sales-assistant/src/assistant/api_server.py` returning tool manifest
- [ ] Add `POST /mcp/tools/chat` → wraps existing chat handler
- [ ] Add `POST /mcp/tools/get_products` → queries chromadb for products/services
- [ ] Add bearer token middleware (env `SALES_MCP_TOKEN`)
- [ ] Add tests in `tests/test_mcp.py`
- [ ] Store `SALES_MCP_TOKEN` in `.env.shared`

---

## PHASE 2 — MCPserver as unified MCP gateway (~2 days)

> nginx-proxy already handles routing and TLS. MCPserver sits behind it as `mcpserver.local` and acts as the MCP aggregator — it does NOT duplicate nginx-proxy's reverse-proxy role.

- [ ] Add `VIRTUAL_HOST=mcpserver.local` to `mcpserver/docker-compose.yml` (already present — verify it's correct)
- [ ] Build a lightweight aggregator service (Node.js or Python) inside the `mcpserver/` stack:
 - `GET /mcp/tools` → fetches tool manifests from all four backends and merges them
 - `POST /mcp/tools/{tool_name}` → routes the call to the correct backend based on tool prefix
 - Validates `MCP_GATEWAY_TOKEN` on every request before forwarding
 - Forwards individual service tokens from `.env.shared`
- [ ] Add `mcpserver/nginx.conf` (vhost config, not a full proxy) with upstream blocks pointing to internal service hostnames on the `nginx-proxy` network
- [ ] Add rate limiting in `nginx-proxy/conf.d/custom-limits.conf` (already exists — add MCP-specific limits)
- [ ] Add structured request logging to `mcpserver/logs/`
- [ ] Test: `curl -H "Authorization: Bearer $MCP_GATEWAY_TOKEN" http://mcpserver.local/mcp/tools` returns merged tool list from all services

---

## PHASE 3 — Wire OpenClaw (clawbot) to all specialists (~1–2 days)

- [ ] Populate `clawbot/openclaw/workspace/.mcp.json` — point at mcpserver.local (the single gateway behind nginx-proxy):
 ```json
 {
 "servers": {
 "ragchat": { "url": "http://mcpserver.local/ragchat/api/mcp", "token": "${RAGCHAT_MCP_TOKEN}" },
 "seo": { "url": "http://mcpserver.local/seo/mcp", "token": "${SEO_MCP_TOKEN}" },
 "osint": { "url": "http://mcpserver.local/osint/mcp", "token": "${OSINT_MCP_TOKEN}" },
 "sales": { "url": "http://mcpserver.local/sales/mcp", "token": "${SALES_MCP_TOKEN}" }
 }
 }
 ```
- [ ] Restart openclaw: `docker compose restart openclaw`
- [ ] Confirm all 4 servers appear in the OpenClaw dashboard tool list
- [ ] Update `clawbot/openclaw/workspace/TOOLS.md` documenting every available tool

---

## PHASE 4 — Define agent workflows / playbooks (~2–3 days)

Create one skill file per workflow in `clawbot/openclaw/workspace/skills/`:

### 4.1 `skills/weekly-seo-audit.md`
- [ ] Trigger: every Monday 09:00
- [ ] Steps:
 1. Call `seo.crawl(client_url)` — start incremental crawl
 2. Call `seo.compare_sitemap(client_url)` — find new/changed pages
 3. Call `ragchat.update_knowledge_base(pages)` — import new content
 4. Generate summary report → send to `sales.chat()` for delivery to client

### 4.2 `skills/competitor-monitoring.md`
- [ ] Trigger: daily or on-demand
- [ ] Steps:
 1. Call `osint.scrape_competitor(linkedin_handle)` — collect fresh posts
 2. Call `osint.query_intel("new products last 7 days")` — extract intel
 3. Call `ragchat.update_knowledge_base(intel)` — feed into support KB
 4. Summarize findings → store in agent memory

### 4.3 `skills/support-escalation-review.md`
- [ ] Trigger: daily, or when ragchat escalation count > threshold
- [ ] Steps:
 1. Call `ragchat.get_escalation_topics(last_24h)` — find recurring unanswered questions
 2. Call `osint.query_intel(topic)` — research each topic
 3. Call `seo.crawl(client_url, path=relevant_category)` — find existing content
 4. Generate FAQ entries → call `ragchat.create_knowledge_nodes(faqs)`

### 4.4 `skills/new-client-onboarding.md`
- [ ] Trigger: manual (new contract signed)
- [ ] Steps:
 1. Call `seo.crawl(client_url, full)` — full site audit
 2. Call `osint.scrape_competitor(top_3_competitors)` — build intel baseline
 3. Call `ragchat.create_shop(client_config)` — provision new shop instance
 4. Import crawl results into ragchat KB
 5. Confirm all agents are operational → notify via `sales.chat()`

---

## PHASE 5 — Identity, persona, and memory (~1 day)

- [ ] Edit `clawbot/openclaw/workspace/IDENTITY.md`: set agent name, role ("Agentic Ops Manager"), avatar
- [ ] Edit `clawbot/openclaw/workspace/SOUL.md`: define operating principles — data privacy, no hallucination, always cite source tool
- [ ] Edit `clawbot/openclaw/workspace/USER.md`: add client profiles (one per managed e-shop)
- [ ] Edit `clawbot/openclaw/workspace/BOOTSTRAP.md`: define startup sequence (check all MCP servers healthy, log status)
- [ ] Define `HEARTBEAT.md`: ping all 4 MCP servers every 5 min; alert if any is down

---

## PHASE 6 — Monitoring and observability (~1–2 days)

- [ ] Add structured logging to each MCP wrapper (JSON lines, include `tool`, `duration_ms`, `client_id`)
- [ ] Route all logs to `mcpserver/logs/` via Docker log driver or volume mount (nginx-proxy already writes access logs to `nginx-proxy/logs/` — correlate by `X-Request-ID`)
- [ ] Create a simple log dashboard (can be a static HTML + `tail -f` via SSE, or add Grafana if needed)
- [ ] Set up alerting: if `seo-crawler` fails 3 consecutive crawls, OpenClaw sends notification
- [ ] Track key metrics from the lean canvas:
 - `% support tickets auto-resolved` — query ragchat escalation table daily
 - `organic traffic lift` — compare seo-crawler reports week-over-week
 - `MRR` — query sales-assistant subscription data

---

## PHASE 7 — Marketing dogfood loop (~ongoing)

- [ ] Configure OpenClaw to run `weekly-seo-audit` skill against `ludekkvapil/` (Hugo site)
- [ ] Use seo-crawler to identify thin content on `ludekkvapil/` → auto-generate content suggestions
- [ ] Use OSINT to monitor competitors offering Drupal/AI services in CEE
- [ ] Feed findings into `ludekkvapil/content/` as draft posts (reviewed before publish)
- [ ] This is the proof-of-concept case study for the first paying client pitch

---

## PHASE 8 — First paying client (GTM)

- [ ] Package the stack as a "Starter" tier: ragchat + seo-crawler + weekly cadence
- [ ] Write onboarding script using `skills/new-client-onboarding.md`
- [ ] Set up billing via ragchat's existing Stripe integration
- [ ] Define SLA: uptime, response time, escalation handling
- [ ] Document self-hosted deployment guide (client runs on their infra or you host)

---

## Deferred / Separate track

- [ ] **Startup Factory** — build only after Phases 1–4 prove the agent loop works end-to-end; position it as the "deploy a new Agentic Ops instance for a client" platform
- [ ] **GPU / vLLM** (`docker-compose.gpu.yml`) — enable for high-volume clients only after token cost analysis confirms it's cheaper than OpenAI API at that scale

---

## Definition of "Fully Agentic"

The system is fully agentic when:
1. A new e-shop can be onboarded by running one OpenClaw skill (no manual steps)
2. Weekly SEO, daily OSINT, and real-time support all run without human intervention
3. OpenClaw detects a gap (unanswered question → missing KB entry) and fills it autonomously
4. Luděk's only manual action is reviewing and approving agent-generated content before publish
