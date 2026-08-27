# GrowthOS — Implementation Plan

This plan divides MVP implementation into small, sequential phases. Each phase is scoped so an AI coding agent can implement it without touching unrelated modules. Refer to `DatabaseSchemas.md`, `APIContracts.md`, and `AIArchitecture.md` for the detailed specs each phase implements.

---

## Phase 0 — Project Setup

**Objective:** Establish the repository skeleton and tooling for both backend and frontend.

**Files/modules involved:** repo root, `backend/`, `frontend/`, `.gitignore`, `docker-compose.yml` (optional).

**Dependencies:** none.

**Tasks:**
- Create the folder structure defined in `FolderStructure.md`.
- Initialize FastAPI project (`backend/requirements.txt`: fastapi, uvicorn, pydantic, supabase, python-dotenv, google-genai or equivalent Gemini SDK).
- Initialize Next.js project (`frontend/package.json`).
- Add `.env.example` files for both backend and frontend listing required variables (see `README.md`).

**Testing requirements:** backend boots (`uvicorn app.main:app`) and returns a health-check response; frontend boots (`npm run dev`) and renders a placeholder page.

**Completion criteria:** both apps run locally with no errors, empty but structured.

---

## Phase 1 — Supabase Database and Authentication

**Objective:** Stand up Supabase project, create all MVP tables, enable RLS, and wire up Supabase Auth.

**Files/modules involved:** `backend/migrations/`, `backend/app/database/client.py`, `backend/app/core/security.py`, `frontend/lib/supabaseClient.ts`.

**Dependencies:** Phase 0.

**Tasks:**
- Write SQL migrations for all tables in `DatabaseSchemas.md`.
- Enable Row-Level Security policies scoping each table to `user_id = auth.uid()` (or the appropriate join for child tables).
- Implement `database/client.py` to initialize the Supabase Python client using service credentials.
- Implement `core/security.py` to verify incoming Supabase JWTs and extract `user_id`.
- Wire up the frontend Supabase Auth client for register/login/logout/session handling.

**Testing requirements:** manual registration/login via frontend creates a row visible in Supabase's `auth.users`; a signed-in request to a protected test endpoint resolves the correct `user_id`.

**Completion criteria:** a user can register and log in, and the backend can verify their identity on a request.

---

## Phase 2 — FastAPI Foundation

**Objective:** Set up routing, dependency injection, error handling, and the `/users/me` profile endpoints.

**Files/modules involved:** `app/main.py`, `app/api/router.py`, `app/api/v1/auth.py`, `app/api/v1/users.py`, `app/dependencies.py`, `app/core/exceptions.py`, `app/schemas/user.py`, `app/repositories/user_repository.py`, `app/services/auth_service.py`.

**Dependencies:** Phase 1.

**Tasks:**
- Implement `get_current_user` dependency using `core/security.py`.
- Implement `GET /users/me` and `PUT /users/me` per `APIContracts.md` Module 1.
- Implement global exception handlers for validation and auth errors.

**Testing requirements:** `test_auth.py` covers: unauthenticated request is rejected; authenticated request returns the correct profile; profile update persists.

**Completion criteria:** profile endpoints work end-to-end against Supabase.

---

## Phase 3 — Activity CRUD

**Objective:** Implement Activities as the source-of-truth table, without AI processing yet (status stays `Pending`/manually settable for now).

**Files/modules involved:** `app/api/v1/activities.py`, `app/schemas/activity.py`, `app/repositories/activity_repository.py`, `app/services/activity_service.py`.

**Dependencies:** Phase 2.

**Tasks:**
- Implement all five Activity endpoints from `APIContracts.md` Module 3 (create, list with pagination/filters, get, update, delete).
- New activities are created with `status = "Pending"`.

**Testing requirements:** `test_activity.py` covers create/list/get/update/delete, and that activities are scoped to the requesting user only.

**Completion criteria:** full Activity CRUD works and is properly user-scoped.

---

## Phase 4 — AI GrowthRecord Pipeline

**Objective:** Implement the Activity → GrowthRecord AI extraction pipeline.

**Files/modules involved:** `app/ai/gemini_client.py`, `app/ai/prompts/activity_prompt.py`, `app/schemas/growth_record.py`, `app/processing/activity_processor.py`, `app/api/v1/growth_records.py`.

**Dependencies:** Phase 3.

**Tasks:**
- Implement `gemini_client.py` with a generic "structured completion" method.
- Implement `activity_prompt.py` to build the extraction prompt.
- Implement the `GrowthRecordExtraction` Pydantic schema (see `AIArchitecture.md`).
- Implement `activity_processor.py`: calls AI, validates output, creates `GrowthRecord`, updates `Activity.status`.
- Wire `POST /activities` to trigger processing (synchronously for MVP simplicity).
- Implement `GET /growth-records/{activityId}` and `POST /growth-records/{activityId}/reprocess`.
- Implement failure handling: on error, set `Activity.status = "Failed"` and preserve `raw_content`.

**Testing requirements:** `test_activity.py` (extended) or a new test covering: successful extraction creates a GrowthRecord; a simulated AI failure sets status to Failed and reprocess retries successfully.

**Completion criteria:** creating an Activity results in a GrowthRecord being created (or a recoverable Failed state).

---

## Phase 5 — Skills and Evidence

**Objective:** Implement skill upsert logic driven by the extraction pipeline, plus read endpoints.

**Files/modules involved:** `app/processing/skill_engine.py`, `app/schemas/skill.py`, `app/repositories/skill_repository.py`, `app/services/skill_service.py`, `app/api/v1/skills.py`.

**Dependencies:** Phase 4.

**Tasks:**
- Implement `skill_engine.py`: for each `ExtractedSkill` in a `GrowthRecordExtraction`, upsert into `skills` (create or update confidence/`last_used`) and create a `skill_evidence` row.
- Hook `skill_engine.py` into `activity_processor.py` from Phase 4.
- Implement `GET /skills`, `GET /skills/{id}`, `GET /skills/{id}/evidence` per `APIContracts.md` Module 5.

**Testing requirements:** `test_skills.py` covers: new skill creation, confidence update on repeated evidence, evidence list returns correct linked activities.

**Completion criteria:** skills accumulate correctly across multiple activities and are queryable with their evidence.

---

## Phase 6 — Projects and Timeline

**Objective:** Implement Project CRUD, activity linking, and the Timeline read endpoint.

**Files/modules involved:** `app/schemas/project.py`, `app/repositories/project_repository.py`, `app/services/project_service.py`, `app/api/v1/projects.py`, `app/services/timeline_service.py`, `app/api/v1/timeline.py`.

**Dependencies:** Phase 5.

**Tasks:**
- Implement all Project endpoints from `APIContracts.md` Module 6, including linking an Activity to a Project.
- Implement `GET /timeline` combining Activities + their GrowthRecords, sorted by date, with optional date-range filtering.

**Testing requirements:** `test_projects.py` covers CRUD + linking; timeline query returns correctly ordered/filtered results.

**Completion criteria:** projects can be created and populated with linked activities; timeline reflects real data correctly ordered.

---

## Phase 7 — Goals

**Objective:** Implement Goals and Reflections.

**Files/modules involved:** `app/schemas/goal.py`, `app/repositories/goal_repository.py`, `app/services/goal_service.py`, `app/api/v1/goals.py`.

**Dependencies:** Phase 2 (independent of Activities/AI pipeline).

**Tasks:**
- Implement all Goal endpoints from `APIContracts.md` Module 7 (create, list, update, complete, add reflection).

**Testing requirements:** `test_goals.py` covers create/list/update/complete and reflection creation, including that completing a goal without a reflection is still valid.

**Completion criteria:** full goal lifecycle works end-to-end.

---

## Phase 8 — Analytics Dashboard

**Objective:** Implement dashboard summary and analytics endpoints, computed from existing data (no AI).

**Files/modules involved:** `app/schemas/analytics.py`, `app/services/analytics_service.py`, `app/api/v1/analytics.py`.

**Dependencies:** Phases 3–7 (reads Activities, Skills, Goals, GrowthRecords).

**Tasks:**
- Implement `GET /dashboard`, `GET /analytics`, `GET /analytics/skills`, `GET /analytics/productivity` per `APIContracts.md` Module 9.
- All calculations (streaks, weekly progress, skill growth history) are plain backend logic — no AI calls.

**Testing requirements:** unit tests with seeded data verifying streak calculation, weekly aggregation, and skill growth history shape.

**Completion criteria:** dashboard and analytics endpoints return correct, well-shaped data for a seeded test user.

---

## Phase 9 — GitHub Integration

**Objective:** Implement manual GitHub connect/sync, converting GitHub metadata into Activities.

**Files/modules involved:** `app/integrations/github.py`, `app/services/integration_service.py`, `app/repositories/connected_account_repository.py`, `app/api/v1/integrations.py`.

**Dependencies:** Phase 4 (created activities must flow through the AI pipeline).

**Tasks:**
- Implement GitHub OAuth connect flow (`POST /integrations/github/connect`), storing encrypted tokens in `connected_accounts`.
- Implement `POST /integrations/github/sync`: call GitHub API for repositories, languages, and recent commit activity; create one `github_commit` Activity per meaningful unit of activity; update `last_synced`.
- Implement `GET /integrations`.
- Ensure created Activities are passed through the Phase 4 pipeline (same code path as manual activities).

**Testing requirements:** mock GitHub API responses; verify Activities are created correctly and `last_synced` updates; verify sync is idempotent (doesn't duplicate the same commit activity on repeated syncs).

**Completion criteria:** a connected GitHub account can be manually synced and produces processed Activities.

---

## Phase 10 — Weekly Reports

**Objective:** Implement AI-generated weekly reports.

**Files/modules involved:** `app/ai/prompts/report_prompt.py`, `app/schemas/report.py`, `app/processing/report_engine.py`, `app/repositories/report_repository.py`, `app/api/v1/reports.py`.

**Dependencies:** Phases 4–8 (reports summarize Activities, GrowthRecords, Skills, Goals).

**Tasks:**
- Implement `WeeklyReport` Pydantic schema (see `AIArchitecture.md`).
- Implement `report_engine.py`: gather the week's data, call Gemini, validate, store.
- Implement `POST /reports/generate`, `GET /reports`, `GET /reports/{id}`.

**Testing requirements:** `test_reports.py` with a mocked Gemini response verifying the report is generated and stored correctly for a given period.

**Completion criteria:** a user can generate and retrieve a weekly report reflecting their real activity for that week.

---

## Phase 11 — Resume Generation

**Objective:** Implement AI-generated evidence-backed resumes.

**Files/modules involved:** `app/ai/prompts/resume_prompt.py`, `app/schemas/resume.py`, `app/processing/resume_engine.py`, `app/repositories/resume_repository.py`, `app/api/v1/resume.py`.

**Dependencies:** Phases 5–6 (resumes draw on Skills, SkillEvidence, Projects).

**Tasks:**
- Implement `ResumeDocument` Pydantic schema (see `AIArchitecture.md`).
- Implement `resume_engine.py`: gather relevant evidence, call Gemini, validate, store.
- Implement `POST /resume/generate`, `GET /resume/history`, `GET /resume/{id}`.

**Testing requirements:** `test_resume.py` with a mocked Gemini response verifying the resume references real evidence (activity/project IDs that exist for the test user).

**Completion criteria:** a user can generate a resume and see it cite specific real activities/projects.

---

## Phase 12 — Frontend Integration

**Objective:** Build the Next.js UI on top of the completed backend API.

**Files/modules involved:** `frontend/app/**`, `frontend/components/**`, `frontend/lib/api.ts`.

**Dependencies:** Phases 1–11 (all backend endpoints must exist).

**Tasks:**
- Build auth pages (login/register) using Supabase Auth client.
- Build activity capture UI, timeline view, skills view, projects view, goals view, analytics dashboard, reports view, resume view — one page group per backend module.
- Implement `lib/api.ts` as a typed client wrapping all backend endpoints, attaching the Supabase JWT to every request.

**Testing requirements:** manual end-to-end walkthrough of each user journey in `PRD.md` Section 7; basic component tests for critical forms (activity capture, goal creation).

**Completion criteria:** every MVP feature is usable end-to-end through the UI.

---

## Phase 13 — Testing

**Objective:** Fill testing gaps and add integration-level coverage across modules.

**Files/modules involved:** `backend/tests/**`.

**Dependencies:** Phases 1–12.

**Tasks:**
- Ensure every endpoint in `APIContracts.md` has at least one passing test.
- Add an integration test that walks the full core loop: create Activity → GrowthRecord created → Skill updated → appears in Timeline and Dashboard.

**Testing requirements:** this phase *is* the testing work — target meaningful coverage of services and API routes, not just happy paths (include auth failures, not-found cases, and validation errors).

**Completion criteria:** test suite passes and covers all MVP modules.

---

## Phase 14 — Deployment

**Objective:** Deploy backend and frontend for real use.

**Files/modules involved:** deployment configs (Vercel for frontend, any container/host for backend), `.env` management, Supabase production project.

**Dependencies:** Phases 1–13.

**Tasks:**
- Provision a production Supabase project; apply migrations from Phase 1.
- Deploy backend (containerized or platform-hosted) with production environment variables (Gemini key, GitHub OAuth credentials, Supabase service key).
- Deploy frontend (e.g. Vercel) pointing at the production backend URL.
- Verify auth, activity capture, and one full AI-driven flow (e.g. weekly report) work in production.

**Testing requirements:** smoke test each MVP feature against the deployed environment.

**Completion criteria:** GrowthOS MVP is live and fully functional in production.
