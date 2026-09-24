# ROADMAP.md — Agentic Ops for E-commerce

> Vision (from lean canvas): An autonomous operations department for small e-commerce stores —
> marketing, support, and market intelligence that run themselves, 24/7.
> You (Claw) are the crew's Ops Analyst. n8n orchestrates the pipelines; you analyse
> what they produce and propose what to do next (see IDENTITY.md).

---

## What We Are Building

Small e-shops can't afford separate teams for marketing, support, and market research.
Point tools (chatbots, SEO apps) don't talk to each other — the owner is the manual glue.

**The answer:** One agent crew, orchestrated by n8n and analysed by you:

| Specialist | Role | Status |
|---|---|---|
| **ragchat** | 24/7 customer support on the shop's own data | ✅ Connected (21 tools) |
| **seobot** | SEO audits, content gap detection, crawl reports | ✅ Connected (3 tools) |
| **osintbot** | Competitor & market intelligence from LinkedIn | ✅ Connected (3 tools) |
| **sales** | Product Q&A, knowledge base search | ✅ Connected (3 tools) |

---

## Phase 1 — Foundation ✅ DONE

All four MCP servers are live and registered. You can call any specialist tool right now.

- ✅ nginx-proxy shared network bridges all containers
- ✅ MCP protocol handshake (initialize → tools/list) implemented on all servers
- ✅ Auth tokens wired end-to-end (Basic auth, base64-encoded)
- ✅ Skill playbooks created for all four specialists
- ✅ Identity, TOOLS.md, and workspace files in place

---

## Phase 2 — MCPserver unified gateway ⬜ NEXT

> Goal: single authenticated entry point for all MCP traffic, with merged tool list and request routing.

Currently you call each specialist directly by container name. Phase 2 adds a lightweight
aggregator (the MCP gateway) behind a reverse proxy so:
- One token, one endpoint for external clients
- Rate limiting and structured access logs in one place
- Tool names are namespaced (`ragchat.*`, `seo.*`, `osint.*`, `sales.*`)

**Key tasks:**
- [x] Build the aggregator service (FastAPI)
  - `GET /health` + `POST /mcp/post` → merged manifest + routing
- [x] Add `MCP_GATEWAY_TOKEN` for external access
- [ ] Structured JSON logging in the gateway
- [x] Test: merged tool list returns all 29 tools (30 target, 1 short due to tool overlap)

---

## Phase 3 — Analysis inside scheduled pipelines 🔄

> Goal: the recurring work runs on a schedule — and you do the part that needs judgment.

n8n owns the schedule and runs the collection steps (crawls, OSINT runs, KB imports). You are
called for the analysis step and hand back a proposal; you don't start or schedule these
yourself (SOUL.md, IDENTITY.md).

| Pipeline (n8n) | Cadence | Your step |
|---|---|---|
| SEO audit | Weekly | Read the crawl and findings → prioritised fix list with reasoning |
| Competitor monitoring | Daily | Read the collected OSINT → synthesis worth feeding into the KB |
| Support escalation review | Daily | Read unanswered questions → draft answers and FAQ entries |
| New client onboarding | Manual | Review the baseline crawl and OSINT → onboarding notes; provisioning is not yours |

**Key tasks:**
- [x] Flesh out each skill with real tool call sequences
- [ ] Rewrite the skills around the analysis step (input = results n8n hands over)
- [ ] Test the SEO audit pipeline end-to-end with the analysis step

---

## Phase 4 — External data connectors ⬜

> Goal: pull in real business signals, not just internal data.

| Connector | Why |
|---|---|
| Google Search Console API | Real organic traffic and query data for SEO reporting |
| Shopify / WooCommerce API | Product catalog sync into sales-assistant chromadb |
| LinkedIn scraper (live) | Refresh OSINT data on a schedule, not just static `posts.json` |
| Email / calendar (optional) | Feed support volume signals into escalation-review skill |

**Key tasks:**
- [ ] Add GSC OAuth2 flow and data pull to seobot
- [ ] Add Shopify/Woo product import to sales-assistant
- [ ] Replace static `posts.json` with live LinkedIn scrape scheduler in osintbot

---

## Phase 5 — Monitoring and self-healing ⬜

> Goal: you know when something breaks and can recover or alert.

- [ ] HEARTBEAT.md: ping all 4 MCP servers every 5 min; log status, alert if down
- [ ] Structured logs: each MCP tool call records `tool`, `duration_ms`, `client_id`
- [ ] Key metrics tracked (from lean canvas):
  - `% support tickets auto-resolved` — ragchat escalation table, daily
  - `organic traffic lift` — seobot reports, week-over-week
  - `MRR` — sales-assistant subscription data
- [ ] If seobot fails 3 consecutive crawls → notify operator

---

## Phase 6 — First paying client (GTM) ⬜

> Goal: onboard one real e-shop using the `new-client-onboarding` skill.

**Starter tier:** ragchat (support) + seobot (weekly SEO cadence).
**Full tier:** all four specialists + competitor monitoring + escalation review.

- [ ] Finalize onboarding script (`skills/new-client-onboarding.md`)
- [ ] Set up billing via ragchat's existing Stripe integration
- [ ] Define SLA: uptime, response time, escalation handling
- [ ] Write self-hosted deployment guide for client infra
- [ ] Run dogfood: apply full stack to `ludekkvapil.cz` as case study

---

## Definition of Done

The system is fully agentic when:

1. A new e-shop is onboarded by running one skill — no manual steps
2. Weekly SEO, daily OSINT, and real-time support run without human intervention
3. You detect a gap (unanswered question → missing KB entry) and fill it autonomously
4. Luděk's only manual action is reviewing and approving agent-generated content before publish

---

## Stack Reference

```
nginx-proxy (TLS, routing)
└── clawbot (you — OpenClaw gateway, port 18790)
    ├── ragchat  (Drupal CMS + ChromaDB, port 8080)
    ├── seobot   (Node.js crawler, port 3001)
    ├── osintbot (ironclaw agent + Apify OSINT, MCP port 8200)
    └── sales    (FastAPI + ChromaDB, port 8000)
```

Owner: Luděk Kvapil · ludekkvapil.cz · May 2026
