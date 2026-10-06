# MAS Dallas CYP Conference App

Mobile-first web app for the MAS Dallas College & Young Professionals (CYP) conference — agenda,
speakers, live Q&A and feedback. Built with FastHTML + HTMX, PostgreSQL (Neon), deployed on Google Cloud Run.

Current edition: **4th Annual CYP Conference — Him & Her: Building Success at Every Stage**
(Saturday, Oct 24, 2026, GEM Academy & Facility, Plano).

## Environments

| | Production | Development |
|---|---|---|
| URL | https://app.mascyp.org | dev.mascyp.org (mapping in progress) |
| Branch | `production` | `dev_2026` |
| Cloud Run service (us-west1) | `mas-cyp-con-2024` | `dev-mascyp-conference-webapp` |
| Database (Neon) | production branch | development branch |
| Currently serves | Coming Soon page only | Full 2026 app |

The 2025 conference data is kept in the `archive_2025` Neon database. Workflow: changes are built and tested on
`dev_2026` (auto-deploys to dev), then merged to `production` when ready.

## Features

- **Home & theme** — "Him & Her" parchment/navy look shared by every page (`assets/theme-26.css`).
- **Agenda** — timeline of sessions with **tag filter pills** (Masculinity, Womanhood, Talk, Workshop, Prayer…).
  All pills start selected; the first click narrows to that tag, further clicks add or remove tags.
  Sessions tagged **All** ("Everyone": keynotes, prayers, breaks) always stay visible.
- **Agenda editor** (moderators, `/admin/agenda`) — click any field on a session card to edit it in place:
  times, title, location, tags, speakers (with "Add new speaker"), description (pop-up editor).
- **Live Q&A** — guests submit questions; moderators approve, hide, mark answered or delete. Updates appear
  instantly for everyone without reloading (only the changed card or count is sent). Likes are one per visitor.
- **Feedback survey** — one submission per visitor, editable later.
- **Speakers, sponsors, prayer times, about** pages.
- **Coming Soon** page (`/coming-soon`) used by production until launch.

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
│   ├── conference.py        # Conference dates and date-window settings
│   ├── static.py            # Loads every assets/*.css|*.js on all pages (sorted)
│   └── visitor.py           # Anonymous visitor cookie (likes, feedback)
├── routes/                  # Pages and endpoints
│   ├── main.py              # Home, about, prayer times, registration, coming soon
│   ├── session.py           # Agenda + session details
│   ├── agenda_admin.py      # Agenda editor, add speaker
│   ├── qa.py                # Q&A (guest + moderator) and live stream
│   ├── feedback.py          # Feedback survey
│   ├── speaker.py, sponsor.py
│   └── admin.py             # Login/logout, admin dashboard
├── components/              # UI components (home, theme, timeline, qa, cards, feedback…)
├── crud/                    # Database operations
├── db/                      # Models, schemas, connection
├── utils/
│   ├── auth.py              # Passwords, @require_moderator, date-window decorators
│   ├── live/                # Live Q&A: hub (local subscribers), bus (Postgres NOTIFY), render
│   ├── tags.py              # Session tag rules
│   └── speaker_utils.py     # Placeholder avatars
├── assets/                  # CSS, JS (qa-live.js, agenda-filter.js), images
├── load_2026_program.py     # Creates tables + loads the 2026 program
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
| `RESTRICT_TO_CONFERENCE_DAY` | `true` limits Q&A to conference day and feedback to conference day + 7 days. Off by default. Dates live in `core/conference.py`. |

## Database

Run these from `app/` (with Docker: `docker exec -it mas_cyp_con_2024-app-1 uv run python <script>`).
Every script prints the target database and does a dry run unless `--apply` is given.

| Task | Command |
|---|---|
| Set up a new database (tables + 2026 program) | `python load_2026_program.py --apply` |
| Convert an older database's categories to tags | `python migrate_event_tags.py --apply` |
| Create a moderator/admin account | `python create_admin.py` |
| Reset a password | `python reset_admin_password.py` |

Day-to-day content (sessions, speakers, tags, descriptions) is edited in the app at `/admin/agenda`.

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

Custom domains are Cloud Run domain mappings (Cloud Console → Cloud Run → Manage custom domains); DNS for
`mascyp.org` is managed at Porkbun (`CNAME <subdomain> → ghs.googlehosted.com`).

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
| `/admin_login` · `/admin_dashboard` | Moderator login and dashboard |
| `/admin/agenda` | Agenda editor (moderators) |
| `/qa/moderator` | Q&A moderation (moderators) |
| `/feedback/moderator` | Feedback submission count (moderators) |

## Load testing Q&A

```bash
cd app
uv run --with aiohttp python tests/test_sse_load.py --num-users 10 --event-id 1 -u <moderator> -p <password>
```
Simulates users submitting and liking questions while a moderator approves them. Run against dev only.
