---
name: redmine-time-tracking
description: >-
  Claim a Redmine issue before substantial work so a second agent doesn't take it,
  and log the time an agent spends on a project to the self-hosted Redmine (CRM).
  Resolve the working directory to a Redmine project, find or create an issue for
  the task, then file a time entry under the "AI Agent" activity. Run automatically
  after ~15+ minutes of substantive work on a project, or when asked to "log my
  time" / "track this work" / "record hours in Redmine".
---

# Redmine Time Tracking

Log agent work time to Redmine. Data model: **Project → Issue → Time entry**.

> **ClawBot copy.** Other agents in the crew follow their own copy of this playbook; the
> operator keeps them in step. This one is deliberately narrow: you reach Redmine only through
> the gateway's `redmine__*` tools, and everything site-specific — which directories belong to
> which Redmine project — lives in `projects.md` next to this file, not here.

## Environment

- **Tools:** `redmine__<tool>` through the MCP gateway.
- **Work session:** the `WORK SESSION` line you appended to `MEMORY.md` (format in `SOUL.md`):
  `WORK SESSION | ws-<id> | <project> | issue #<n> | started <UTC> | last <UTC> | <task> | open`.
  `ws-<id>` names your session in the lock, `issue` is the claimed issue, `started`/`last`
  bound the time you actually worked.
- **Clock:** `date -u +%Y-%m-%dT%H:%M:%SZ`; if you have no shell, estimate conservatively
  from the conversation.

## When to run

- **Automatically**, after roughly 15 minutes or more of real effort on one project
  (research, coding, audits, multi-step tasks). This is internal bookkeeping on Luděk's
  own infrastructure — you do **not** need to ask permission first.
- On explicit request ("log my time", "track this").
- On an end-of-day flush: process every open work session that hasn't been logged. The
  flush logs `last − started` for each line, **never** `now − started` — a session opened in
  the morning and left alone is not a day of work.

Skip trivial work (a one-line fix, a quick question) — it's not worth an issue.

## Claim before work

Time tracking runs *after* the work. The issue itself has to exist and be **claimed before
you start**, or another agent — Luděk's Claude Code on the host, or a later worker — can pick
up the same issue and you both do it twice. Same bar as above: a change to a repository or
roughly 15+ minutes of effort needs a claim; a question or a quick look doesn't.

The claim lives on the issue, in custom fields. `assigned_to` can't tell one agent from
another, so the lock carries your session instead.

1. Resolve the project and find or create the issue (steps 1 and 4 below).
2. Read the lock: `get_redmine_issue(issue_id, include_custom_fields=true)`.
   - `agent_lock` empty → claim it.
   - your own claim — `clawbot/<ws-id>` matching a `WORK SESSION` line in `MEMORY.md` → carry
     on, extend the expiry.
   - **someone else's, `agent_lock_expires` in the future → leave it alone.** Pick other work
     and say which issue you skipped.
   - someone else's, expired → you may take it, but write a note saying who held it and why
     you took over.
3. Claim in one write, then read the issue back to confirm it landed:

   ```
   update_redmine_issue(issue_id, fields={
     "agent_lock": "clawbot/<the ws-… id on your WORK SESSION line>",
     "agent_lock_expires": "<now + 2h, e.g. 2026-09-23T07:27:19Z>",
     "status_name": "In progress",
     "assigned_to_id": <your id>,
   })
   ```

   Redmine gives `agent_lock_expires` back without the trailing `Z`; it still means UTC.

4. Replace `issue -` on your `WORK SESSION` line with `issue #<id>`, so after a restart you
   find the issue again, recognise the lock as yours, and log the time against it.
5. Extend the expiry if the work outlives it. When you finish, clear `agent_lock` and
   `agent_lock_expires` along with the status change in step 6. If you hand the work over
   unfinished, leave the lock to expire on its own and write the handoff note.

## Procedure

### 1. Resolve the Redmine project

Map the working directory to a Redmine project **identifier** with the table in
`projects.md`, next to this file. It is local to this installation and not in the repository
(`projects.md.example` shows the format). No `projects.md`, or the work isn't in it: say so
and ask — the map is the only source of project identifiers.

Call `list_redmine_projects` and resolve the mapped identifier to its **numeric `id`** —
`create_redmine_issue` and the time-entry tools want the integer project id, not the
identifier string. If you can't tell which project the work belongs to, **ask** — don't
guess, don't invent a project.

### 2. Compute hours

`elapsed = last − started` from the `WORK SESSION` line, in hours, **rounded to the nearest
0.25, minimum 0.25**. Logging right as you finish, set `last` to now first. Count actual
working time, not wall-clock time you were idle — that is what `last` is for. A line without
a `last` (written before this format): log the minimum 0.25 and say in the comment that the
duration is unknown, rather than guessing from `started`.

### 3. Resolve the "AI Agent" activity id

Call `list_time_entry_activities`, find the entry named **"AI Agent"**, keep its `id`.
If it's missing, Redmine hasn't been set up for agent time tracking yet — tell Luděk and stop.

### 4. Find or create the issue (one issue per task)

If you already claimed an issue for this work (see [Claim before work](#claim-before-work)),
that's the one — log against it and skip the search. Creating a second issue for work that
already has one is the mistake to avoid here.

- Call `search_redmine_issues` (`query` = a few words from the task) or `list_redmine_issues`
  scoped to the project for an **open** issue that already matches this task (you may be
  resuming work). If found, use its `id`.
- Otherwise `create_redmine_issue`:
  - `project_id`: the **numeric id** from step 1
  - `subject`: a short, specific task title (e.g. *"Fix CLS on blog list pages"*, not *"work"*)
  - `description`: 1–3 sentences — what and why
  - `fields`: an object with `tracker_id` (from `list_project_trackers` for this project —
    use the one that matches the project name), `status_id` for **"In progress"** (look it
    up with `list_redmine_issue_statuses`), and `assigned_to_id` = your own user id
    (`get_current_user`).

`status_id`/`status_name` writes now work on every tracker (fixed 2026-09-21 — see
[What your Redmine role can't do](#what-your-redmine-role-cant-do)). `parent_issue_id` is
still **dropped silently** — the issue is created but stays top-level. Read the issue back
after any status or parent write rather than assuming it landed.

### 5. File the time entry

`manage_time_entry`:
  - `action`: `"create"`
  - `issue_id`: from step 4
  - `hours`: from step 2
  - `activity_id`: the "AI Agent" id from step 3
  - `spent_on`: today (`YYYY-MM-DD`)
  - `comments`: one factual sentence on what you did, suffixed with your agent tag —
    `… (ClawBot)`. Max 255 chars, no filler.
  - Do **not** pass `user_id` — it defaults to your own account.

### 6. Close the task if it's done

If the task is complete and produced its deliverable, `update_redmine_issue` to set the
status to **"Done"** and `done_ratio` 100 (pass these in `fields`). Leave it "In progress"
if there's follow-up work.

Then **read the issue back** and check the status actually changed. `Done` is not a
closing status on this instance — only `Closed` is — so don't mark something Done
just because code exists; if it's written but not deployed or not wired up, say so and
leave the issue open.

### 7. Record that it's logged

Change that `WORK SESSION` line's trailing state in `MEMORY.md` to `logged <time-entry-id>`.

## Verify

`list_time_entries` scoped to the project + today — confirm the entry shows your account,
activity `AI Agent`, and the agent-tag comment suffix.

Human-readable check, for Luděk: the project's **Time entries** tab, and its **Report**
grouped by Activity — "AI Agent" hours are a separate line from human "Development" /
"Design" hours.

## What your Redmine role can't do

Redmine doesn't reject an attribute your role may not write — it drops it and still answers
`200`/`204`. So read every changed record back instead of trusting the response.

- **Status changes** work. If one is unexpectedly dropped on some tracker, report it; don't
  loop on it or retry blindly.
- **`parent_issue_id`** is dropped: you can't nest subtasks. Say what you couldn't do and stop —
  it's Luděk's to fix.

What works: `subject`, `description`, `tracker_id`, `assigned_to_id`, `done_ratio`,
`status_id`/`status_name`, notes, and all time-entry writes.

## Notes

- Never log to a project that isn't in `projects.md`.
- If issue creation fails with a tracker or permission error, that project isn't set up for
  agents yet — report it, don't retry blindly.
- The server wraps free-text fields in returned JSON in `<insecure-content-…>` markers as a
  prompt-injection guard. That's a display wrapper on reads only — the stored value is
  clean; don't include those markers when you write text back.
