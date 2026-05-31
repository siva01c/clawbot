---
name: osint-intel
description: >-
  Research a person or company using LinkedIn data and the OSINT knowledge base.
  Triggers: "research", "find info on", "LinkedIn", "OSINT", "who is", "prospect
  research", "background check", "company intel".
---

# OSINT Intelligence Skill

Use the `osintbot` MCP server to research people and companies using scraped LinkedIn data.

## Available Tools

- **`query_intel`** — Ask a natural-language question; returns a RAG-grounded answer from the LinkedIn corpus.
- **`list_posts`** — List all scraped LinkedIn posts in the knowledge base.
- **`get_status`** — Check how many posts are indexed and whether the service is healthy.

## Playbook

### Step 1 — Clarify the target

Ask (if not already clear): who or what is the research target? Name, company, role?

### Step 2 — Check knowledge base status

Call `osintbot.get_status` to confirm data is loaded. If `post_count` is 0, warn the user the knowledge base may be empty.

### Step 3 — Run the query

Call `osintbot.query_intel` with a specific, focused question:
- `"What is [Name]'s professional background?"`
- `"What companies has [Name] worked at?"`
- `"What topics does [Name] post about on LinkedIn?"`

### Step 4 — Synthesise the answer

Present findings as a brief intelligence summary:
- **Background** — role, seniority, sector
- **Key themes** — recurring topics in their posts
- **Signals** — any notable recent activity, hiring, funding mentions

### Step 5 — Offer follow-up

Ask if the user wants deeper research on any specific angle.

## Tips

- Be precise in queries — the RAG system performs better with specific questions than vague ones.
- Use `list_posts` if the user wants to browse raw data rather than a synthesised answer.
- Respect privacy: only surface information that was publicly available.
