---
name: competitor-monitoring
description: >-
  Research competitors using OSINT intelligence. Find recent posts, product announcements,
  hiring signals, and market moves. Feed findings into the knowledge base.
  Triggers: "competitor", "monitor competitors", "what is [company] doing",
  "market intel", "competitive analysis", "OSINT", "LinkedIn research",
  "what are competitors up to".
---

# Competitor Monitoring Skill

Pulls fresh intelligence from the OSINT knowledge base, synthesises it into
competitive signals, and feeds actionable findings into the ragchat KB so sales
and support always have up-to-date market context.

## Available Tools

- **`osintbot__get_status`** — Check how many posts are indexed and last update time.
- **`osintbot__list_posts`** — Browse raw LinkedIn posts in the knowledge base.
- **`osintbot__query_intel`** — Natural-language RAG query over the LinkedIn corpus.
- **`ragchat__*`** — Update knowledge base with competitive context.
- **`sales__search_knowledge`** — Verify if competitive intel is already in the sales KB.

## Playbook

### Step 1 — Establish scope

Ask (if not clear): which competitor(s) or topics to investigate?
Default scope for dogfood: CEE/Czech agencies offering Drupal, AI chatbots, or SEO services.

### Step 2 — Check data freshness

Call `osintbot__get_status` — note `post_count` and last update.
If data is stale (> 7 days) or count is low, warn the user and suggest running a fresh scrape.

### Step 3 — Browse recent activity

Call `osintbot__list_posts` to see what's in the corpus.
Skim for recent dates and relevant company/person names.

### Step 4 — Run targeted intelligence queries

Run these queries via `osintbot__query_intel` (adjust for actual targets):

```
"What products or services has [competitor] announced recently?"
"Is [competitor] hiring? What roles?"
"What are [competitor]'s customers saying about them?"
"What AI or automation tools is [competitor] promoting?"
"What pricing signals exist for [competitor]?"
```

Run one focused query per angle — the RAG model performs better with specific questions.

### Step 5 — Synthesise findings

Produce an intelligence brief:

```
## Competitor Intel Brief — <date>

### [Competitor Name]
- **Recent moves:** [product launches, partnerships, pricing changes]
- **Hiring signals:** [roles being advertised → growth areas]
- **Customer sentiment:** [positive/negative themes from posts]
- **Threat level:** Low / Medium / High
- **Opportunity:** [gap we can exploit or message to counter]

### Market trends
- [Recurring themes across all competitors]
```

### Step 6 — Update knowledge bases

If significant new intel is found:
1. Call `ragchat__*` to store competitive context as a knowledge node tagged `competitor-intel`.
2. Call `sales__search_knowledge` with competitor name — if nothing returns, the sales KB is blind
   to this competitor; note it for a manual knowledge import.

### Step 7 — Recommend actions

Based on findings, suggest concrete next steps:
- Content angles to counter competitor messaging (feed to `weekly-seo-audit`)
- Sales objections to prepare for (feed to `sales-assistant` KB)
- Outreach targets (companies recently frustrated with competitor)

## Tips

- Queries about specific people or companies return sharper results than broad market questions.
- `list_posts` is useful for spotting patterns the RAG might summarise away.
- Competitive intel has a short shelf life — flag anything older than 30 days as stale.
- Respect privacy: only surface publicly available LinkedIn information.
