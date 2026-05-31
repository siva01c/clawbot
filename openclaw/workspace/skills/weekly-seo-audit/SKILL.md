---
name: weekly-seo-audit
description: >-
  Run a full SEO audit on a client website. Crawl the site, analyse the report,
  identify issues and opportunities, then generate an actionable improvement plan.
  Triggers: "weekly SEO", "SEO audit", "audit ludekkvapil.cz", "run SEO",
  "check SEO", "crawl site", "SEO report", "Monday audit".
---

# Weekly SEO Audit Skill

Runs the full SEO audit loop: crawl → analyse → cross-reference knowledge base →
produce prioritised action plan. Default dogfood target: `ludekkvapil.cz`.

## Available Tools

- **`seobot__crawl`** — Start a crawl job. Returns `job_id`.
- **`seobot__get_report`** — Poll for results. Returns page list, issues, metadata.
- **`seobot__list_reports`** — Check previous audit dates for comparison.
- **`ragchat__*`** — Read/update knowledge base with fresh content from the crawl.

## Playbook

### Step 1 — Confirm the target

If no URL is given, default to `https://ludekkvapil.cz`.
Ask only if the context is ambiguous (e.g. multiple clients active).

### Step 2 — Check for a recent report

Call `seobot__list_reports` — if a report for this domain exists from the last 7 days,
ask the user whether to re-crawl or use the existing data.

### Step 3 — Start the crawl

Call `seobot__crawl` with:
```json
{ "url": "<target_url>", "incremental": false, "headless": true }
```
Note the returned `job_id`. Inform the user: "Crawl started — this takes a few minutes."

### Step 4 — Wait and poll

Call `seobot__get_report` with the `job_id` every ~30s until status is `complete`.
Show progress updates if the user is watching.

### Step 5 — Analyse the report

From the finished report, extract and categorise issues:

**Critical (fix this week):**
- Missing `<title>` or `<meta description>` on indexed pages
- 4xx/5xx response codes on linked pages
- Pages blocked by robots.txt that should be indexed
- Duplicate title tags across pages

**High priority:**
- Title tags over 60 chars or under 30 chars
- Missing H1 or multiple H1s on a page
- Images missing alt text
- Pages with no internal links pointing to them (orphan pages)

**Opportunities:**
- Pages with thin content (under 300 words) that could be expanded
- New pages since the last crawl (feed into Step 6)
- Pages with high potential but weak titles

### Step 6 — Feed new content into the knowledge base

For each new or significantly changed page since the last crawl:
Call `ragchat__*` (content import / node update tool) to ensure the knowledge base
reflects the current site. If ragchat lacks a direct import tool, note URLs for
manual review.

### Step 7 — Generate the action plan

Produce a structured report:

```
## SEO Audit — <domain> — <date>

### Summary
- Pages crawled: N
- New pages since last audit: N
- Critical issues: N
- High-priority issues: N

### Critical Issues
1. [page URL] — [issue] — [fix]

### High-Priority Issues
1. [page URL] — [issue] — [recommendation]

### Opportunities
1. [page URL] — [observation] — [action]

### Next Steps
- [ ] Fix critical issues by [date]
- [ ] Review thin content pages
- [ ] Schedule follow-up crawl in 7 days
```

### Step 8 — Store the summary

Save the audit summary to memory so it can be referenced in future sessions and
compared week-over-week.

## Tips

- Incremental crawls (`"incremental": true`) are faster but may miss removed pages —
  use full crawls for weekly audits.
- Compare this week's critical issue count against last week's to show progress.
- For `ludekkvapil.cz` specifically: the site is a Hugo static site — common issues
  are missing meta descriptions on blog posts and orphan tag pages.
