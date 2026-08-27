# GrowthOS — Database Schemas (Supabase PostgreSQL, MVP)

All tables use `UUID` primary keys (`gen_random_uuid()` default). `users.id` matches the Supabase Auth user id (`auth.users.id`) — there is no separate password column since Supabase Auth owns credentials.

---

## 1. users

Extends Supabase's built-in `auth.users` with app-specific profile data.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, FK → auth.users(id) |
| name | VARCHAR | NOT NULL |
| email | VARCHAR | UNIQUE, NOT NULL |
| profile_image | TEXT | nullable |
| profession | VARCHAR | nullable (e.g. Student, Engineer, Researcher) |
| bio | TEXT | nullable |
| timezone | VARCHAR | NOT NULL, default 'UTC' |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

Relationships: 1:N to Activities, Skills, Projects, Goals, ConnectedAccounts, ResumeVersions, Reports.

---

## 2. activities

The source of truth. Every manual entry or GitHub-derived event becomes an Activity.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL, indexed |
| activity_type | ENUM | NOT NULL — see values below |
| source | ENUM | NOT NULL — see values below |
| title | TEXT | NOT NULL |
| raw_content | TEXT | NOT NULL |
| source_metadata | JSONB | nullable (e.g. repo name, commit sha, language) |
| activity_date | TIMESTAMPTZ | NOT NULL |
| status | ENUM | NOT NULL, default 'Pending' — see values below |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() |

**activity_type** (ENUM): `manual_note`, `project_update`, `github_commit`, `youtube_video`, `meeting_notes`, `research_note`

**source** (ENUM): `Manual`, `GitHub`

**status** (ENUM): `Pending`, `Processing`, `Completed`, `Failed`

Index: `(user_id, activity_date DESC)` — for timeline queries.

---

## 3. growth_records

Structured AI output generated from an Activity. One-to-one with Activities.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| activity_id | UUID | FK → activities(id), UNIQUE, NOT NULL |
| summary | TEXT | NOT NULL |
| insights | JSONB | nullable |
| confidence | FLOAT | NOT NULL, range 0–1 |
| embedding_generated | BOOLEAN | NOT NULL, default false (reserved for future pgvector semantic search) |
| processed_at | TIMESTAMPTZ | NOT NULL, default now() |

---

## 4. skills

Master list of inferred skills per user.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL, indexed |
| skill_name | VARCHAR | NOT NULL |
| category | VARCHAR | nullable |
| confidence | FLOAT | NOT NULL, range 0–1 |
| last_used | DATE | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |

Constraint: UNIQUE `(user_id, skill_name)` — one row per skill per user; confidence and `last_used` are updated as new evidence arrives.

---

## 5. skill_evidence

Links a Skill to the Activity that supports it.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| skill_id | UUID | FK → skills(id), NOT NULL |
| activity_id | UUID | FK → activities(id), NOT NULL |
| confidence | FLOAT | NOT NULL, range 0–1 |
| description | TEXT | nullable |

Index: `(skill_id)` for fetching all evidence for a skill.

---

## 6. projects

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL, indexed |
| name | VARCHAR | NOT NULL |
| description | TEXT | nullable |
| github_repo | TEXT | nullable |
| status | VARCHAR | NOT NULL, default 'active' |
| start_date | DATE | nullable |
| end_date | DATE | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |

---

## 7. project_activities

Many-to-many mapping between Projects and Activities.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK → projects(id), NOT NULL |
| activity_id | UUID | FK → activities(id), NOT NULL |

Constraint: UNIQUE `(project_id, activity_id)`.

---

## 8. goals

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL, indexed |
| title | VARCHAR | NOT NULL |
| description | TEXT | nullable |
| priority | ENUM | NOT NULL — `Low`, `Medium`, `High` |
| target_date | DATE | nullable |
| status | ENUM | NOT NULL, default 'Pending' — `Pending`, `Completed`, `Skipped` |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |

---

## 9. goal_reflections

End-of-day reflection tied to a goal. One-to-one with Goals.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| goal_id | UUID | FK → goals(id), UNIQUE, NOT NULL |
| completed | BOOLEAN | NOT NULL |
| reflection | TEXT | nullable |
| reason | TEXT | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |

---

## 10. connected_accounts

Stores external platform connections. MVP supports only `GitHub`.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL, indexed |
| platform | VARCHAR | NOT NULL — MVP value: `GitHub` |
| username | VARCHAR | NOT NULL |
| access_token | TEXT | NOT NULL, encrypted at rest |
| refresh_token | TEXT | nullable, encrypted at rest |
| last_synced | TIMESTAMPTZ | nullable |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |

Constraint: UNIQUE `(user_id, platform)`.

---

## 11. resume_versions

Generated resumes. No PDF export or ATS score in MVP.

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL, indexed |
| title | VARCHAR | NOT NULL |
| resume_json | JSONB | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |

---

## 12. reports

Weekly AI growth reports (Monthly/Yearly reserved for future enhancement, MVP only generates `Weekly`).

| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users(id), NOT NULL, indexed |
| type | ENUM | NOT NULL — `Weekly` (MVP); `Monthly`, `Yearly` reserved |
| content | JSONB | NOT NULL |
| period_start | DATE | NOT NULL |
| period_end | DATE | NOT NULL |
| generated_at | TIMESTAMPTZ | NOT NULL, default now() |

---

## Entity Relationship Summary

```
users
 ├── 1:N activities
 ├── 1:N skills
 ├── 1:N projects
 ├── 1:N goals
 ├── 1:N connected_accounts
 ├── 1:N resume_versions
 └── 1:N reports

activities
 ├── 1:1 growth_records
 ├── 1:N skill_evidence
 └── 1:N project_activities

skills
 └── 1:N skill_evidence

projects
 └── 1:N project_activities

goals
 └── 1:1 goal_reflections
```

## Removed Tables / Fields (out of MVP scope)

- No LeetCode/Duolingo/Coursera/Calendar-specific fields — `connected_accounts.platform` supports only `GitHub` for now.
- `resume_versions.resume_pdf_url` and `resume_versions.ats_score` removed (PDF export and ATS scoring are out of scope).
- `activities.activity_type` excludes `leetcode_submission`, `duolingo_session`, `calendar_goal`, `course_completion` — reserved for future enhancement.
- `users.password_hash` removed — credentials are managed by Supabase Auth, not this schema.

## Row-Level Security

Since Supabase Postgres is used, enable Row-Level Security (RLS) on every table and restrict access to rows where `user_id = auth.uid()` (or the equivalent join through `activity_id`/`skill_id`/`goal_id` for child tables like `growth_records`, `skill_evidence`, `project_activities`, and `goal_reflections`).

Child-table ownership is resolved through their parent as follows:

- `growth_records` → owned via `activities.user_id` (join on `growth_records.activity_id = activities.id`)
- `skill_evidence` → owned via `skills.user_id` (join on `skill_evidence.skill_id = skills.id`)
- `project_activities` → owned via `projects.user_id` (join on `project_activities.project_id = projects.id`)
- `goal_reflections` → owned via `goals.user_id` (join on `goal_reflections.goal_id = goals.id`)

Users must never access another user's data, under any circumstance. If service-role operations are required (e.g. server-side jobs that bypass RLS), they must be performed server-side only — the Supabase service-role key must never reach the frontend.
