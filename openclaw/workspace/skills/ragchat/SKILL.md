---
name: ragchat
description: >-
  Query the RAG knowledge base, manage Drupal CMS content, or use any of the
  21 registered tools in the ragchat server. Triggers: "knowledge base", "CMS",
  "Drupal", "content", "ragchat", "RAG", "documents".
---

# RagChat Skill

Use the `ragchat` MCP server — the primary knowledge and CMS integration layer with 21 tools.

## Key Tool Categories

### Knowledge / RAG
- Search and retrieve documents from the Drupal-backed knowledge base
- Answer questions grounded in indexed content

### Drupal CMS
- Create, read, update, delete nodes and taxonomy terms
- Manage media, menus, and site configuration

### Utility
- Translation, summarisation, and content generation tools

## Playbook

### Step 1 — Identify intent

Map the user request to a tool category:
- Content questions → RAG search tools
- CMS operations → Drupal CRUD tools
- General tasks → utility tools

### Step 2 — Discover available tools (if unsure)

Call `ragchat` `tools/list` (built-in MCP introspection) to see all 21 tools and their descriptions.

### Step 3 — Execute

Call the appropriate tool with the minimal required parameters.
Always confirm destructive CMS operations (delete, bulk update) with the user before executing.

### Step 4 — Present results

- For search: summarise relevant excerpts with source references
- For CMS ops: confirm what was created/updated/deleted, include node ID or URL
- For utility: relay the output directly

## Tips

- RagChat is the default server for anything content or knowledge related.
- When in doubt between ragchat and sales, use ragchat for general knowledge and sales for product-specific queries.
