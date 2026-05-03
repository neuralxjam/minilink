# MiniLink

> Self-hosted URL shortener with redirect analytics. POST a long URL, get a short code; GET the short code, redirect and increment a hit counter.

## Overview

MiniLink is a small but production-shaped URL shortener. It exposes a JSON API for creating short links and a redirect endpoint for resolving them, backed by Postgres for durable storage and Redis as a hot-path cache. A small HTMX dashboard surfaces top links and hits over time.

The project's purpose is to demonstrate **DevOps fundamentals** in a tight scope: multi-stage Docker builds, Docker Compose for local multi-service dev, GHCR image publishing from CI, and a real cloud deploy on fly.io.

## Stack

- FastAPI + SQLModel
- PostgreSQL (durable storage)
- Redis (read-through cache for short-code lookups)
- Docker (multi-stage build) + Docker Compose (local orchestration)
- GitHub Actions (lint → test → build image → push to GHCR → deploy)
- fly.io (multi-container deploy target, free tier)
- HTMX + Tailwind (dashboard UI)

## Common commands

| Command | What it does |
|---|---|
| `docker compose up` | Bring up API + Postgres + Redis locally |
| `docker compose down -v` | Tear down and wipe volumes |
| `pytest` | Run the test suite |
| `ruff check .` | Lint |
| `fly deploy` | Push the current image to fly.io (after Day 7) |

*(commands without a working implementation yet are placeholders; they get real on the day the corresponding feature lands)*

## Architecture

```
                  ┌────────────┐
   browser ─────► │  FastAPI   │
                  └─────┬──────┘
                        │  short-code lookup
                        ▼
                  ┌────────────┐    miss    ┌──────────────┐
                  │   Redis    │ ─────────► │  PostgreSQL  │
                  │  (cache)   │ ◄───────── │  (truth)     │
                  └────────────┘    fill    └──────────────┘
```

Reads hit Redis first; on miss, fall through to Postgres and warm the cache. Writes go straight to Postgres and invalidate (or write-through) the cache entry.

## Conventions

- Commit messages: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`)
- Branches: `main` is protected; feature work on `feat/<short-name>` branches
- No auto-push to `main`. No `git push --force`. No skipping pre-commit hooks.
- Pacing: ask before large multi-file refactors; small targeted edits preferred.
- Python: 3.11.9 (see `.python-version` once created — fly.io builder respects it).

## See also

- `setup.md` — first-time setup
- `SKILLS.md` — available Claude Skills
- `mcp.md` — MCP server config
