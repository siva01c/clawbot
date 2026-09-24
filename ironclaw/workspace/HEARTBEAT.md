# HEARTBEAT.md

# Periodic background tasks. The agent checks this file each cycle.
# Syntax: cron-like schedule | skill name | description

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# No pipelines here. What runs and when is n8n's call (SOUL.md, IDENTITY.md): the weekly SEO
# audit, competitor monitoring and the support-escalation review are n8n workflows that call
# ClawBot for the analysis step. Scheduling them here as well would run them twice, and would
# have ClawBot start work its role says it never starts.

# End-of-day time-tracking flush — every day at 18:00. Bookkeeping of ClawBot's own hours,
# not a pipeline: logs `last − started` of each open WORK SESSION line in MEMORY.md.
0 18 * * * | redmine-time-tracking | Flush open WORK SESSION lines from MEMORY.md to Redmine
