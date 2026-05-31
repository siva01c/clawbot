---
name: support-escalation-review
description: >-
  Review unanswered or escalated customer support questions, research them
  using OSINT and SEO data, then generate FAQ entries to close the knowledge gap.
  Triggers: "escalation review", "unanswered questions", "support gaps",
  "knowledge gap", "FAQ generation", "what questions can't we answer",
  "support review", "improve support".
---

# Support Escalation Review Skill

Finds recurring questions the support bot couldn't answer, researches each gap
using the specialist tools, and generates ready-to-import FAQ entries so the same
question never goes unanswered twice.

## Available Tools

- **`ragchat__*`** — Query escalation data, import new FAQ nodes, search existing KB.
- **`osintbot__query_intel`** — Research topics not covered by internal KB.
- **`seobot__crawl`** / **`seobot__get_report`** — Crawl relevant site sections for existing content.
- **`sales__search_knowledge`** — Check if the sales KB already covers the gap.

## Playbook

### Step 1 — Pull escalation data

Call `ragchat__*` (general query tool or escalation-specific tool if available) with:
```
"What questions were escalated or unanswered in the last 24 hours?"
"List recurring topics where the support bot had low confidence"
```

If no escalation API is available yet, ask the user to paste recent unanswered questions.

### Step 2 — Identify knowledge gaps

Group the escalated questions by topic:
- **Product questions** — pricing, availability, features not in the KB
- **Process questions** — returns, delivery, account management
- **Competitor questions** — "how do you compare to X?"
- **Technical questions** — integrations, APIs, advanced use cases

### Step 3 — Research each gap

For each distinct knowledge gap:

**Option A — Internal search first:**
Call `sales__search_knowledge` with the topic.
If a good result returns → the answer exists, just not surfaced to support. Flag for routing fix.

**Option B — OSINT research:**
Call `osintbot__query_intel` with:
```
"What do customers typically ask about [topic]?"
"What is the industry-standard answer for [question type]?"
```

**Option C — Site crawl:**
If the answer might exist on the client's website but isn't indexed:
Call `seobot__crawl` on the relevant URL section, then `seobot__get_report`.
Extract the relevant content.

### Step 4 — Draft FAQ entries

For each gap, write a FAQ entry:

```
## FAQ: [Question]

**Category:** [Product / Process / Competitor / Technical]
**Answer:**
[Clear, concise answer — 2–4 sentences. Source: [tool/URL used]]

**Tags:** [relevant keywords for RAG matching]
```

### Step 5 — Import to knowledge base

For each drafted FAQ:
Call `ragchat__*` (node create tool) to import the FAQ as a new knowledge node.

Confirm each import succeeded (note the returned node ID).

### Step 6 — Summary report

```
## Escalation Review — <date>

- Escalations reviewed: N
- Knowledge gaps found: N
- FAQ entries created: N
- Gaps still open (need human input): N

### Still open
- [question] — needs [product team / pricing info / etc.]
```

### Step 7 — Follow-up

Store open gaps in memory. Revisit next session.
If the same gap appears 3 sessions in a row → escalate to the user directly.

## Tips

- One new FAQ per session is progress — don't wait until you have a dozen.
- Short, specific FAQ answers outperform long explanations in RAG retrieval.
- Tag each FAQ entry with the date created so freshness can be tracked.
