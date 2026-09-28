# Build context: the repository root (see docker-compose.yml).

# --- Source Stage ---
# IronClaw is built from upstream nearai/ironclaw, pinned to one commit, plus the
# local changes in patches/ironclaw/ (internal MCP gateway extension, no model
# override when it names the configured model).
# To move to a newer IronClaw: bump IRONCLAW_REF, rebuild, fix any patch that no
# longer applies.
FROM rust:1.92-bookworm AS source

ARG IRONCLAW_REPO=https://github.com/nearai/ironclaw.git
ARG IRONCLAW_REF=9b4fa6383ebfc8d927dd5cf948b264290faeb2c2

RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ironclaw
RUN git init -q . \
    && git remote add origin "$IRONCLAW_REPO" \
    && git fetch -q --depth 1 origin "$IRONCLAW_REF" \
    && git -c advice.detachedHead=false checkout -q FETCH_HEAD

COPY patches/ironclaw/ /patches/
RUN set -e; for p in /patches/*.patch; do echo "Applying $p"; git apply --index "$p"; done

# --- Builder Stage ---
FROM source AS builder

# Build workspace in release mode
RUN cargo build --release --workspace --features webui-v2-beta,slack-v2-host-beta,postgres

# Extract only executable binaries
RUN mkdir -p /build-bin && \
    find target/release/ -maxdepth 1 -type f -executable -exec cp {} /build-bin/ \;

# --- Proxy Stage ---
# The ironclaw binary's embedded SPA lacks js/pages/logs/, so the proxy serves
# that directory itself, straight from the patched source.
FROM nginx:alpine AS proxy
COPY --from=source /ironclaw/crates/ironclaw_webui_v2_static/static/js/pages/logs/ /nginx-logs/
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# --- Runner Stage ---
FROM debian:bookworm-slim AS runner

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
        python3 \
        python3-pip \
        python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Trust the internal MCP gateway's TLS CA. `ironclaw_network` builds reqwest
# with `rustls-tls-native-roots`, so the system trust store is what it reads.
# Generate the cert first: sh mcp-tls/gen-certs.sh
COPY mcp-tls/certs/ca.crt /usr/local/share/ca-certificates/clawbot-mcp-ca.crt
RUN update-ca-certificates

# Copy compiled binaries from builder stage
COPY --from=builder /build-bin/* /usr/local/bin/

# Ensure generic "ironclaw" alias points to the compiled reborn binary if present
RUN if [ -f /usr/local/bin/ironclaw-reborn ]; then ln -sf /usr/local/bin/ironclaw-reborn /usr/local/bin/ironclaw; fi

# Setup directories
RUN mkdir -p /root/.ironclaw/reborn
WORKDIR /root/.ironclaw/reborn

# Copy startup configurations and scripts
COPY ironclaw/config.toml /root/.ironclaw/reborn/config.toml
COPY docker/ironclaw/start.sh /usr/local/bin/start-ironclaw.sh
RUN chmod +x /usr/local/bin/start-ironclaw.sh

EXPOSE 18789
CMD ["/usr/local/bin/start-ironclaw.sh"]
