# MiniLink

> Self-hosted URL shortener with redirect analytics — FastAPI · PostgreSQL · Redis · Docker · Railway

**Live demo → [minilink-production.up.railway.app](https://minilink-production.up.railway.app)**

![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-multi--stage-2496ED?logo=docker&logoColor=white)
![Railway](https://img.shields.io/badge/deployed-Railway-0B0D0E?logo=railway&logoColor=white)
![CI](https://github.com/neuralxjam/minilink/actions/workflows/ci.yml/badge.svg)

---

## What it does

Paste a long URL into the dashboard, get a short code back. Every redirect is recorded and the dashboard surfaces your top links by hit count.

| Endpoint | Behaviour |
|---|---|
| `POST /shorten` | Accept a URL, return `{"code": "abc123", "short_url": "https://..."}` |
| `GET /{code}` | 302-redirect to the original URL (Redis-cached; falls back to Postgres on miss) |
| `GET /` | HTMX dashboard — top 20 links, sortable by hits |

## Why this project

This is **Project 4** of a three-project DevOps-focused trio (MiniLink → WatchTower → InfraKit) built to close the "I only write frontend" gap in my portfolio. The URL shortener is the classic systems design warm-up — contained scope, three distinct layers, real production patterns.

**DevOps skills demonstrated:**

- **Multi-stage Docker build** — builder stage installs dependencies; runtime stage copies only the artifact. Keeps the final image ≈150 MB vs. 1 GB+ for a naive single-stage build.
- **Docker Compose** — one command (`docker compose up`) brings up the API, Postgres, and Redis locally with health-gated startup ordering.
- **Redis read-through cache** — short-code lookups hit Redis first. On a miss, the code fetches from Postgres and warms the cache. On a hit, Postgres is never touched.
- **CI/CD pipeline** — GitHub Actions runs lint (ruff) → tests (pytest) → builds a Docker image → pushes to GHCR on every commit to `main`. Railway redeploys automatically on the same push.
- **Railway cloud deploy** — managed Postgres and Redis provisioned as Railway services; env vars injected automatically; public HTTPS domain with one click.

## Architecture

```
Browser
  │
  ▼
FastAPI  (Railway — Dockerfile, port 8080)
  │
  ├─ short-code lookup
  │       │
  │       ▼
  │    Redis  ──── miss ────►  PostgreSQL
  │   (cache)  ◄──── fill ───  (source of truth)
  │
  └─ hit counter write ──────► PostgreSQL
```

Reads go to Redis first. A cache miss falls through to Postgres and warms the entry with a 24-hour TTL. Writes (new short code, hit counter increment) go straight to Postgres; the cache entry is written through or invalidated as appropriate.

## Local quickstart

Requires Docker Desktop. No local Postgres or Redis install needed.

```bash
git clone https://github.com/neuralxjam/minilink.git
cd minilink
python -m venv .venv

# Windows
.venv\Scripts\pip install -r requirements-dev.txt
# macOS / Linux
.venv/bin/pip install -r requirements-dev.txt

docker compose up
```

Visit `http://localhost:8000` — the dashboard loads. To smoke-test the API:

```bash
# shorten a URL
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
# → {"code":"abc123","short_url":"http://localhost:8000/abc123"}

# follow the redirect
curl -i http://localhost:8000/abc123
# → 302 Location: https://example.com
```

## Deploy your own

See [`setup.md`](./setup.md) for full Railway setup instructions (5-minute process, free tier).

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI + SQLModel |
| Database | PostgreSQL (Railway managed) |
| Cache | Redis (Railway managed) |
| Container | Docker multi-stage build |
| Local orchestration | Docker Compose |
| CI/CD | GitHub Actions → GHCR → Railway auto-deploy |
| Dashboard UI | HTMX + Tailwind CSS |

## Roadmap / known limitations

- [ ] Rate limiting per IP (stretch goal)
- [ ] Custom short codes
- [ ] Click analytics by country (via `CF-IPCountry` header)
- [ ] Dashboard has no delete or expire UI — links live forever unless removed via the DB
- [ ] Single-region deploy; no CDN or edge caching for the redirect path

## See also

- [`CLAUDE.md`](./CLAUDE.md) — project overview, architecture, and conventions
- [`setup.md`](./setup.md) — first-time local and Railway setup
- [`SKILLS.md`](./SKILLS.md) — Claude Skills used in this project
- [`mcp.md`](./mcp.md) — MCP server configuration
