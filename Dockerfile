# ── Stage 1: build the TypeScript API ─────────────────────────────────────────
FROM node:22-slim AS node-build

WORKDIR /build/api
COPY api/package*.json ./
RUN npm ci
COPY api/ ./
RUN npm run build

# ── Stage 2: final runtime image ──────────────────────────────────────────────
FROM python:3.12-slim

# Install Node.js runtime (no build tools needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies (sherlock) ─────────────────────────────────────────────
COPY sherlock_project/ ./sherlock_project/
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
        tomli \
        requests \
        requests-futures \
        colorama \
        pandas \
        openpyxl \
        PySocks \
        certifi

# ── Python bridge script ───────────────────────────────────────────────────────
COPY sherlock_bridge.py ./

# ── Node.js API (compiled JS + production node_modules) ───────────────────────
COPY --from=node-build /build/api/dist ./api/dist
COPY api/package*.json ./api/
RUN cd api && npm ci --omit=dev

# Railway injects PORT at runtime; default to 3000 for local runs.
ENV PORT=3000
EXPOSE 3000

CMD ["node", "api/dist/index.js"]
