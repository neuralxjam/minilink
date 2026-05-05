# Setup

## Prerequisites

- Claude Code (latest)
- Python 3.11.9
- Docker Desktop (for the multi-container local stack)
- GitHub account
- fly.io account — free tier is enough

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

## Step 5 — Deploy to fly.io (first time)

Install flyctl and log in:

```bash
brew install flyctl       # macOS
# or: https://fly.io/docs/hands-on/install-flyctl/
fly auth login
```

Create the app and provision managed Postgres + Redis:

```bash
fly apps create minilink

fly postgres create --name minilink-db --region sin --vm-size shared-cpu-1x --volume-size 1
fly postgres attach --app minilink minilink-db

fly redis create --name minilink-redis --region sin --plan free
# copy the Redis URL from the output
fly secrets set REDIS_URL="<redis-url-from-above>" --app minilink
```

Deploy:

```bash
fly deploy
```

The app will be live at `https://minilink.fly.dev`.

## Step 6 — Wire up CI auto-deploy

Add `FLY_API_TOKEN` to GitHub repository secrets
(`Settings → Secrets and variables → Actions → New repository secret`):

```bash
fly tokens create deploy -x 999999h   # generate a long-lived token
# paste the output as the FLY_API_TOKEN secret value
```

From this point every push to `main` runs the full pipeline:
**lint → test → build + push to GHCR → fly deploy**.

## Troubleshooting

- **Port 8000 already in use**: `docker compose down` first, or change the host port in `docker-compose.yml`.
- **Postgres connection refused on startup**: the healthcheck in `docker-compose.yml` gates the API on `pg_isready`; if it still fails, run `docker compose down -v` and `docker compose up` again.
- **fly deploy fails with "app not found"**: ensure `fly apps create minilink` was run and the `app` field in `fly.toml` matches the created app name.
