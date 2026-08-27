# GrowthOS — API Contracts (MVP, v1)

**Base URL:** `/api/v1`

Unless noted otherwise, every endpoint requires a valid Supabase-issued JWT in the `Authorization: Bearer <token>` header. The backend resolves `user_id` from the token; all data is scoped to that user.

---

## Module 1 — Auth & Profile

Registration, login, logout, and token refresh are handled client-side by the Supabase Auth SDK and are **not** implemented as custom backend endpoints. The backend only exposes profile endpoints.

### Get Profile
`GET /users/me`
- Auth: required
- Response: `{ id, name, email, profileImage, profession, bio, timezone, createdAt }`
- Errors: `401 Unauthorized`

### Update Profile
`PUT /users/me`
- Auth: required
- Request: `{ name?, profileImage?, profession?, bio?, timezone? }`
- Response: updated profile object
- Errors: `400 Validation Error`, `401 Unauthorized`

---

## Module 2 — GitHub Integration

### Connect GitHub
`POST /integrations/github/connect`
- Auth: required
- Request: `{ oauthCode: string }`
- Response: `{ connected: true, username: string }`
- Errors: `400 Invalid OAuth Code`, `401 Unauthorized`

### Sync GitHub
`POST /integrations/github/sync`
- Auth: required
- Request: `{}` (manual, on-demand trigger — no body needed)
- Response: `{ syncedActivities: number, lastSynced: string }`
- Errors: `401 Unauthorized`, `404 Not Connected`, `502 GitHub API Error`

### List Connected Accounts
`GET /integrations`
- Auth: required
- Response: `[{ platform: "GitHub", username, lastSynced }]`
- Errors: `401 Unauthorized`

---

## Module 3 — Activities

### Create Activity
`POST /activities`
- Auth: required
- Processing: **synchronous**. The request does not return until AI extraction has completed. Flow: create Activity → run AI extraction → validate with Pydantic → create GrowthRecord → update Skills/Evidence → return the completed result in the same response. There is no polling, background job, queue, or separate processing-status endpoint in the MVP.
- Request:
```json
{
  "activityType": "manual_note",
  "title": "Today's Progress",
  "content": "Built JWT authentication and solved 3 graph problems."
}
```
- Response: `{ "activityId": "uuid", "status": "Completed", "growthRecord": { "summary": "...", "insights": {}, "confidence": 0.9 } }` — or `{ "activityId": "uuid", "status": "Failed" }` if AI extraction fails (see `AIArchitecture.md` for fallback behavior; retry via `POST /growth-records/{activityId}/reprocess`).
- Errors: `400 Validation Error`, `401 Unauthorized`

### Get All Activities
`GET /activities`
- Auth: required
- Query params (optional): `page`, `limit`, `source`, `activityType`
- Response: `{ items: [Activity], page, totalPages }`
- Errors: `401 Unauthorized`

### Get Activity
`GET /activities/{id}`
- Auth: required
- Response: `Activity` object (includes linked GrowthRecord if processed)
- Errors: `401 Unauthorized`, `404 Not Found`

### Update Activity
`PUT /activities/{id}`
- Auth: required
- Request: `{ title?, content? }`
- Response: updated `Activity`
- Errors: `400 Validation Error`, `401 Unauthorized`, `404 Not Found`

### Delete Activity
`DELETE /activities/{id}`
- Auth: required
- Response: `204 No Content`
- Errors: `401 Unauthorized`, `404 Not Found`

---

## Module 4 — Growth Memory (GrowthRecords)

### Get Growth Record
`GET /growth-records/{activityId}`
- Auth: required
- Response: `{ activityId, summary, insights, confidence, processedAt }`
- Errors: `401 Unauthorized`, `404 Not Found`

### Reprocess Activity
`POST /growth-records/{activityId}/reprocess`
- Auth: required
- Processing: **synchronous**, same as Activity creation — the request does not return until AI extraction has completed.
- Use case: re-run AI extraction if it previously failed or AI logic improved.
- Response: `{ "activityId": "uuid", "status": "Completed", "growthRecord": {...} }` or `{ "activityId": "uuid", "status": "Failed" }`
- Errors: `401 Unauthorized`, `404 Not Found`

> Semantic search (`POST /growth-records/search`) is a **future enhancement** (requires pgvector) and is not part of MVP.

---

## Module 5 — Skills

### Get All Skills
`GET /skills`
- Auth: required
- Response: `[{ id, skillName, category, confidence, lastUsed }]`
- Errors: `401 Unauthorized`

### Get Skill Details
`GET /skills/{id}`
- Auth: required
- Response: `{ id, skillName, category, confidence, lastUsed }`
- Errors: `401 Unauthorized`, `404 Not Found`

### Get Skill Evidence
`GET /skills/{id}/evidence`
- Auth: required
- Response: `[{ activityId, confidence, description, activityTitle, activityDate }]`
- Errors: `401 Unauthorized`, `404 Not Found`

---

## Module 6 — Projects

**`status` field:** per `DatabaseSchemas.md`, `projects.status` is a `VARCHAR` with default `active` — the schema does not constrain it to a fixed enum, so no additional project states are prescribed here beyond the `active` default.

### Create Project
`POST /projects`
- Auth: required
- Request: `{ name, description?, githubRepo?, startDate?, endDate? }`
- Response: created `Project`
- Errors: `400 Validation Error`, `401 Unauthorized`

### Get Projects
`GET /projects`
- Auth: required
- Response: `[Project]`
- Errors: `401 Unauthorized`

### Get Project
`GET /projects/{id}`
- Auth: required
- Response: `Project` (with linked activities summary)
- Errors: `401 Unauthorized`, `404 Not Found`

### Update Project
`PUT /projects/{id}`
- Auth: required
- Request: `{ name?, description?, status?, endDate? }`
- Response: updated `Project`
- Errors: `400 Validation Error`, `401 Unauthorized`, `404 Not Found`

### Delete Project
`DELETE /projects/{id}`
- Auth: required
- Response: `204 No Content`
- Errors: `401 Unauthorized`, `404 Not Found`

### Link Activity to Project
`POST /projects/{id}/activities`
- Auth: required
- Request: `{ activityId }`
- Response: `{ projectId, activityId }`
- Errors: `400 Validation Error`, `401 Unauthorized`, `404 Not Found`

---

## Module 7 — Goals

### Create Goal
`POST /goals`
- Auth: required
- Request:
```json
{ "title": "Complete LangChain", "priority": "High", "targetDate": "2026-08-05" }
```
- Response: created `Goal`
- Errors: `400 Validation Error`, `401 Unauthorized`

### Get Goals
`GET /goals`
- Auth: required
- Query params (optional): `status`
- Response: `[Goal]`
- Errors: `401 Unauthorized`

### Update Goal
`PUT /goals/{id}`
- Auth: required
- Request: `{ title?, description?, priority?, targetDate? }`
- Response: updated `Goal`
- Errors: `400 Validation Error`, `401 Unauthorized`, `404 Not Found`

### Complete Goal
`PATCH /goals/{id}/complete`
- Auth: required
- Response: updated `Goal` with `status = "Completed"`
- Errors: `401 Unauthorized`, `404 Not Found`

### Add Reflection
`POST /goals/{id}/reflection`
- Auth: required
- Request: `{ completed: boolean, reflection?, reason? }`
- Response: created `GoalReflection`
- Errors: `400 Validation Error`, `401 Unauthorized`, `404 Not Found`

---

## Module 8 — Timeline

### Timeline
`GET /timeline`
- Auth: required
- Query params (optional): `startDate`, `endDate`
- Response: `[{ activity, growthRecord }]` sorted by `activityDate` descending
- Errors: `401 Unauthorized`

---

## Module 9 — Analytics

### Dashboard Summary
`GET /dashboard`
- Auth: required
- Response:
```json
{
  "todayGoals": [],
  "recentActivities": [],
  "weeklyProgress": {},
  "skillGrowth": {},
  "streak": 12
}
```
- Errors: `401 Unauthorized`

### Analytics
`GET /analytics`
- Auth: required
- Query params: `period` = `weekly` | `monthly`
- Response: aggregated analytics object for the requested period
- Errors: `400 Invalid Period`, `401 Unauthorized`

### Skill Growth
`GET /analytics/skills`
- Auth: required
- Response: `[{ skillName, confidenceHistory: [{date, confidence}] }]`
- Errors: `401 Unauthorized`

### Productivity
`GET /analytics/productivity`
- Auth: required
- Response: `{ activityCountByDay: {...}, streak: number }`
- Errors: `401 Unauthorized`

---

## Module 10 — Reports

### Generate Report
`POST /reports/generate`
- Auth: required
- Request: `{ "period": "weekly" }`
- Response: `{ reportId, status: "Processing" }`
- Errors: `400 Invalid Period`, `401 Unauthorized`

### Get Reports
`GET /reports`
- Auth: required
- Response: `[Report]`
- Errors: `401 Unauthorized`

### Get Report
`GET /reports/{id}`
- Auth: required
- Response: `Report` (with full `content`)
- Errors: `401 Unauthorized`, `404 Not Found`

---

## Module 11 — Resume

### Generate Resume
`POST /resume/generate`
- Auth: required
- Request: `{ "template": "software_engineer" }`
- Response: `{ resumeId, status: "Processing" }`
- Errors: `400 Validation Error`, `401 Unauthorized`

### Resume History
`GET /resume/history`
- Auth: required
- Response: `[{ id, title, createdAt }]`
- Errors: `401 Unauthorized`

### Get Resume
`GET /resume/{id}`
- Auth: required
- Response: `{ id, title, resumeJson, createdAt }`
- Errors: `401 Unauthorized`, `404 Not Found`

> PDF export (`GET /resume/{id}/pdf`) and ATS analysis (`POST /resume/{id}/ats-score`) are **not** part of MVP.
