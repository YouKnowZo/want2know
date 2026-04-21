# Want2Know by PaperBagExpress

## Overview
Want2Know is an OSINT (Open Source Intelligence) tool by PaperBagExpress that searches for user profiles across 1000+ social media platforms. Provides a modern light-theme web UI, CLI, and Python library interface.

OSINT Toolkit (14 tools, 100% free, no API keys):
- Phone Number Intel (carrier, line type, area-code city/state, risk, all formats)
- Email Intel (validation, MX, SPF/DMARC, Gravatar, Google dorks)
- IP / Domain Geolocation (with embedded Leaflet map)
- WHOIS / RDAP
- DNS Records (A/AAAA/MX/NS/TXT/CNAME/SOA/CAA/DMARC via Cloudflare DoH)
- Subdomain Finder (crt.sh Certificate Transparency)
- Security Headers (graded against HSTS/CSP/XFO/etc)
- Username Variations Generator
- Breach Analytics (XposedOrNot — real breach names, dates, exposed fields, risk score)
- Wayback Snapshots (Internet Archive CDX)
- Threat Intelligence (URLhaus + ThreatFox)
- GitHub Profile deep-scan (bio, repos, stars, languages)
- Reddit Profile deep-scan (karma, account age, recent subs/comments)
- Reverse Image Search (Google Lens, Yandex, TinEye, Bing, Karma Decay, SauceNAO link generators)
- Bulk Lookup (paste up to 50 / CSV upload, auto-detects type)
- PDF Report Export (jsPDF)
- Saved Cases (localStorage-backed investigations)
- Live searches counter (file-backed)

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
- **OPRecon OSINT Tools tab** with Phone Number Lookup and IP/Domain Geolocation

## OSINT Tools (8 total, all free, no API keys)
- `recon/phone_lookup.py` — phone intel: validity, carrier, line type, US area code → city/state, risk score, all formats (E.164/RFC3966/INTL/NATL), timezones. Backed by `phonenumbers` + local `recon/data/area_codes.json` (300+ NANP codes)
- `recon/ip_lookup.py` — IP/domain geolocation via ip-api.com
- `recon/whois_lookup.py` — WHOIS / RDAP domain & IP registration
- `recon/email_lookup.py` — email validation, MX/SPF/DMARC via Cloudflare DoH, Gravatar URL, MD5/SHA hashes, HIBP breach link, Google dork pivots
- `recon/dns_lookup.py` — A/AAAA/MX/NS/TXT/CNAME/SOA/CAA/DMARC records via Cloudflare DoH
- `recon/subdomain_lookup.py` — subdomain enumeration via crt.sh Certificate Transparency logs
- `recon/headers_lookup.py` — security header grading (HSTS/CSP/XFO/etc.) → A–F score, plus tech stack fingerprints
- Username variations generator (pure JS in-browser, 30+ variants incl. l33t-speak; chips clickable to feed back into Profile Search)

## API Endpoints (all POST)
- `/api/phone` { number } · `/api/ip` { target } · `/api/whois` { target }
- `/api/email` { email } · `/api/dns` { target } · `/api/subdomains` { target } · `/api/headers` { target }
- `/scan_progress` { uuid } → `{checked, total, found}` for live progress bar

## Performance / Anti-Freeze Fixes (Apr 2026)
- Rate limit raised 15 → 60/min (was blocking back-to-back scans)
- Fast-scan retry rounds reduced 3 → 1 (huge speedup; was main "freeze" cause)
- Concurrent request limit raised 15 → 25
- HTTP timeout lowered 2s → 1.5s
- New in-memory `_progress` tracker exposes accurate `X / Y sites checked` to the UI
- Loading overlay now shows authoritative progress bar + percent + live found count
