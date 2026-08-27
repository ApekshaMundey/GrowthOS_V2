# GrowthOS — Folder Structure

This is a two-package repository: a FastAPI backend and a Next.js frontend. Kept intentionally flat and simple for an MVP.

```
growthos/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point, app startup
│   │   ├── config.py                # Env var loading (Supabase, Gemini, GitHub keys)
│   │   ├── dependencies.py          # Shared FastAPI dependencies (e.g. current_user)
│   │   │
│   │   ├── api/
│   │   │   ├── router.py            # Aggregates all v1 routers
│   │   │   └── v1/
│   │   │       ├── auth.py          # Session/profile endpoints (Supabase Auth-backed)
│   │   │       ├── users.py         # Get/update profile
│   │   │       ├── activities.py    # Activity CRUD
│   │   │       ├── growth_records.py# Get/reprocess GrowthRecords
│   │   │       ├── skills.py        # Skills + evidence read endpoints
│   │   │       ├── projects.py      # Project CRUD + activity linking
│   │   │       ├── goals.py         # Goal CRUD + reflections
│   │   │       ├── timeline.py      # Timeline read endpoint
│   │   │       ├── analytics.py     # Dashboard + analytics endpoints
│   │   │       ├── reports.py       # Weekly report generation/read
│   │   │       ├── resume.py        # Resume generation/read
│   │   │       └── integrations.py  # GitHub connect/sync/list
│   │   │
│   │   ├── core/
│   │   │   ├── security.py          # Supabase JWT verification
│   │   │   ├── logging.py           # App-wide logging setup
│   │   │   ├── constants.py         # Enums, shared constants
│   │   │   └── exceptions.py        # Custom exception classes + handlers
│   │   │
│   │   ├── database/
│   │   │   └── client.py            # Supabase client initialization
│   │   │
│   │   ├── schemas/                 # Pydantic request/response + AI output schemas
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── activity.py
│   │   │   ├── growth_record.py
│   │   │   ├── skill.py
│   │   │   ├── project.py
│   │   │   ├── goal.py
│   │   │   ├── report.py
│   │   │   ├── resume.py
│   │   │   ├── analytics.py
│   │   │   └── connected_account.py  # Schemas for GitHub connect/sync (connected_accounts table)
│   │   │
│   │   ├── services/                # Business logic, one file per domain
│   │   │   ├── auth_service.py
│   │   │   ├── activity_service.py
│   │   │   ├── skill_service.py
│   │   │   ├── project_service.py
│   │   │   ├── goal_service.py
│   │   │   ├── report_service.py
│   │   │   ├── resume_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── timeline_service.py
│   │   │   └── integration_service.py  # GitHub connect/sync orchestration
│   │   │
│   │   ├── processing/               # AI-orchestration pipeline (calls ai/ + services/)
│   │   │   ├── activity_processor.py # Activity → GrowthRecord pipeline
│   │   │   ├── skill_engine.py       # Skill extraction/confidence updates
│   │   │   ├── report_engine.py      # Weekly report generation
│   │   │   └── resume_engine.py      # Resume generation
│   │   │
│   │   ├── ai/
│   │   │   ├── gemini_client.py      # Thin wrapper around Gemini API calls
│   │   │   └── prompts/
│   │   │       ├── activity_prompt.py
│   │   │       ├── skill_prompt.py
│   │   │       ├── report_prompt.py
│   │   │       └── resume_prompt.py
│   │   │
│   │   ├── integrations/
│   │   │   └── github.py             # GitHub API calls (repos, languages, commits)
│   │   │
│   │   ├── repositories/             # Supabase query functions, one per table group
│   │   │   ├── user_repository.py
│   │   │   ├── activity_repository.py
│   │   │   ├── skill_repository.py
│   │   │   ├── project_repository.py
│   │   │   ├── goal_repository.py
│   │   │   ├── report_repository.py
│   │   │   ├── resume_repository.py
│   │   │   └── connected_account_repository.py
│   │   │
│   │   └── utils/
│   │       └── date_utils.py         # Shared date/timezone helpers
│   │
│   ├── migrations/                   # SQL migration files for Supabase Postgres
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_activity.py
│   │   ├── test_skills.py
│   │   ├── test_projects.py
│   │   ├── test_goals.py
│   │   ├── test_reports.py
│   │   └── test_resume.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md                     # Backend-specific setup notes (optional, can defer to root README)
│
├── frontend/
│   ├── app/                          # Next.js app router pages
│   │   ├── (auth)/                   # Login/register pages
│   │   ├── dashboard/                # Analytics dashboard
│   │   ├── activities/               # Daily capture + activity list
│   │   ├── timeline/                 # Growth timeline view
│   │   ├── skills/                   # Skills + evidence view
│   │   ├── projects/                 # Projects view
│   │   ├── goals/                    # Goals + reflections view
│   │   ├── reports/                  # Weekly reports view
│   │   └── resume/                   # Resume generation/view
│   ├── components/                   # Shared UI components
│   ├── lib/
│   │   ├── api.ts                    # Backend API client
│   │   └── supabaseClient.ts         # Supabase Auth client (frontend)
│   ├── .env.example
│   └── package.json
│
├── docs/                             # This set of specification documents
│   ├── PRD.md
│   ├── Architecture.md
│   ├── FolderStructure.md
│   ├── DatabaseSchemas.md
│   ├── APIContracts.md
│   ├── AIArchitecture.md
│   ├── ImplementationPlan.md
│   └── README.md
│
├── .gitignore
└── docker-compose.yml (optional, for local Postgres if not using hosted Supabase during dev)
```

Notes:
- No SQLAlchemy models or ORM layer — the backend talks to Supabase Postgres via the Supabase Python client, so `repositories/` contains query functions rather than ORM model classes.
- No `background/` or `middleware/rate_limit.py` — not required for MVP; add later if needed.
- No `utils/pdf_generator.py` or `utils/ats_scorer.py` — those features are out of MVP scope.
- No `integrations/leetcode.py`, `duolingo.py`, or `calendar.py` — GitHub is the only MVP integration.
