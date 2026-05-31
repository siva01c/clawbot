# HEARTBEAT.md

# Periodic background tasks. The agent checks this file each cycle.
# Syntax: cron-like schedule | skill name | description

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Weekly SEO audit — every Monday at 09:00
# 0 9 * * 1 | weekly-seo-audit | Run SEO audit on ludekkvapil.cz

# Daily competitor monitoring — every day at 08:00
# 0 8 * * * | competitor-monitoring | Scan OSINT corpus for competitor signals

# Daily support escalation review — every day at 08:30
# 30 8 * * * | support-escalation-review | Find and close knowledge gaps from yesterday

# NOTE: Uncomment the lines above (remove the leading #) when heartbeat scheduling
# is activated in OpenClaw. Currently all tasks are triggered manually.

# Add tasks below when you want the agent to check something periodically.
