# MAS Dallas CYP Conference App

Mobile-first web app for the MAS Dallas College & Young Professionals (CYP) conference — agenda,
speakers, live Q&A and feedback. Built with FastHTML + HTMX, PostgreSQL (Neon), deployed on Google Cloud Run.

Current edition: **4th Annual CYP Conference — Him & Her: Building Success at Every Stage**
(Saturday, Oct 24, 2026, GEM Academy & Facility, Plano).

## Environments

| | Production | Development |
|---|---|---|
| URL | https://mascyp.org (also https://app.mascyp.org; `www.mascyp.org` forwards here) | https://test.mascyp.org |
| Branch | `production` | `dev_2026` |
| Cloud Run service (us-west1, project `mas-cyp-con-2024-435900`) | `mas-cyp-con-2024` | `dev-mascyp-conference-webapp` |
| Database (Neon host) | `ep-rough-hill-…` (secret `DATABASE_URL_PROD`) | `ep-patient-tooth-…` (secret `DATABASE_URL_DEV`) |
| Date limits | Q&A and feedback open Oct 24, 10 AM (see `core/conference.py`) | None: everything always open |

The 2025 conference data is kept in the `archive_2025` Neon database. Workflow: changes are built and tested on
`dev_2026` (auto-deploys to dev), then merged to `production` when ready.

## Features

- **Home & theme** — "Him & Her" parchment/navy look shared by every page (`assets/theme-26.css`).
- **Agenda** — timeline of sessions with **tag filter pills** in two rows; none are selected at first (everything
  shows). Audience (Masculinity, Womanhood) is single-select; session type (Talk, Workshop, Discussion, Prayer,
  Break) is multi-select, showing sessions of any chosen type. Sessions tagged **All** ("Everyone") count as
  matching either audience.
- **Agenda editor** (admins, `/admin/agenda`) — click any field on a session card to edit it in place:
  times, title, location, tags, speakers (with "Add new speaker"), description (pop-up editor).
- **Speaker and sponsor editor** (admins, `/admin/speakers`, `/admin/sponsors`) — edit text, upload photos and
  logos, add and delete. Images are stored in the database (see [Database](#database)).
- **Speakers** are listed in program order (by their first session); sponsors in the order they were added.
- **Live Q&A** — only for sessions with a description, except titles in `NO_QA_TITLES` (`routes/qa.py`, currently
  the Qur'an Recitation). Guests submit questions; moderators approve, hide, mark answered or delete. Updates appear
  instantly for everyone without reloading (only the changed card or count is sent). Likes are one per visitor.
- **Feedback survey** — one submission per visitor, editable later.
- **Prayer times, about, registration** (`/registration` redirects to Ticket Tailor) pages.
- **Date windows** (production): Q&A and feedback show a "See You Soon" countdown until Oct 24, 10 AM; Q&A closes
  at the end of that day, feedback 7 days after the conference. Preview the closed page on dev at `/qa_soon`.
- **Coming Soon** page (`/coming-soon`): with `COMING_SOON=true` (production) it replaced every page until
  `SITE_OPENS` (Oct 17, 7 AM).

## Tech stack

- [FastHTML](https://fastht.ml) (Python) + HTMX, DaisyUI/Tailwind
- PostgreSQL on Neon via async SQLAlchemy + asyncpg
- Live updates: Server-Sent Events, fanned out across Cloud Run instances with Postgres `LISTEN/NOTIFY`
- Docker, Google Cloud Run, GitHub Actions

## Project structure

```
app/
├── main.py                  # Entry point; static files + route registration
├── core/
│   ├── app.py               # FastHTML app, headers, middleware, session key
│   ├── conference.py        # Conference dates, site opening, Q&A/feedback windows
│   ├── coming_soon_gate.py  # Serves only the coming soon page until the site opens
│   ├── static.py            # Loads every assets/*.css|*.js on all pages (sorted)
│   └── visitor.py           # Anonymous visitor cookie (likes, feedback)
├── routes/                  # Pages and endpoints
│   ├── main.py              # Home, about, prayer times, registration, coming soon
│   ├── session.py           # Agenda + session details
│   ├── agenda_admin.py      # Agenda editor
│   ├── people_admin.py      # Speaker and sponsor editor, photo/logo uploads
│   ├── media.py             # Serves uploaded images at /media/<id>
│   ├── qa.py                # Q&A (guest + moderator) and live stream
│   ├── feedback.py          # Feedback survey
│   ├── speaker.py, sponsor.py
│   └── admin.py             # Login/logout, admin dashboard
├── components/              # UI components (home, theme, timeline, qa, cards, feedback message card…)
├── crud/                    # Database operations
├── db/                      # Models, schemas, connection
├── utils/
│   ├── auth.py              # Passwords, @require_moderator, date-window decorators
│   ├── live/                # Live Q&A: hub (local subscribers), bus (Postgres NOTIFY), render
│   ├── images.py            # Resizes and stores uploaded photos/logos
│   ├── tags.py              # Session tag rules
│   └── speaker_utils.py     # Placeholder avatars
├── assets/                  # CSS, JS (qa-live.js, agenda-filter.js), icons (speaker/sponsor images are in the DB)
├── load_2026_program.py     # Creates tables + loads the 2026 program
├── load_2026_speakers_sponsors.py  # Fills speaker bios and sponsor details
├── sync_prod_from_dev.py    # Copies dev's content (and images) to prod
├── migrate_event_tags.py    # Converts old event categories to tags
├── create_admin.py          # Create a moderator/admin account
└── reset_admin_password.py  # Reset an account's password
```

## Local development

1. Create `.env` in the repo root:
   ```
   ENVIRONMENT=development
   PORT=8080
   HOST=0.0.0.0
   DATABASE_URL=postgresql://USER:PASSWORD@HOST-pooler.REGION.aws.neon.tech/neondb
   ```
   No quotes, and no `?sslmode=...` suffix (asyncpg negotiates SSL itself). Always point local development at the
   **development** database.

2. Run with Docker (recommended — live reload on code changes):
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```
   or directly:
   ```bash
   uv sync
   cd app && uv run --env-file ../.env uvicorn main:app --reload --port 8080
   ```

3. Open http://localhost:8080. Moderator login: http://localhost:8080/admin_login

### Optional settings

| Variable | Purpose |
|---|---|
| `DATABASE_URL_DIRECT` | Direct (non-pooler) Neon URL for live Q&A `LISTEN`. Defaults to `DATABASE_URL` with `-pooler` removed. |
| `SESSION_SECRET` | Key that signs login cookies. Required on Cloud Run; locally a git-ignored `.sesskey` file is generated. |
| `COMING_SOON` | `true` serves only the coming soon page (static assets stay reachable) until `SITE_OPENS` in `core/conference.py`, then the site opens by itself. Set in `deploy-prod.yml`; change it to `false` and push `production` to open the site early. |
| `RESTRICT_TO_CONFERENCE_DAY` | `true` opens Q&A and feedback at `INTERACTIVE_OPENS` (Oct 24, 10 AM) and closes Q&A at the end of that day and feedback 7 days later. On by default when `ENVIRONMENT=production`, off otherwise; set `false` to lift it on prod. Dates live in `core/conference.py`. |

## Database

Run these from `app/` (with Docker: `docker exec -it mas_cyp_con_2024-app-1 uv run python <script>`).
Every script prints the target database and does a dry run unless `--apply` is given.

| Task | Command |
|---|---|
| Set up a new database (tables + 2026 program) | `python load_2026_program.py --apply` |
| Fill speaker bios and sponsor details, add missing sponsors (photos and logos are uploaded in the app) | `python load_2026_speakers_sponsors.py --apply` (`--overwrite` replaces existing text) |
| Convert an older database's categories to tags | `python migrate_event_tags.py --apply` |
| Make prod's content (sessions, speakers, sponsors, prayer times, uploaded images) match dev; replaces prod's copies (prod Q&A questions go with them), keeps accounts and feedback, backs up to `app/backups/` | `DEV_DATABASE_URL=… PROD_DATABASE_URL=… python sync_prod_from_dev.py --apply` (see below) |
| Create a moderator/admin account (password from standard input, optional expiry in Dallas time) | `op read "op://<vault>/<item>/password" \| python create_account.py <username> --role moderator --expires 2026-10-25T02:00 --apply` |
| Create a moderator/admin account (interactive, older) | `python create_admin.py` |
| Reset a password | `python reset_admin_password.py` |

**Syncing dev to prod.** Take `PROD_DATABASE_URL` from the live service, not from a local `.env`:
```bash
gcloud run services describe mas-cyp-con-2024 --project mas-cyp-con-2024-435900 --region us-west1 \
  --format=json | python3 -c "import json,sys; print(next(e['value'] for e in json.load(sys.stdin)['spec']['template']['spec']['containers'][0]['env'] if e['name']=='DATABASE_URL'))"
```
Check that the dry run's "to prod" host is `ep-rough-hill-…` before adding `--apply`. When code adds a table or
column, push `production` and run the sync straight away; the new code fails until prod's schema matches. From
conference day on, don't sync: it would delete the day's real Q&A questions.

Day-to-day content is edited in the app (admin accounts):
- sessions, tags, descriptions and who speaks: `/admin/agenda`
- speakers and sponsors, including photo and logo uploads: `/admin/speakers`, `/admin/sponsors`

Uploaded images are stored in the database (`images` table) and served at `/media/<id>`, so changing a photo needs no
code push. Speaker photos are cropped to a 400×400 square; logos keep their shape (SVG is kept as-is).
`sync_prod_from_dev.py` copies them to prod with the rest of the content. Speaker photos and sponsor logos are not
kept in `app/assets/`.

## Deployment

Pushing a branch triggers its GitHub Actions workflow, which builds the Docker image and deploys to Cloud Run:

| Branch | Workflow | Service |
|---|---|---|
| `dev_2026` | `.github/workflows/deploy-dev.yml` | `dev-mascyp-conference-webapp` |
| `production` | `.github/workflows/deploy-prod.yml` | `GCP_RUN_NAME` secret (`mas-cyp-con-2024`) |

Both deploy with `--timeout=3600 --concurrency=500` so live Q&A streams can stay open.

Required GitHub secrets: `GCP_SA_KEY`, `GCP_PROJECT_ID`, `GCP_REGION`, `GCP_RUN_NAME`,
`DATABASE_URL_DEV`, `DATABASE_URL_PROD`, `SESSION_SECRET_DEV`, `SESSION_SECRET_PROD`.
Secret values are plain text (no quotes). Generate session secrets with:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Custom domains are Cloud Run domain mappings (Cloud Console → Cloud Run → Manage custom domains): `mascyp.org`
and `app.mascyp.org` → prod, `test.mascyp.org` → dev. DNS is managed at Porkbun (Google A/AAAA records). `www` is a
Porkbun URL forward (301, include path) to `https://mascyp.org`; the `*` CNAME to `pixie.porkbun.com` is part of
that forwarding, so keep it.

## How live Q&A works

1. A route changes data, then calls `live.publish(...)` → Postgres `NOTIFY` with a tiny JSON payload (ids only).
2. Each app instance with viewers holds one `LISTEN` connection, renders the changed card **once**, and pushes it
   over SSE to its connected phones (`utils/live/`).
3. The browser script (`assets/qa-live.js`) inserts, replaces or removes only that card, keeps the visitor's
   tab and like state, reconnects automatically and re-syncs after any gap.

Guests never receive unapproved questions; the moderator stream requires login.

## Main routes

| Route | Description |
|---|---|
| `/` · `/about` · `/agenda` · `/session/{id}` | Home, about, agenda, session details |
| `/speakers` · `/sponsors` · `/prayer-times` | Speakers, sponsors, prayer times |
| `/qa` · `/qa/event/{id}` | Q&A sessions and a session's questions |
| `/qa/event/{id}/stream` | Live updates (SSE) |
| `/feedback` · `/feedback/edit` | Feedback survey |
| `/registration` | Redirects to the Ticket Tailor event |
| `/media/{id}` | Uploaded speaker photos and sponsor logos |
| `/qa_soon` | Preview of the closed Q&A page (dev only; 404 on production) |
| `/admin_login` · `/admin_dashboard` | Moderator login and dashboard (accounts with `expires_at` lose access, and are logged out, at that time) |
| `/admin/agenda` | Agenda editor (admins) |
| `/admin/speakers` · `/admin/sponsors` | Speaker and sponsor editor with image uploads (admins) |
| `/qa/moderator` | Q&A moderation (moderators) |
| `/feedback/moderator` | Feedback submission count (moderators) |

## Load testing Q&A

```bash
cd app
uv run --with aiohttp python tests/test_sse_load.py --num-users 10 --event-id 1 -u <moderator> -p <password>
```
Simulates users submitting and liking questions while a moderator approves them. Run against dev only.
