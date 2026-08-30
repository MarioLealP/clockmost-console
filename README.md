# clockmost-console

The clockmost dashboard. Forked from `clockmost-frontend-template`; the demo
console screen is the starting point and grows into the real thing.

Lives at **https://console.clockmost.com** — VPN-only, behind Authentik
forward-auth.

## Stack

React 19 · Vite 8 · TypeScript 7 · Tailwind v4 (mapped onto the Endfield
`--ef-*` tokens) · oxlint + oxfmt (no ESLint, no Prettier) · Vitest.

Same split as the template: `.ef-*` classes for components and motifs, Tailwind
for layout and spacing; `src/styles/theme.css` bridges them. `src/styles/endfield.css`
is vendored from `Benylin/endfield-design` — refresh with `pnpm sync:endfield`.

## Commands

```sh
pnpm install
pnpm dev            # vite dev server
pnpm check          # fmt:check · lint · typecheck · test  (what CI runs)
pnpm build          # tsc --noEmit && vite build
```

## Deploy

The server build is an nginx-served static bundle.

```sh
docker build -t clockmost/clockmost-console:<version> .
```

The live deployment is a compose stack in the infra repo at
`clockmost-infra:projects/clockmost-console/` — it vendors this app's source
under `app/` and builds it there (`build: ./app`,
`image: clockmost/clockmost-console:<version>`), the same pattern as
`projects/caddy/`. To ship a new version:

1. land the change here, bump `<version>`;
2. re-vendor into the infra repo: from a checkout,
   `rsync -a --delete --exclude .git --exclude node_modules --exclude dist
./ /home/clockmost-infra/projects/clockmost-console/app/`;
3. bump the tag in `projects/clockmost-console/compose.yaml`;
4. commit + push the infra repo — `clockmost-deploy` builds and rolls it.

(A Gitea-Actions image build → registry → pinned-tag pipeline is the eventual
replacement for step 2–3; it needs a `write:package` token added as an Actions
secret.)

## CI

`.gitea/workflows/ci.yml` — one `smell` job: fmt → lint → typecheck → test →
build. Gate `main` on it in Gitea → Settings → Branches.
