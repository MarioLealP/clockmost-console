# syntax=docker/dockerfile:1
# clockmost-console — build the SPA with Node, run it (+ the BFF) on Python.

# ---- stage 1: the React build ----------------------------------------------
FROM node:24-alpine AS web
WORKDIR /web
RUN corepack enable
COPY pnpm-lock.yaml package.json ./
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile
COPY index.html vite.config.ts tsconfig.json ./
COPY src ./src
RUN pnpm build

# ---- stage 2: the Python runtime ------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS api
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project
COPY backend/ ./
COPY --from=web /web/dist ./dist

ENV PATH="/app/.venv/bin:$PATH" \
    CM_DIST_DIR=/app/dist \
    CM_STATE_FILE=/data/state.json \
    CM_DATABASE_URL=sqlite+aiosqlite:////data/console.db

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --start-period=8s --retries=3 \
  CMD wget -qO- http://127.0.0.1/api/health >/dev/null 2>&1 || exit 1

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 80 --no-access-log"]
