---
name: sales-assistant
description: >-
  Answer product questions, search the knowledge base, or handle customer
  support queries using the sales assistant AI. Triggers: "product", "pricing",
  "availability", "what do you sell", "sales", "customer question", "recommend",
  "knowledge base", "search products".
---

# Sales Assistant Skill

Use the `sales` MCP server to answer product-related questions grounded in the vector knowledge base.

## Available Tools

- **`chat`** — Send a message to the sales AI. Returns a grounded, knowledge-base-backed answer.
- **`search_knowledge`** — Semantic search over the product knowledge base. Returns matching documents.
- **`get_status`** — Check knowledge base size and service health.

## Playbook

### Step 1 — Understand the query type

Decide which tool fits best:
- **Conversational / product Q&A** → use `chat`
- **Targeted lookup** (e.g. "find all products under €50") → use `search_knowledge`
- **Health / data freshness check** → use `get_status`

### Step 2a — Chat (conversational)

Call `sales.chat` with `{ "message": "<user question>", "session_id": "<uuid>" }`.

Use a consistent `session_id` across turns in the same conversation to maintain context.
Relay the response verbatim — it's already grounded and formatted.

### Step 2b — Search (structured lookup)

Call `sales.search_knowledge` with `{ "query": "<search terms>", "top_k": 5 }`.

Present results as a ranked list with document titles and relevant excerpts.

### Step 3 — Handle follow-ups

Keep the same `session_id` for the whole conversation thread so the sales AI remembers context.

## Tips

- For ambiguous queries try `search_knowledge` first to show options, then `chat` to explain a specific item.
- The knowledge base is the source of truth — do not invent product details.
- Use `get_status` if the user reports outdated or missing information.
