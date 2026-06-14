# --- Builder Stage ---
FROM rust:1.92-bookworm AS builder

RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy local nearai/ironclaw repository
COPY scratch-ironclaw-repo /ironclaw
WORKDIR /ironclaw

# Build workspace in release mode
RUN cargo build --release --workspace --features webui-v2-beta,slack-v2-host-beta,postgres

# Extract only executable binaries
RUN mkdir -p /build-bin && \
    find target/release/ -maxdepth 1 -type f -executable -exec cp {} /build-bin/ \;

# --- Runner Stage ---
FROM debian:bookworm-slim AS runner

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
        hugo \
        python3 \
        python3-pip \
        python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy compiled binaries from builder stage
COPY --from=builder /build-bin/* /usr/local/bin/

# Ensure generic "ironclaw" alias points to the compiled reborn binary if present
RUN if [ -f /usr/local/bin/ironclaw-reborn ]; then ln -sf /usr/local/bin/ironclaw-reborn /usr/local/bin/ironclaw; fi

# Setup directories
RUN mkdir -p /root/.ironclaw/reborn
WORKDIR /root/.ironclaw/reborn

# Copy startup configurations and scripts
COPY clawbot/ironclaw/config.toml /root/.ironclaw/reborn/config.toml
COPY clawbot/docker/ironclaw/start.sh /usr/local/bin/start-ironclaw.sh
RUN chmod +x /usr/local/bin/start-ironclaw.sh

EXPOSE 18789
CMD ["/usr/local/bin/start-ironclaw.sh"]
