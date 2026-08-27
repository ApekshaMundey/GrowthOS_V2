# GrowthOS — Architecture

## 1. Overview

GrowthOS is a deterministic backend application with a thin AI processing layer — **not** a multi-agent system. Normal backend code handles auth, CRUD, timelines, analytics, and GitHub sync. AI is invoked only for reasoning tasks: extraction, summarization, and generation.

## 2. High-Level System Architecture

```
┌────────────────────┐        HTTPS/JSON        ┌─────────────────────────┐
│   Frontend (Next.js) │ ───────────────────────▶ │   Backend (FastAPI)      │
│   React UI (v0)       │ ◀─────────────────────── │   Pydantic validation    │
└────────────────────┘                            └───────────┬─────────────┘
                                                                │
                              ┌─────────────────────────────────┼───────────────────────────┐
                              │                                 │                             │
                     ┌────────▼────────┐             ┌──────────▼─────────┐         ┌─────────▼────────┐
                     │ Supabase Auth    │             │ Supabase PostgreSQL │         │  AI Layer (Gemini) │
                     │ (JWT sessions)   │             │  (all app data)     │         │  structured outputs │
                     └──────────────────┘             └──────────┬──────────┘         └─────────┬──────────┘
                                                                   │                              │
                                                          ┌────────▼────────┐                     │
                                                          │  GitHub API      │◀────────────────────┘
                                                          │ (manual sync)    │        (AI reasons over
                                                          └──────────────────┘         synced metadata too)
```

## 3. Component Boundaries

| Layer | Responsibility | Technology |
|---|---|---|
| Frontend | UI, forms, dashboards, calling backend API | Next.js / React |
| Backend | Auth verification, CRUD, routing, business logic, orchestrating AI calls | FastAPI, Python, Pydantic |
| Database | Persistent storage of all structured data | Supabase PostgreSQL |
| Auth | User identity, sessions, tokens | Supabase Auth |
| AI Layer | Extraction, summarization, report/resume generation | Gemini API + Pydantic schemas |
| External Integration | Read-only metadata retrieval | GitHub API |

The backend is the only component that talks to the database, the AI layer, and GitHub. The frontend never calls Supabase or Gemini directly except for Supabase Auth's client-side session handling.

## 4. Authentication Flow

```
User → Frontend (login form) → Supabase Auth → JWT issued
Frontend stores session → attaches JWT as Bearer token on every API request
FastAPI middleware verifies JWT with Supabase → extracts user_id → injects into request context
```

- Registration, login, logout, and token refresh are handled by Supabase Auth directly from the frontend SDK.
- FastAPI does not implement its own password/JWT logic — it verifies Supabase-issued JWTs on incoming requests.
- Every backend query is scoped to the authenticated `user_id`.

## 5. Activity Processing Flow (Core Loop)

```
1. User submits an Activity (free text, link, or GitHub-sourced metadata)
2. Backend: validates input → creates Activity row (status = Pending)
3. Backend: calls AI layer with the raw Activity content
4. AI layer: extracts structured GrowthRecord (summary, skills, insights, confidence)
5. Backend: writes GrowthRecord row (linked 1:1 to Activity) → Activity status = Completed
6. Backend: upserts/updates Skills (with confidence) and SkillEvidence rows
7. Timeline and Analytics read from Activities + GrowthRecords + Skills — no extra AI calls needed
```

If AI extraction fails, the Activity is marked `Failed` and the raw content is preserved so it can be reprocessed later (see `AIArchitecture.md` for fallback behavior).

## 6. Growth Memory Flow

Growth Memory is not a separate service — it is the **accumulated state** of Activities, GrowthRecords, Skills, SkillEvidence, and Projects in the database. It updates incrementally as each Activity is processed:

```
New GrowthRecord created
   → Skills table updated (new skill or confidence/last_used refreshed)
   → SkillEvidence row created (linking skill → activity)
   → Project linkage updated if the activity references a project
```

## 7. GitHub Synchronization Flow (MVP: manual, on-demand)

```
1. User connects GitHub (OAuth) → ConnectedAccounts row stores encrypted access token
2. User clicks "Sync" → Backend calls GitHub API:
   - list repositories
   - detect primary languages
   - pull recent commit activity metadata
3. Backend creates one Activity per meaningful unit of GitHub activity (activity_type = github_commit, source = GitHub)
4. Each created Activity flows through the standard Activity Processing Flow above
5. ConnectedAccounts.last_synced is updated
```

No webhooks and no background workers are used in the MVP — sync is triggered explicitly by the user from the UI.

## 8. Weekly Report Flow

```
User (or scheduled trigger) requests a weekly report
   → Backend gathers the week's Activities + GrowthRecords + Skill deltas
   → Backend sends this structured context to the AI layer
   → AI generates a narrative summary + highlights (Pydantic-validated JSON)
   → Backend stores the result in Reports (type = Weekly)
   → Frontend renders the report
```

## 9. Resume Generation Flow

```
User requests a resume (optionally with a target role/template)
   → Backend gathers relevant Projects, Skills, SkillEvidence, and GrowthRecords
   → Backend sends this evidence bundle to the AI layer
   → AI generates a structured resume (Pydantic-validated JSON), citing evidence per bullet
   → Backend stores result in ResumeVersions
   → Frontend renders the resume; no PDF export in MVP
```

## 10. Data Flow Summary

- **Write path:** Frontend → FastAPI → (Supabase Postgres and/or Gemini) → Postgres.
- **Read path:** Frontend → FastAPI → Postgres (Timeline, Analytics, Skills, Projects, Goals all read directly from stored, already-processed data — no AI calls on read).
- **AI is only invoked on the write path**, at well-defined points: activity extraction, weekly report generation, resume generation.

## 11. Deployment Notes

- Backend: FastAPI app, deployable as a single service (no separate worker processes required for MVP).
- Database & Auth: fully managed by Supabase.
- Frontend: Next.js app, deployable independently (e.g. Vercel).
- Secrets (Gemini API key, GitHub OAuth credentials, Supabase service key) live in backend environment variables only — never exposed to the frontend.
