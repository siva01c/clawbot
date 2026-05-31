---
name: seo-crawler
description: >-
  Crawl a website for SEO analysis, generate an SEO report, or list existing
  crawl reports. Triggers: "crawl", "SEO audit", "check my site", "SEO report",
  "analyse website", "analyse URL".
---

# SEO Crawler Skill

Use the `seobot` MCP server to audit websites for technical SEO issues.

## Available Tools

- **`crawl`** — Start a new crawl job for a domain. Returns a `jobId`.
- **`get_report`** — Fetch the finished report for a domain (after crawl completes).
- **`list_reports`** — List all domains that have been crawled.

## Playbook

### Step 1 — Identify the target

Ask the user for the URL / domain if not already provided.
Normalise to bare domain: `example.com` (no `https://`, no trailing slash).

### Step 2 — Start the crawl

Call `seobot.crawl` with `{ "domain": "<domain>" }`.
Report back the `jobId` and tell the user the crawl is running in the background (usually 1–5 min for small sites).

### Step 3 — Retrieve the report

When the user asks for results (or after an appropriate wait), call `seobot.get_report` with `{ "domain": "<domain>" }`.

### Step 4 — Summarise findings

Parse the JSON report and surface:
1. **Critical issues** — missing title/meta, broken links, missing H1, redirect chains
2. **Warnings** — duplicate titles, slow pages, images without alt text
3. **Quick wins** — low-effort fixes with high impact

Present findings as a prioritised action list. Offer to explain any item in detail.

## Tips

- If the crawl is still in progress `get_report` returns `{"status":"running"}` — tell the user to ask again in a minute.
- Use `list_reports` to show the user which domains have cached reports before starting a fresh crawl.
