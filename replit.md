# Workspace

## Overview

pnpm workspace monorepo using TypeScript, plus a Python/Flask web app (Makedough).

## Makedough (Python/Flask)

**Location:** `artifacts/makedough/`

**Stack:** Python 3.11, Flask, recipe-scrapers, requests, Alpine.js (CDN)

**Run command:** `cd artifacts/makedough && python app.py`

**Workflow:** "Start application" — serves on port 5000

### Routes
- `GET /` — serves the HTML frontend
- `POST /extract` — accepts `{ url }`, returns `{ title, servings, total_time, ingredients[], steps[], source_url, author, host }`
- `POST /modify` — accepts `{ recipe, request, history }`, returns `{ ingredients[], changes_summary, flags[] }`

### Features (complete)
- URL input + Extract button frontend (Alpine.js reactive)
- `/extract` endpoint using `recipe_scrapers.scrape_html` with `wild_mode=True`
- Recipe modification via OpenRouter (`google/gemma-4-31b-it`) with iterative history chain
- Side-by-side Original | Current ingredient columns
- Shortcut chips: dietary restrictions, scale presets, volume/weight unit toggle
- Attribution: author + host displayed below recipe title

### Notes
- `OPENROUTER_API_KEY` stored in Replit secrets, never hardcoded
- Port 5000; workflow command kills stale process before starting Flask
- `recipe_scrapers.scrape_html(html, org_url=url, wild_mode=True)` — not `scrape_me`

## TypeScript Monorepo

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
