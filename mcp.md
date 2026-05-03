# MCP Servers

## User-level servers

Configured globally in `~/.claude.json` — available across all your projects.

## Project-level servers

Configured in `.mcp.json` at this repo's root — available only when working in this project.

| Server | Purpose | How configured |
|---|---|---|
| (none yet — add as project needs grow) | | |

## Suggested servers for MiniLink

| Server | Why useful here |
|---|---|
| `postgres` | Inspect schema, query the `links` and `hits` tables without leaving Claude Code |
| `redis` | Check cached short codes, TTLs, eviction behavior during the Day 3 caching work |
| `github` | Manage issues, pull requests, and Actions runs from inside the editor session |

## Setup

See the [Anthropic MCP docs](https://docs.anthropic.com/en/docs/claude-code/mcp) for adding servers.
For project-level servers, create `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "<name>": {
      "command": "<command>",
      "args": ["<arg>"]
    }
  }
}
```
