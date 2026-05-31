---
name: new-client-onboarding
description: >-
  Onboard a new e-commerce client onto the Agentic Ops platform. Provisions all
  four specialist agents with client-specific data. Run when a new contract is signed.
  Triggers: "new client", "onboard", "new shop", "set up client", "new contract",
  "provision client", "add client".
---

# New Client Onboarding Skill

The complete onboarding sequence for a new e-commerce client. When done, all four
specialist agents are loaded with client data and ready to operate autonomously.

Estimated time: 30–60 minutes (mostly crawl time).

## Checklist overview

1. Collect client profile
2. Full site audit (seobot)
3. Competitor OSINT baseline (osintbot)
4. Knowledge base provisioned (ragchat)
5. Product catalogue imported (sales)
6. All agents confirmed operational
7. First weekly audit scheduled

---

## Available Tools

- **`seobot__crawl`** / **`seobot__get_report`** — Full site crawl for SEO baseline.
- **`osintbot__query_intel`** / **`osintbot__list_posts`** — Competitor intelligence baseline.
- **`ragchat__*`** — Provision shop, import site content as knowledge nodes.
- **`sales__search_knowledge`** / **`sales__chat`** — Verify product KB loaded correctly.

---

## Playbook

### Step 1 — Collect client profile

Ask the user for:
- **Shop name** and **primary URL** (e.g. `https://myshop.cz`)
- **E-commerce platform** (Shopify / WooCommerce / Drupal Commerce / other)
- **Product categories** (1–3 main categories)
- **Top 3 competitors** (company names or LinkedIn handles if known)
- **Primary language** (cs / en / other)
- **Support contact email** (for escalation notifications)

Store answers in memory under `clients/<shop-name>/profile.md`.

### Step 2 — Full site crawl

Call `seobot__crawl` with:
```json
{ "url": "<client_url>", "incremental": false, "headless": true }
```

While crawling, proceed with Steps 3 and 4 in parallel.

### Step 3 — OSINT competitor baseline

For each of the top 3 competitors:
Call `osintbot__query_intel` with:
```
"What does [competitor] sell and who are their customers?"
"What are [competitor]'s main marketing messages?"
"What weaknesses or complaints are mentioned about [competitor]?"
```

Compile into a competitor profile stored in memory under `clients/<shop-name>/competitors.md`.

### Step 4 — Provision ragchat shop

Call `ragchat__*` (shop creation / node bundle creation tool) with the client config:
- Shop name, primary domain, language
- Support email
- Product categories as taxonomy terms

Note the returned shop ID — store in `clients/<shop-name>/profile.md`.

### Step 5 — Import site content into knowledge base

Once the seobot crawl completes (call `seobot__get_report` to poll):

For each page in the crawl report:
- Extract: URL, title, content summary, last modified date
- Call `ragchat__*` (node create tool) to import as a knowledge node tagged with
  the client's shop ID.

Priority order for import:
1. Product pages
2. Category pages
3. FAQ / help pages
4. About / contact pages
5. Blog posts (if any)

### Step 6 — Import product catalogue to sales KB

If the client has a product catalogue (Shopify/Woo feed URL or CSV):
Call `sales__chat` with:
```
"Please confirm you have the product catalogue for [shop name] loaded."
```

If not loaded: note this as an action item — Phase 4 (Shopify/Woo API connector) will automate this.
For now, ask the user to export a product CSV and note the manual import path.

### Step 7 — Verify all agents operational

Run a sanity check on each specialist:

```
seobot__list_reports          → should show the new domain
osintbot__get_status          → confirm data loaded
ragchat__*                    → search for the shop name → confirm nodes exist
sales__search_knowledge       → query a product name → confirm results return
```

Report any failures to the user with remediation steps.

### Step 8 — Onboarding complete

Deliver a handoff summary:

```
## Onboarding Complete — <shop name> — <date>

### What's live
- ✅ SEO baseline crawl: N pages indexed
- ✅ Competitor intel: [competitor 1], [competitor 2], [competitor 3] profiled
- ✅ Knowledge base: N content nodes imported (shop ID: <id>)
- ✅ Sales KB: [loaded / pending Phase 4 product sync]

### First automated runs scheduled
- Weekly SEO audit: next Monday 09:00
- Daily competitor monitoring: starts tomorrow

### Action items for Luděk
- [ ] Review imported knowledge nodes for accuracy
- [ ] Confirm product catalogue import path (Phase 4)
- [ ] Set support email routing to ragchat endpoint
```

## Tips

- Steps 2, 3, and 4 can run in parallel — start the crawl first since it's the slowest.
- If the client's site blocks crawlers (robots.txt), note it and advise them to whitelist the crawler IP.
- Save the onboarding summary to `workspace/clients/<shop-name>/onboarding-<date>.md` for reference.
