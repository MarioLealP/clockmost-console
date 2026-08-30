# clockmost-console

The clockmost dashboard. `https://console.clockmost.com` — VPN-only, behind
Authentik forward-auth.

## Shape

```
 host timer (~20s) ─ clockmost-console-state ─▶ /var/lib/clockmost-console/state.json
                                                     │ bind-mounted ro
 clockmost-console container                         │
   FastAPI BFF  (backend/)  ◀──────────────────── reads it, keeps Snapshot history
     ├─ GET /api/infra          latest snapshot + 6h history
     ├─ GET /api/infra/history  ?hours=
     ├─ GET/PUT /api/prefs      per-Authentik-user UI state
     ├─ GET /api/health
     └─ serves the React build (dist/) as the SPA
   React 19 + Vite 8 + Tailwind v4  (src/)  — the Endfield design system
```

- **frontend** — `src/`, `package.json`. React + Vite + Tailwind v4 on
  `endfield.css`, linted by oxlint, formatted by oxfmt.
- **backend** — `backend/`, `pyproject.toml` (uv). FastAPI + SQLModel + Alembic,
  SQLite (`sqlite+aiosqlite`, swap to Postgres via `CM_DATABASE_URL`). Linted +
  formatted by **ruff**, typed by **mypy**.

## Dev

```sh
# backend
cd backend
uv sync
CM_STATE_FILE=/some/state.json uv run alembic upgrade head
CM_STATE_FILE=/some/state.json uv run uvicorn app.main:app --reload --port 8787

# frontend (separate shell) — /api is proxied to :8787
pnpm install
pnpm dev
```

`pnpm check` runs the web gate (oxfmt / oxlint / tsc / vitest); `cd backend &&
uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run
pytest` runs the API gate. Both are the CI `web` / `api` jobs.

## Deploy

Built as one container (`Dockerfile`: node builds `dist/`, then a
`python:3.13` runtime runs `alembic upgrade head` + uvicorn). Deployed as a
compose stack in the infra repo at `clockmost-infra:projects/clockmost-console/`
with this repo's tree vendored under `app/` (same as `caddy`).

The stack bind-mounts `/var/lib/clockmost-console` (holds `state.json` written by
the host timer + `console.db`), and gets `CM_HA_*` from its sops `secrets.env`.

To ship: re-vendor into the infra repo, bump `image:` in
`projects/clockmost-console/compose.yaml`, commit + push — `clockmost-deploy`
builds and rolls it.

## Roadmap

- **Phase 1** ✅ — BFF + infra panels off `clockmost-status`.
- **Phase 2** — Home Assistant: `/api/ha/*` proxy + live WS, entity panels.
  Needs an HA long-lived token in the stack secrets.
- **Phase 3** — density pass, per-user layout (`/api/prefs`), history sparklines,
  entity actions (toggle a light).
