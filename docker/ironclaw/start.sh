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

# Ensure correct permissions
chmod 700 "$RUNTIME_DIR" || true
[ -f "$RUNTIME_DIR/config.toml" ] && chmod 600 "$RUNTIME_DIR/config.toml" || true

# Start IronClaw Server
echo "Launching IronClaw secure agent gateway..."
cd "$WORKSPACE_DIR"
exec ironclaw serve --port 18789
