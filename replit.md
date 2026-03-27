# Social Analyzer

## Overview
An OSINT (Open Source Intelligence) tool that searches for user profiles across 1000+ social media platforms. Provides a modern web UI, CLI, and Python library interface.

## Architecture
- **Backend**: Node.js + Express.js (`app.js`)
- **Frontend**: Single-page HTML app (`public/app.html`) — Bootstrap 5, Selectize, vanilla JS
- **Modules**: `modules/` directory with scan engines and helpers
- **Data**: `data/sites.json` — 1000+ social media site detection rules

## Key Files
- `app.js` — Express server, API routes, CLI entry point
- `public/app.html` — Main frontend (modernized dark UI)
- `modules/helper.js` — Shared config, file paths, utilities
- `modules/fast-scan.js` — Fast HTTP-based profile detection
- `modules/slow-scan.js` — Slow Selenium-based detection
- `modules/special-scan.js` — Special detection methods
- `modules/external-apis.js` — Google/external API lookups
- `modules/name-analysis.js` — Name origin detection
- `modules/string-analysis.js` — Username string analysis
- `data/sites.json` — Site detection database

## Running
- **Start**: `node app.js --gui`
- **Port**: 5000 (listens on 0.0.0.0)
- **URL**: `/` redirects to `/app.html`
- **Workflow**: "Start application" → `node app.js --gui`

## Bug Fixes Applied
1. Removed Windows-only `n` package from dependencies
2. Fixed default port from 9005 → 5000
3. Changed server host from `localhost` to `0.0.0.0` for proxy compatibility
4. Fixed `countries_json_path` bug (was pointing to names.json)
5. Fixed `HttpsProxyAgent` missing `new` keyword
6. Changed `/generate` endpoint from GET to POST (body not available on GET)
7. Added root `/` redirect to `/app.html`
8. Added `selenium-webdriver` back to package.json

## New Features Added
- Modern dark GitHub-inspired UI (Bootstrap 5)
- Favicon (SVG)
- Search history (localStorage, last 10 searches)
- Summary stat cards (detected, scanned, origins, age hints)
- Profile cards with favicon thumbnails, color-coded tags
- CSV export
- JSON export
- Toast notifications
- Collapsible result sections with counts
- Word pill visualization for string analysis
- Fast Mode preset button
- Cancel task button in loading overlay
