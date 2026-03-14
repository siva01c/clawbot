FROM node:22-bookworm-slim AS base

ARG TARGET_ENV=production

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g openclaw@latest

RUN mkdir -p /root/.openclaw
COPY docker/openclaw/start.sh /usr/local/bin/start-openclaw.sh
RUN chmod +x /usr/local/bin/start-openclaw.sh

# Development stage
FROM base AS dev
COPY openclaw/openclaw.json /root/.openclaw/openclaw.json
COPY openclaw/extensions/ /root/.openclaw/extensions/
VOLUME /root/.openclaw
EXPOSE 18789
CMD ["/usr/local/bin/start-openclaw.sh"]

# Production stage
FROM base AS production
COPY openclaw/openclaw.json /root/.openclaw/openclaw.json
COPY openclaw/extensions/ /root/.openclaw/extensions/
RUN chmod 700 ~/.openclaw && chmod 600 /root/.openclaw/openclaw.json
EXPOSE 18789
CMD ["/usr/local/bin/start-openclaw.sh"]

# Final stage - choose based on TARGET_ENV
FROM ${TARGET_ENV:-production} AS final

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:18789/ || exit 1
