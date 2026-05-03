# Setup

## Prerequisites

- Claude Code (latest)
- Python 3.11.9 (a `.python-version` file will be added on Day 7 to pin this for fly.io's builder)
- Docker Desktop (for the multi-container local stack starting Day 4)
- GitHub account
- (later, Day 7) fly.io account — free tier is enough

## Step 1 — Install required Claude Code plugins

Run these in Claude Code (one at a time):

```
/plugin install claude-code-setup@claude-plugins-official
/plugin install superpowers@claude-plugins-official
/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
/plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

These install **per-user** (in `~/.claude/`), not per-project — so they're a one-time install across all 3 projects in this trio (MiniLink, WatchTower, InfraKit). If you've already installed them for an earlier project, skip this step.

## Step 2 — Clone and install

```
git clone https://github.com/neuralxjam/minilink.git
cd minilink
# (Day 1+: Python venv + requirements.txt setup goes here)
```

## Step 3 — Run

```
# (Day 5+: docker compose up brings up API + Postgres + Redis)
docker compose up
```

The API will be reachable at `http://localhost:8000` once Day 1's FastAPI scaffold lands.

## Step 4 — Verify

```
# (Day 1+: smoke tests for /shorten and /{code})
curl -X POST http://localhost:8000/shorten -d '{"url":"https://example.com"}' -H 'Content-Type: application/json'
# returns {"code": "abc123", "short_url": "http://localhost:8000/abc123"}

curl -i http://localhost:8000/abc123
# returns 302 with Location: https://example.com
```

## Troubleshooting

- **Port 8000 already in use**: another process is bound. `docker compose down` first, or change the port in `docker-compose.yml`.
- **Postgres connection refused**: the API container started before Postgres was ready. Add a healthcheck + `depends_on: condition: service_healthy` to `docker-compose.yml` (Day 5).
- **Python version mismatch on fly.io**: ensure `.python-version` exists with `3.11.9` (the same gotcha as Render — fly.io's builder respects this file).
