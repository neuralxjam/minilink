# Setup

## Prerequisites

- Claude Code (latest)
- Python 3.11.9
- Docker Desktop (for the multi-container local stack)
- GitHub account
- Railway account — free Hobby plan is enough ([railway.app](https://railway.app))

## Step 1 — Install required Claude Code plugins

Run these in Claude Code (one at a time):

```
/plugin install claude-code-setup@claude-plugins-official
/plugin install superpowers@claude-plugins-official
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

These install **per-user** (in `~/.claude/`), not per-project — one-time install shared across all projects in this trio (MiniLink → WatchTower → InfraKit).

## Step 2 — Clone and install

```bash
git clone https://github.com/neuralxjam/minilink.git
cd minilink
python -m venv .venv
# Windows
.venv\Scripts\pip install -r requirements-dev.txt
# macOS / Linux
.venv/bin/pip install -r requirements-dev.txt
```

## Step 3 — Run locally

```bash
docker compose up
```

The API is at `http://localhost:8000` and the dashboard at `http://localhost:8000/`.

## Step 4 — Verify

```bash
curl -X POST http://localhost:8000/shorten \
  -d '{"url":"https://example.com"}' \
  -H 'Content-Type: application/json'
# → {"code": "abc123", "short_url": "http://localhost:8000/abc123"}

curl -i http://localhost:8000/abc123
# → 302 Location: https://example.com
```

## Step 5 — Deploy to Railway (first time)

Railway deploys from GitHub directly — no CLI needed for initial setup.

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → select `neuralxjam/minilink`. Railway detects `railway.toml` and builds using the Dockerfile.

2. **Add Postgres** — click **+ New** → **Database** → **Add PostgreSQL**. Railway auto-injects `DATABASE_URL` into the API service.

3. **Add Redis** — click **+ New** → **Database** → **Add Redis**. Railway auto-injects `REDIS_URL`.

4. **Add `BASE_URL`** — API service → **Variables** tab → **+ New Variable**:
   - Key: `BASE_URL`
   - Value: (you'll fill this in after Step 5)

5. **Generate the public domain** — API service → **Settings** → **Networking** → **Generate Domain**. Copy the `*.up.railway.app` hostname shown and paste it as the `BASE_URL` value from Step 4. Then set **Target Port** to **8080** in the same Networking section.

6. Trigger the first deploy — Railway usually auto-deploys after Step 1. If not, go to **Deployments** → **Deploy Now**.

The app will be live at the domain from Step 5.

## Step 6 — CI auto-deploy

Railway's GitHub App watches the repository. Every push to `main` automatically triggers a Railway redeploy — no tokens or secrets needed beyond the initial GitHub connection in Step 5.

The GitHub Actions workflow (`.github/workflows/`) runs **lint → test → build + push to GHCR** on every push. Railway then picks up the new commit and redeploys from the Dockerfile.

## Troubleshooting

- **Port 8000 already in use**: `docker compose down` first, or change the host port in `docker-compose.yml`.
- **Postgres connection refused on startup**: the healthcheck in `docker-compose.yml` gates the API on `pg_isready`; if it still fails, run `docker compose down -v` and `docker compose up` again.
- **502 Bad Gateway with `X-Railway-Fallback`**: check API service → **Settings → Networking → Target Port**. Must be **8080**, not 8000.
- **`short_url` in API responses shows wrong domain**: update the `BASE_URL` variable in the API service's **Variables** tab to match the domain shown in Settings → Networking.
