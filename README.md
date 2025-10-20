Conference Management App
A practical conference web application built with FastHTML, providing essential features for managing and engaging conference attendees.

*Features*
1. Agenda & Sessions
- View complete conference schedule with session times and locations
- Session details including descriptions and speaker information
- Speaker profiles with biographical information
- Interactive timeline view of events
2. Speakers
- Browse all conference speakers
- Detailed speaker profiles with images and bios
- Links to speakers' sessions
3. Feedback Survey
- Comprehensive post-conference feedback form
- Submit and edit feedback submissions
- Moderator dashboard to view submission counts
4. Interactive Q&A Sessions
- Real-time question submission for conference sessions
- Like/upvote questions
- Live updates via Server-Sent Events (SSE)
- Sort questions by popularity or recency

*Tech Stack*
- Framework: FastHTML - Modern Python web framework
- Database: PostgreSQL (via SQLAlchemy with async support)
- Frontend: HTMX for dynamic interactions, DaisyUI for styling
- Real-time: Server-Sent Events (SSE) for live updates
- Deployment: Google Cloud Run with Docker

*Project Strcuture*
```
app/
├── main.py                 # Application entry point
├── conference_data.json    # Conference data (events, speakers, etc.)
├── assets/                 # Static files (CSS, images)
├── components/             # Reusable UI components
│   ├── cards.py           # Session/speaker cards
│   ├── qa.py              # Q&A components
│   ├── feedback_form.py   # Feedback form
│   └── navigation.py      # Navigation components
├── routes/                 # Route handlers
│   ├── main.py            # Home, about
│   ├── session.py         # Agenda routes
│   ├── speaker.py         # Speaker routes
│   ├── feedback.py        # Feedback routes
│   ├── qa.py              # Q&A routes
│   └── admin.py           # Admin/moderator routes
├── crud/                   # Database operations
│   ├── event.py
│   ├── speaker.py
│   ├── question.py
│   └── feedback.py
├── db/                     # Database models and schemas
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   └── connection.py      # Database connection manager
├── utils/                  # Utility functions
│   ├── auth.py            # Authentication decorators
│   ├── session.py         # Session management
│   └── sse_manager.py     # SSE connection manager
└── tests/                  # Test files
```

Setup & Installation
Prerequisites
Python 3.10+
PostgreSQL database
Docker (for containerized deployment)
Environment Variables
Create a `.env` file with the following variables:
```
ENVIRONMENT=development  # or production
PORT=8080
HOST=0.0.0.0
DATABASE_URL=postgresql://user:password@host:port/database
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
```

*Local Development*
1. Install dependencies (using uv):
```uv sync```
2. Initialize database:
```
# Create tables
python app/migrate_qa.py
python app/migrate_feedback.py

# Load conference data
python app/sync_data.py
```

3. Run the application:
```
cd app
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

4. Access the app:
- Main site: http://localhost:8080
- Admin login: http://localhost:8080/admin/login

*Docker Development*
```docker-compose -f docker-compose.dev.yml up```
This mounts your local `app` directory for live reloading.

*Deployment*
Google Cloud Run
The project includes GitHub Actions workflows for automatic deployment:
- Development: Push to dev_2025 branch
- Production: Push to production branch

Required GitHub Secrets:
`GCP_SA_KEY`: Service account JSON key
`GCP_PROJECT_ID`: Google Cloud project ID
`GCP_REGION`: Deployment region (e.g., us-central1)
`GCP_RUN_NAME`: Cloud Run service name
`DATABASE_URL_DEV`: Development database URL
`DATABASE_URL_PROD`: Production database URL

*Manual Deployment*
```
# Build Docker image
docker build -t gcr.io/PROJECT_ID/conference-app:latest .

# Push to Google Container Registry
docker push gcr.io/PROJECT_ID/conference-app:latest

# Deploy to Cloud Run
gcloud run deploy conference-app \
  --image gcr.io/PROJECT_ID/conference-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=$DATABASE_URL"
```

*Database Migrations*
`migrate_qa.py` - Creates Q&A tables (questions, likes)
`migrate_feedback.py` - Creates feedback submission table
`add_qa_activation.py` - Adds Q&A activation fields to events
`sync_data.py` - Syncs conference data from JSON file

Data Management
Conference data is managed via `conference_data.json`:
```
{
  "events": [...],
  "speakers": [...],
  "event_speakers": [...],
  "prayer_times": [...]
}
```

To update the database with new data:
```python app/sync_data.py```

*Testing*
Load Testing Q&A System
```
# Test with 10 simulated users
python app/tests/test_sse_load.py --num-users 10 --event-id 1

# With custom moderator credentials
python app/tests/test_sse_load.py -n 10 -e 1 -u admin -p password
```
This simulates:
- Users submitting questions
- Users liking questions
- Moderator approving/hiding questions
- SSE real-time updates


*Key Components*
Authentication & Authorization:
- Session-based authentication for moderators
- Decorators: `@require_moderator`, `@require_conference_day`
Role-based access control
Real-time Updates:
- SSE for live Q&A updates
- Automatic refresh when questions are submitted/approved
- Connection pooling and keepalive pings
Database
- Async SQLAlchemy with PostgreSQL
- Connection pooling for performance
- Automatic session management


*API Endpoints*
Public Routes
`GET /` - Home page
`GET /agenda` - Conference schedule
`GET /speakers` - Speaker list
`GET /feedback` - Feedback form
`GET /qa` - Q&A sessions list
Q&A Routes
`GET /qa/event/{event_id}` - Q&A page for event
`POST /qa/event/{event_id}/submit` - Submit question
`POST /qa/question/{question_id}/like` - Like question
`GET /qa/event/{event_id}/stream` - SSE stream
Moderator Routes (Auth Required)
`GET /qa/moderator` - Moderator dashboard
`POST /qa/moderator/event/{event_id}/toggle-qa` - Activate/deactivate Q&A
`POST /qa/moderator/question/{question_id}/toggle-visibility` - Show/hide question
`POST /qa/moderator/question/{question_id}/toggle-answered` - Mark as answered
`DELETE /qa/moderator/question/{question_id}` - Delete question

*Configuration*
Conference Day Restriction
By default, the app restricts access to certain features to conference day only. Configure via the `require_conference_day` decorator in `utils/auth.py`.

Session Management
- Session IDs stored in cookies
- Used for tracking feedback submissions and question likes
- Prevents duplicate submissions

Contributing
- Create a feature branch
- Make changes
- Test locally with Docker
- Push to trigger CI/CD pipeline

Built with ❤️ using FastHTML