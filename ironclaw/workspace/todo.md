# Agentic Ops & lkv.cz — Master Project TODO List

This document acts as the consolidated tracking system for the **Agentic Ops** roadmap, microsite ideas, and business planning decisions. It highlights what is **Done** (implemented in code) and what **Has to be Done** (configuration, runtime setup, and GTM steps).

---

## 📊 High-Level Status Dashboard

| Phase | Component / Goal | Status | Key Code References |
|---|---|---|---|
| **Phase 0** | Nginx Reverse Proxy & Network | ⚠️ **Partial** (Stopped) | [ops-proxy/docker-compose.yml](file:///home/siva01/projects/lkv/ops-proxy/docker-compose.yml) |
| **Phase 1** | Specialist MCP Servers (ragchat, seo, osint, sales) |  **Done** | [mcp-server.ts](file:///home/siva01/projects/lkv/seo-tools/src/mcp-server.ts), [osintbot_mcp.py](file:///home/siva01/projects/lkv/osintbot/scripts/osintbot_mcp.py), [mcp.py](file:///home/siva01/projects/lkv/sales-assistant/src/assistant/api/routes/mcp.py) |
| **Phase 2** | MCP Gateway Aggregator |  **Done** | [main.py](file:///home/siva01/projects/lkv/mcpserver/gateway/main.py) |
| **Phase 3** | OpenClaw Integration | ⚠️ **Partial** | [openclaw/.mcp.json](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/.mcp.json) |
| **Phase 4** | Playbook Skills Definition |  **Done** | [weekly-seo-audit](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/skills/weekly-seo-audit/SKILL.md), [competitor-monitoring](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/skills/competitor-monitoring/SKILL.md) |
| **Phase 5** | Agent Identity & Guidelines |  **Done** | [IDENTITY.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/IDENTITY.md), [SOUL.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/SOUL.md) |
| **Phase 6** | Observability & Alerting | ⚠️ **Partial** | [gateway/main.py](file:///home/siva01/projects/lkv/mcpserver/gateway/main.py), [ops-proxy/conf.d](file:///home/siva01/projects/lkv/ops-proxy/conf.d) |
| **Phase 7** | Marketing Dogfood & Microsites | 📅 **Todo** | Shared Hugo design |
| **Phase 8** | GTM Business Plan & Monetization | 📅 **Todo** | Payments, auth, cost optimization |

---

## 🛠️ Detailed Task Checklist

### PHASE 0 — nginx-proxy: shared reverse-proxy and network
> **Goal:** Run the central gateway routing all traffic to the containerized backends.

- [ ] **0.1 — Start nginx-proxy (ops-proxy)**
  - [ ] Confirm the external network exists; create it if not:
    ```bash
    docker network inspect agentic-ops >/dev/null 2>&1 || docker network create -d bridge agentic-ops
    ```
  - [ ] Copy env template and configure in `ops-proxy`:
    ```bash
    cd ops-proxy && cp .env.dist .env
    # Set VIRTUAL_HOST and DEFAULT_EMAIL in .env
    ```
  - [ ] Start the proxy stack: `docker compose up -d`
  - [ ] Verify: `docker ps` shows `ops-proxy` and `ops-acme` containers running.
- [x] **0.2 — Register each service as a virtual host**
  - [x] Map `ragchat` to `ragchat.local` (Port 8080) -> [ragchat/docker-compose.yml](file:///home/siva01/projects/lkv/ragchat/docker-compose.yml)
  - [x] Map `sales-assistant` to `dev.ludekkvapil.cz` (Port 8000) -> [sales-assistant/docker-compose.yml](file:///home/siva01/projects/lkv/sales-assistant/docker-compose.yml)
  - [x] Map `mcpserver` static site to `mcpserver.local` (Port 80) -> [mcpserver/docker-compose.yml](file:///home/siva01/projects/lkv/mcpserver/docker-compose.yml)
  - [x] Map `mcpserver-gateway` to `mcp-gateway.local` (Port 8100) -> [mcpserver/docker-compose.yml](file:///home/siva01/projects/lkv/mcpserver/docker-compose.yml)
  - [ ] Map `seo-tools` MCP to `seo.local` (Port 3001) -> **Todo:** Add `VIRTUAL_HOST` variables to [seo-tools/docker-compose.yml](file:///home/siva01/projects/lkv/seo-tools/docker-compose.yml)
  - [ ] Map `osintbot` MCP (`osintbot-mcp`, Port 8200) — internal only, reached via mcpserver gateway; no public VIRTUAL_HOST needed -> [osintbot/docker-compose.yml](file:///home/siva01/projects/lkv/osintbot/docker-compose.yml)
  - [ ] Map `clawbot` OpenClaw dashboard to `clawbot.local` (Port 18789) -> **Todo:** Add `VIRTUAL_HOST` variables to [clawbot/docker-compose.yml](file:///home/siva01/projects/lkv/clawbot/docker-compose.yml)
- [ ] **0.3 — Local /etc/hosts entries (dev environment)**
  - [ ] Add domain mapping in host `/etc/hosts`:
    ```
    127.0.0.1  ragchat.local dev.ludekkvapil.cz mcpserver.local mcp-gateway.local seo.local osint.local clawbot.local
    ```
- [ ] **0.4 — Shared secrets file**
  - [ ] Create `.env.shared` at workspace root with all MCP tokens (e.g. `RAGCHAT_MCP_TOKEN`, `SEO_MCP_TOKEN`, `OSINT_MCP_TOKEN`, `SALES_MCP_TOKEN`, `MCP_GATEWAY_TOKEN`).
  - [ ] Reference `.env.shared` from each project's docker-compose file via `env_file`.

---

### PHASE 1 — Expose each specialist as an MCP server
> **Goal:** Expose JSON-RPC 2.0 endpoints for all specialty applications to communicate with the orchestrator.

- [x] **1.1 — ragchat: register existing MCP endpoint**
  - Exposes route `/mcp/post` via custom Drupal module `mcp_tools` requiring token authentication.
- [x] **1.2 — seo-tools: add MCP HTTP wrapper**
  - Implemented in [mcp-server.ts](file:///home/siva01/projects/lkv/seo-tools/src/mcp-server.ts). Exposes `crawl`, `get_report`, and `list_reports`.
- [x] **1.3 — OSINT: add MCP HTTP endpoint**
  - Implemented in [osintbot_mcp.py](file:///home/siva01/projects/lkv/osintbot/scripts/osintbot_mcp.py) (fastmcp tools), exposed over HTTP via `osintbot_mcp_http.py` shim. Exposes `osintbot_investigate`, `osintbot_plan`, `osintbot_wiki_lookup`, `osintbot_status`, etc.
- [x] **1.4 — sales-assistant: expose chat and product tools**
  - Implemented in [mcp.py](file:///home/siva01/projects/lkv/sales-assistant/src/assistant/api/routes/mcp.py). Exposes `chat`, `search_knowledge`, and `get_status`.

---

### PHASE 2 — MCPserver as unified MCP gateway
> **Goal:** Aggregate all four specialist MCP servers under a single namespaced gateway.

- [x] **2.1 — Build FastAPI aggregator service**
  - Implemented in [main.py](file:///home/siva01/projects/lkv/mcpserver/gateway/main.py). It merges tool manifests and namespaces tools as `{server}__{tool}` (e.g., `seobot__crawl`, `ragchat__ProductSearch`).
- [x] **2.2 — Rate limiting and proxy buffering**
  - Configured in [vmweb-limits.conf](file:///home/siva01/projects/lkv/ops-proxy/conf.d/vmweb-limits.conf) to support large JSON-RPC packages.
- [ ] **2.3 — Test gateway aggregation**
  - Run `curl -H "Authorization: Bearer $MCP_GATEWAY_TOKEN" http://mcp-gateway.local/mcp/post` with `tools/list` request and confirm namespaced tools are fetched and merged correctly.

---

### PHASE 3 — Wire OpenClaw (clawbot) to all specialists
> **Goal:** Configure ClawBot to utilize the unified gateway or connect to all backends.

- [ ] **3.1 — Update ClawBot MCP configurations**
  - Edit [openclaw/.mcp.json](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/.mcp.json) to reference the aggregated gateway URL `http://mcp-gateway.local/mcp/post` (or point directly to all 4 backends).
- [ ] **3.2 — Restart OpenClaw & verify tools**
  - Restart the service: `docker compose restart openclaw`
  - Verify that the namespaced tools appear on the OpenClaw dashboard.
- [ ] **3.3 — Update tools documentation**
  - Update [TOOLS.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/TOOLS.md) with details on namespaced tools.

---

### PHASE 4 — Define agent workflows / playbooks
> **Goal:** Implement agent execution instructions (skills) in markdown files.

- [x] **4.1 — Implement `weekly-seo-audit` playbook**
  - Created at [weekly-seo-audit/SKILL.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/skills/weekly-seo-audit/SKILL.md).
- [x] **4.2 — Implement `competitor-monitoring` playbook**
  - Created at [competitor-monitoring/SKILL.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/skills/competitor-monitoring/SKILL.md).
- [x] **4.3 — Implement `support-escalation-review` playbook**
  - Created at [support-escalation-review/SKILL.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/skills/support-escalation-review/SKILL.md).
- [x] **4.4 — Implement `new-client-onboarding` playbook**
  - Created at [new-client-onboarding/SKILL.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/skills/new-client-onboarding/SKILL.md).

---

### PHASE 5 — Identity, persona, and memory
> **Goal:** Setup agent profile, values, system memory, and heartbeat checklist.

- [x] **5.1 — Configure Identity & Persona**
  - Configured at [IDENTITY.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/IDENTITY.md) (Name: ClawBot, Role: Agentic Ops Manager).
- [x] **5.2 — Configure Soul & Boundaries**
  - Configured at [SOUL.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/SOUL.md).
- [x] **5.3 — Configure User memory & Bootstrap sequences**
  - Configured at [USER.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/USER.md) and [HEARTBEAT.md](file:///home/siva01/projects/lkv/clawbot/openclaw/workspace/HEARTBEAT.md).

---

### PHASE 6 — Monitoring and observability
> **Goal:** Instrument request logging and alerting across the agentic services.

- [x] **6.1 — Structured logging**
  - Gateway [main.py](file:///home/siva01/projects/lkv/mcpserver/gateway/main.py) writes JSON logs indicating tool, duration, and response codes.
- [ ] **6.2 — Dashboard and Centralized Log Storage**
  - Store request metrics under `mcpserver/logs/` and configure log routing.
- [ ] **6.3 — Setup crawl fail alerts**
  - Set up warning notifications if a crawl job fails repeatedly.

---

### PHASE 7 — Marketing dogfood loop & microsites
> **Goal:** Configure ClawBot to audit the local site and deploy client-facing microsites.

- [ ] **7.1 — Weekly audit against `ludekkvapil.cz`**
  - Trigger weekly cron skill to audit the owner's Hugo static website.
- [ ] **7.2 — Build Microsites using Hugo (Shared Theme / Unified Design)**
  - [ ] **Microsite `seo.ludekkvapil.cz`**: Form/interface for generating SEO reports leveraging `seo-tools`.
  - [ ] **Microsite `courses.ludekkvapil.cz`**: Course registry, inspired by [naucmese.cz/ludek-kvapil](https://www.naucmese.cz/ludek-kvapil).
  - [ ] **Microsite `osint.ludekkvapil.cz`**: OSINT intelligence interface leveraging `osintbot`.
- [ ] **7.3 — Competitor Feed draft posts**
  - Run daily OSINT checks on competitor moves and write draft recommendations into `ludekkvapil/content/` for human review.

---

### PHASE 8 — First paying client (GTM Business Plan)
> **Goal:** Turn the unified agent crew into a commercial SaaS offer.

- [ ] **8.1 — Domain & SSL Configuration**
  - Setup DNS record and nginx configuration to resolve `seo.ludekkvapil.cz` to the frontend dashboard.
- [ ] **8.2 — Authentication & Authorization**
  - Secure the client portal and API endpoints with user authentication.
- [ ] **8.3 — Pricing & Tier Structure**
  - Define product pricing: **Per report** vs **Subscription-based**.
  - Configure credit allotment, trial limits, and packages (e.g. Free trial limit, monthly subscription quota).
- [ ] **8.4 — Cost Analysis and Optimization**
  - [ ] Calculate cost per report (single vs multiple languages, site crawl depth/page size).
  - [ ] Optimize LLM token usage: determine optimal model fit (e.g., GPT-4o vs Claude 3.5 Sonnet vs open source models like Llama 3 running locally on Ollama).
- [ ] **8.5 — Payment Integration**
  - Connect client signups to Stripe / billing gateway.
