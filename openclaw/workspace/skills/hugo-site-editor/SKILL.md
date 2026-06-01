---
name: hugo-site-editor
description: >-
  Edit, improve, or fix the ludekkvapil.cz Hugo website. Read and write content
  files, fix SEO front matter, add meta descriptions, improve page copy, create
  new content, fix broken front matter, rebuild the site.
  Triggers: "edit website", "fix site", "improve page", "add description",
  "update content", "write new page", "fix SEO on site", "rebuild site",
  "add meta", "update about page", "new blog post", "fix front matter",
  "improve copy", "translate page", "add keywords".
---

# Hugo Site Editor Skill

Direct read-write access to the `ludekkvapil.cz` Hugo source at `/site`.
When running inside OpenClaw, use the Hugo dev service at `http://hugo:1313` for live preview and content checks.
When using the host browser, use `http://localhost:1313` (or the mapped `HUGO_DEV_PORT`).
After any edit, rebuild with `hugo --minify --gc` to publish changes.

## Site Structure

```
/site/
├── config.toml          ← site config, i18n, theme, baseURL
├── content/             ← all pages (YAML front matter + Markdown body)
│   ├── _index.md        ← EN home page
│   ├── about.md         ← About page
│   ├── interests.md
│   ├── services.md
│   ├── services/        ← individual service pages
│   │   ├── genai-chatbots.md
│   │   ├── drupal-hugo-development.md
│   │   ├── web-automation.md
│   │   ├── api-integrations.md
│   │   ├── devops.md
│   │   ├── testing.md
│   │   └── data-analysis.md
│   ├── projects/        ← project case studies
│   ├── notices/         ← technical notes/blog
│   └── cs/              ← Czech translations (mirror of EN structure)
├── data/                ← JSON data files (skills, experience, etc.)
├── static/              ← static assets (images, files)
├── layouts/             ← template overrides
├── themes/hugo-resume/  ← active theme
└── public/              ← BUILD OUTPUT (do not edit directly)
```

**Two languages:** EN (default, no prefix) and CS (`/cs/` prefix).
Front matter is YAML (delimited by `---`).

## Front Matter Reference

All standard SEO fields for this site:

```yaml
---
title: "Page Title"           # <title> tag — keep 50–60 chars
draft: false                  # true = excluded from build
weight: 1                     # ordering within section (lower = first)
description: "..."            # <meta name="description"> — 120–160 chars
                              # NOTE: this site uses 'meta_description' in
                              # some templates — check and use the right one
summary: "..."                # teaser text shown in listings
keywords: ["kw1", "kw2"]      # <meta name="keywords">
lastmod: 2026-05-30           # last modified date (ISO 8601)
sitemap:
  priority: 0.8               # 0.0–1.0 (home = 1.0, sections = 0.8, pages = 0.6)
  changefreq: monthly         # always|hourly|daily|weekly|monthly|yearly|never
type: "services"              # content type (must match template folder)
icon: "robot"                 # theme-specific icon name
---
```

**Site-specific fields observed:**
- `seo_title` — used in `<title>` by the theme (separate from `title`)
- `meta_description` — used in `<meta description>` by the theme
- Both `summary` and `meta_description` are used — always populate both

## Available Tools

- **`site-files__read_file`** — Read any file in `/site`
- **`site-files__write_file`** — Write (overwrite) a file at `/site/...`
- **`site-files__list_directory`** — List directory contents
- **`site-files__create_directory`** — Create a new directory

> Hugo binary is available inside the container at `/usr/bin/hugo`.
> Build command (run inside container or note for manual execution):
> `cd /site && hugo --minify --gc`
> Preferred command from the `clawbot/` directory:
> `docker compose exec openclaw sh -c 'cd /site && hugo --minify --gc'`

## Playbooks

---

### Fix SEO Front Matter

Use after a `weekly-seo-audit` report to systematically fix SEO issues.

**Step 1 — Load the audit report**
Review the list of pages with issues from the SEO audit skill.

**Step 2 — For each affected page:**

```
site-files__read_file("/site/content/<path>.md")
```

Parse the YAML front matter block (between `---` delimiters).

**Step 3 — Apply fixes based on issue type:**

| Issue | Fix |
|---|---|
| Missing `meta_description` | Add `meta_description: "..."` (120–160 chars, includes primary keyword) |
| Missing `description` | Add `description: "..."` same content as meta_description |
| `seo_title` missing | Add `seo_title: "..."` (50–60 chars, keyword-first format) |
| `title` too long | Shorten `title` to ≤60 chars, move detail to `description` |
| Missing `keywords` | Add `keywords: ["keyword1", "keyword2"]` (3–5 terms) |
| Missing `lastmod` | Add `lastmod: <today's date>` |
| Missing `sitemap` priority | Add `sitemap:\n  priority: 0.6` for regular pages |

**Step 4 — Write the fixed file:**

```
site-files__write_file("/site/content/<path>.md", "<full file content>")
```

Always write the **complete** file — front matter + body. Never write front matter only.

**Step 5 — After all fixes, rebuild:**

Note: `hugo --minify --gc` must be run from `/site` inside the container.
Inform the user to run: `docker compose exec openclaw sh -c 'cd /site && hugo --minify --gc'`
For live preview, ensure Hugo dev service is running and use `http://hugo:1313` from OpenClaw.

---

### Improve Page Copy

**Step 1 — Read the page:**
```
site-files__read_file("/site/content/<path>.md")
```

**Step 2 — Analyse:**
- Is the content scannable? (headers, bullets, short paragraphs)
- Does it answer the visitor's likely intent?
- Is there a clear CTA (call to action)?
- Is the English/Czech appropriate and professional?
- Word count — under 300 words on a service page is thin

**Step 3 — Rewrite the body section** (below the `---` closing delimiter).
Preserve all front matter exactly. Only edit the Markdown body.

**Step 4 — For Czech pages** under `cs/`, match the same improvements.

---

### Create a New Content Page

**Step 1 — Determine the content type:**

| Content | Path pattern | `type` field |
|---|---|---|
| Service | `content/services/<slug>.md` | `services` |
| Project | `content/projects/<slug>.md` | — |
| Notice/Blog | `content/notices/<category>/README.md` | — |

**Step 2 — Create the file:**

Use this front matter template (YAML):
```yaml
---
title: "<Page Title>"
draft: false
weight: 99
seo_title: "<Keyword-first title, 50-60 chars>"
meta_description: "<Compelling description with primary keyword, 120-160 chars>"
description: "<Same as meta_description>"
summary: "<One-sentence teaser for listing pages>"
keywords: ["keyword1", "keyword2", "keyword3"]
lastmod: <today ISO date>
type: "<content type>"
sitemap:
  priority: 0.6
  changefreq: monthly
---

<Markdown body>
```

**Step 3 — Create Czech translation** at `content/cs/<same-path>` with the same
front matter structure but Czech text. Use `translationKey` to link them:
```yaml
translationKey: "<shared-key>"
```

**Step 4 — Rebuild.**

---

### Translate EN Page to Czech

**Step 1 — Read the EN source:**
```
site-files__read_file("/site/content/<path>.md")
```

**Step 2 — Determine the CS path:**
- EN: `content/services/devops.md` → CS: `content/cs/services/devops.md`
- Check if CS version exists: `site-files__list_directory("/site/content/cs/")`

**Step 3 — Translate:**
- Front matter: translate `title`, `seo_title`, `meta_description`, `description`, `summary` to Czech
- Body: translate all Markdown body text to professional Czech
- Preserve all field names (they stay in English)
- Add `translationKey: "<slug>"` to both files to link them

**Step 4 — Write the CS file and rebuild.**

---

### Audit Front Matter Coverage

Quick sweep across all content pages to find SEO gaps.

**Step 1 — List all content files:**
```
site-files__list_directory("/site/content/")
site-files__list_directory("/site/content/services/")
site-files__list_directory("/site/content/projects/")
```

**Step 2 — For each .md file, read and check for:**
- `meta_description` present and 120–160 chars
- `seo_title` present and 50–60 chars
- `keywords` array has ≥ 3 items
- `lastmod` is set
- Body has ≥ 300 words (for service/project pages)

**Step 3 — Produce a gap report:**
```
## Front Matter Coverage — <date>

| Page | meta_description | seo_title | keywords | lastmod | Word count |
|------|-----------------|-----------|----------|---------|------------|
| services/genai-chatbots.md | ✅ | ✅ | ❌ | ❌ | 450 |
| about.md | ❌ | ❌ | ❌ | ❌ | 120 |
...
```

Fix all ❌ items using the "Fix SEO Front Matter" playbook.

---

## Build & Deploy Notes

- **Build output**: `/site/public/` — this is what gets served
- **Theme**: `hugo-resume` at `/site/themes/hugo-resume/`
- **No hot-reload**: changes require a rebuild to be visible at `ludekkvapil.cz`
- **Draft pages**: `draft: true` pages are excluded from production build
- **i18n**: EN pages live at root, CS pages at `/cs/` — both built from same `hugo` command
- **Sitemap**: auto-generated at `/site/public/sitemap.xml` after build

## Tips

- Always read a file before writing it — never write blind.
- Preserve the exact delimiter style (`---` YAML) — this site uses YAML, not TOML (`+++`).
- When writing files, include the complete content including unchanged body — `write_file` overwrites the whole file.
- If `hugo` build fails (e.g. due to a template error), the error will appear in the build output — read it carefully.
- The `notices/` section uses `README.md` filenames instead of content slugs — this is intentional.
- For images: static files live in `/site/static/` and are referenced as `/files/image.jpg` (no `/static/` prefix).
