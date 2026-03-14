#!/bin/sh
set -eu

echo "Updating openclaw to latest..."
npm install -g openclaw@latest

SRC_DIR="/openclaw-src"
RUNTIME_DIR="/root/.openclaw"
GATEWAY_URL="ws://127.0.0.1:18789"
AUTO_APPROVE_PAIRING="${OPENCLAW_AUTO_APPROVE_PAIRING:-true}"

echo "Starting OpenClaw setup..."

if [ -d "$SRC_DIR" ]; then
	echo "Syncing OpenClaw config from $SRC_DIR to $RUNTIME_DIR"
	mkdir -p "$RUNTIME_DIR"

	if [ -f "$SRC_DIR/openclaw.json" ]; then
		cp "$SRC_DIR/openclaw.json" "$RUNTIME_DIR/openclaw.json"
	fi

	if [ -d "$SRC_DIR/extensions" ]; then
		rm -rf "$RUNTIME_DIR/extensions"
		mkdir -p "$RUNTIME_DIR/extensions"
		cp -R "$SRC_DIR/extensions/." "$RUNTIME_DIR/extensions/"
	fi

	if [ -d "$SRC_DIR/identity" ]; then
		rm -rf "$RUNTIME_DIR/identity"
		mkdir -p "$RUNTIME_DIR/identity"
		cp -R "$SRC_DIR/identity/." "$RUNTIME_DIR/identity/"
	fi
fi

chmod 700 "$RUNTIME_DIR" || true
[ -f "$RUNTIME_DIR/openclaw.json" ] && chmod 600 "$RUNTIME_DIR/openclaw.json" || true
[ -d "$RUNTIME_DIR/identity" ] && chmod 700 "$RUNTIME_DIR/identity" || true
[ -f "$RUNTIME_DIR/identity/device.json" ] && chmod 600 "$RUNTIME_DIR/identity/device.json" || true

openclaw --version
echo "Starting gateway..."

openclaw gateway --port 18789 --allow-unconfigured &
GATEWAY_PID=$!

(
	sleep 3
	echo "=== Dashboard URL ==="
	openclaw dashboard --no-open 2>&1 | sed "s/:18789/:${OPENCLAW_PORT:-18789}/g" || true
	echo "====================="
) &

if [ "$AUTO_APPROVE_PAIRING" = "true" ]; then
	echo "Auto-approve pairing is enabled."
	(
		# Wait for gateway socket, then continuously approve pending requests.
		sleep 2
		while kill -0 "$GATEWAY_PID" 2>/dev/null; do
			if [ -n "${OPENCLAW_GATEWAY_TOKEN:-}" ]; then
				REQUEST_IDS=$(openclaw devices list --json --url "$GATEWAY_URL" --token "$OPENCLAW_GATEWAY_TOKEN" 2>/dev/null | sed -n 's/.*"requestId": "\([^"]*\)".*/\1/p' || true)
				if [ -n "$REQUEST_IDS" ]; then
					for REQUEST_ID in $REQUEST_IDS; do
						if openclaw devices approve "$REQUEST_ID" --url "$GATEWAY_URL" --token "$OPENCLAW_GATEWAY_TOKEN" >/dev/null 2>&1; then
							echo "Auto-approved pairing request: $REQUEST_ID"
						fi
					done
				fi
			fi
			sleep 3
		done
	) &
fi

wait "$GATEWAY_PID"