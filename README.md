# MiniLink

> Self-hosted URL shortener with redirect analytics. POST a long URL, get a short code; GET the short code, redirect and increment a hit counter.

**Status**: Day 0 — repo scaffolding only. Application code starts Day 1. Live demo URL will land here once Day 7 (fly.io deploy) ships.

**Stack**: FastAPI · SQLModel · PostgreSQL · Redis · Docker (multi-stage) · Docker Compose · GitHub Actions · fly.io · HTMX + Tailwind

**Why this project exists**: closes the DevOps gap in [my portfolio](https://neuralxjam.github.io) — multi-stage Docker, Compose, Redis caching, GHCR image publishing, and a real cloud deploy. Project 4 of a 3-project DevOps trio (MiniLink → WatchTower → InfraKit).

## See also

- [`CLAUDE.md`](./CLAUDE.md) — project overview + conventions
- [`setup.md`](./setup.md) — first-time setup
- [`SKILLS.md`](./SKILLS.md) — Claude Skills used
- [`mcp.md`](./mcp.md) — MCP server config
