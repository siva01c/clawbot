---
name: example-skill
description: >-
  A starter template showing how to structure a custom skill. Replace this
  with your own skill's triggers and instructions.
---

# Example Skill

This is a minimal example of a custom OpenClaw skill. Skills are Markdown files
with YAML frontmatter that tell the agent when and how to use a specific playbook.

## How to create your own skill

1. Create a new folder under `openclaw/workspace/skills/your-skill-name/`
2. Add a `SKILL.md` file with:
   - `name`: a unique identifier (matches the folder name)
   - `description`: when the agent should load this skill (used for matching triggers)
3. Write the playbook below the frontmatter

## Example steps

1. Greet the user
   - Say hello and introduce yourself
2. Ask what they need
   - Listen for the user's request
3. Complete the task
   - Follow the instructions in this playbook

## Triggers

Use phrases like "run example skill", "show me an example", or "demo skill" to
activate this skill.
