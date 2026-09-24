#!/bin/sh
set -eu

RUNTIME_DIR="/root/.ironclaw/reborn"
WORKSPACE_DIR="$RUNTIME_DIR/workspace"

echo "Starting IronClaw secure runtime setup..."

# Ensure config directories exist
mkdir -p "$RUNTIME_DIR"
mkdir -p "$WORKSPACE_DIR"

# Copy dynamic configs from read-only mount if present
if [ -f "/ironclaw-src/config.toml" ]; then
    echo "Syncing IronClaw configuration..."
    cp "/ironclaw-src/config.toml" "$RUNTIME_DIR/config.toml"
fi

# TOOLS.md, USER.md and the Redmine project map are gitignored (the repo is public), so a
# fresh clone has only the templates, and the commit that untracked them deletes them from a
# checkout on `git pull`. Seed a missing one from its template so the agent never starts
# without them, and say so loudly: the template holds placeholders, not this host's values.
for name in TOOLS.md USER.md skills/redmine-time-tracking/projects.md; do
    if [ ! -f "$WORKSPACE_DIR/$name" ] && [ -f "$WORKSPACE_DIR/$name.example" ]; then
        cp "$WORKSPACE_DIR/$name.example" "$WORKSPACE_DIR/$name"
        echo "WARNING: $name was missing — seeded from $name.example (placeholders)." \
             "Fill in ironclaw/workspace/$name on the host, then: docker compose restart ironclaw" >&2
    fi
done

# Ensure correct permissions
chmod 700 "$RUNTIME_DIR" || true
[ -f "$RUNTIME_DIR/config.toml" ] && chmod 600 "$RUNTIME_DIR/config.toml" || true

# Start IronClaw Server
echo "Launching IronClaw secure agent gateway..."
cd "$WORKSPACE_DIR"
exec ironclaw serve --port 18789
