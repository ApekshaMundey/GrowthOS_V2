# GrowthOS

Transform your daily efforts into measurable growth.

GrowthOS is an AI-powered personal growth platform that automatically captures a user's daily work, organizes it into a structured Growth Memory, and generates insights: progress analytics, learning timelines, and evidence-backed resumes.

Full product and engineering specs live in `/docs`:
- `PRD.md` — product requirements
- `Architecture.md` — system architecture and data flows
- `FolderStructure.md` — repository layout
- `DatabaseSchemas.md` — Supabase Postgres schema
- `APIContracts.md` — REST API reference
- `AIArchitecture.md` — AI pipeline design
- `ImplementationPlan.md` — phased build plan

## Architecture Summary

GrowthOS is a deterministic FastAPI backend with a focused AI layer (Gemini) for extraction and generation tasks — not a multi-agent system. Frontend is Next.js. Data and auth are fully managed by Supabase.

```
Next.js frontend → FastAPI backend → Supabase Postgres
                                   → Supabase Auth
                                   → Gemini API (AI extraction/generation)
                                   → GitHub API (manual sync)
```

## Core Flow

```
User logs an activity
   → FastAPI creates Activity
   → Gemini extracts structured GrowthRecord
   → Skills + Evidence are updated
   → Growth Memory is persisted
   → Timeline / Analytics / Reports / Resume
```

This flow runs synchronously per `APIContracts.md` and `AIArchitecture.md` — see those documents for the full request/response contract.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js / React |
| Backend | FastAPI, Python, Pydantic |
| Database | Supabase PostgreSQL |
| Auth | Supabase Auth |
| AI | Gemini API (structured outputs via Pydantic) |
| External Integration | GitHub API (manual/read-only sync) |

## Repository Structure

```
growthos/
├── backend/       # FastAPI app
├── frontend/       # Next.js app
└── docs/          # Specification documents (this set)
```

See `FolderStructure.md` for the full breakdown.

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Supabase project (free tier is fine for development)
- A Gemini API key
- A GitHub OAuth App (for the GitHub integration)

### Clone and install

```bash
git clone <repo-url>
cd growthos

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Environment Variables

> **Security warning:** server-side secrets — `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY`, and `GITHUB_CLIENT_SECRET` — must never be committed to Git and must never be exposed to the frontend. They belong only in `backend/.env`.

### backend/.env

```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
GEMINI_API_KEY=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

### frontend/.env.local

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## Running the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

## Running the Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Running Tests

```bash
cd backend
pytest
```

## MVP Feature List

1. User Authentication
2. Daily Activity Capture
3. AI Extraction into structured GrowthRecords
4. Persistent Growth Memory
5. Skills
6. Skill Evidence
7. Projects
8. Goals and Reflections
9. Growth Timeline
10. Analytics Dashboard
11. Weekly AI Growth Report
12. Evidence-Backed Resume Generation
13. GitHub Integration (manual sync)

See `PRD.md` for full detail, including explicit MVP exclusions and future enhancements.
