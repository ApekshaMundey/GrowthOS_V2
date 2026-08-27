# GrowthOS — AI Architecture

## 1. Principle

AI is used **only** for reasoning tasks. It is invoked from specific, deterministic points in the backend — it does not run autonomously, does not orchestrate other agents, and does not make CRUD or routing decisions. This is a single-model, single-purpose-per-call design, not a multi-agent system.

## 2. AI Responsibilities

| Task | Trigger | Output |
|---|---|---|
| Extract structured information from an Activity | New Activity created | `GrowthRecord` (summary, skills, insights, confidence) |
| Identify/update skills | Part of the extraction step above | Skill names + confidence deltas |
| Generate a weekly growth summary | User/scheduled request for a report | `Report.content` (narrative + highlights) |
| Generate an evidence-backed resume | User requests a resume | `ResumeVersion.resume_json` |

Everything else (auth, CRUD, timeline assembly, analytics math, goal tracking) is plain backend code with **no AI involvement**.

## 3. Model & Tooling

- **Model:** Gemini API.
- **Structured outputs:** every AI call defines a Pydantic schema for the expected response and requests structured/JSON output conforming to it. The backend validates the response against the schema before persisting anything.
- All prompts live in `app/ai/prompts/`, one file per task, so they can be iterated on independently of the calling code.

## 4. Activity → GrowthRecord Pipeline

This pipeline runs **synchronously**, within the same request that creates or reprocesses the Activity (see `APIContracts.md`, `POST /activities` and `POST /growth-records/{activityId}/reprocess`). The request does not return until the pipeline below has completed. There is no queue, background worker, or polling involved in the MVP.

```
Activity.raw_content
   → activity_prompt.py builds the prompt (raw content + activity_type + optional project context)
   → gemini_client.py sends request, requests structured output matching GrowthRecordExtraction schema
   → response validated against Pydantic schema
   → activity_processor.py:
        - creates GrowthRecord row (summary, insights, confidence)
        - for each extracted skill: upsert into Skills (create or update confidence/last_used)
        - create SkillEvidence row linking skill → activity
        - set Activity.status = "Completed"
```

### GrowthRecordExtraction schema (conceptual)

```python
class ExtractedSkill(BaseModel):
    name: str
    category: str | None
    confidence: float  # 0-1

class GrowthRecordExtraction(BaseModel):
    summary: str
    insights: dict
    confidence: float  # overall extraction confidence, 0-1
    skills: list[ExtractedSkill]
```

## 5. Skill Extraction Details

- Skills are matched by name (case-insensitive) against the user's existing `skills` rows.
- If a skill already exists: update `confidence` (e.g. weighted average or max of old/new) and `last_used` to the activity date.
- If it doesn't exist: create a new `skills` row.
- Every extraction — new or repeated skill — creates a new `skill_evidence` row so the skill's evidence trail keeps growing.

## 6. Evidence Extraction

"Evidence" is not a separate AI call — it is a byproduct of the extraction step: each skill the AI identifies in an Activity becomes a `SkillEvidence` row pointing back to that Activity, with a short `description` (AI-generated, one sentence) of why that activity is evidence for that skill.

## 7. Weekly Report Generation

```
report_engine.py:
   - gathers the week's Activities + GrowthRecords + Skill confidence deltas for the user
   - builds a compact structured context (not raw text dumps) to keep prompts small
   → report_prompt.py builds the prompt
   → gemini_client.py requests structured output matching WeeklyReport schema
   → validated and stored in Reports.content
```

### WeeklyReport schema (conceptual)

```python
class WeeklyReport(BaseModel):
    highlights: list[str]
    skillGrowth: dict[str, float]   # skill name -> confidence delta
    goalsCompleted: int
    narrativeSummary: str
```

## 8. Resume Generation

```
resume_engine.py:
   - gathers relevant Projects, Skills (above a confidence threshold), and their SkillEvidence
   - optionally filters by target template/role (e.g. "software_engineer")
   → resume_prompt.py builds the prompt with this evidence bundle
   → gemini_client.py requests structured output matching ResumeDocument schema
   → validated and stored in ResumeVersions.resume_json
```

Every bullet point the AI produces should reference which Project/Activity it is based on, so the resume stays evidence-backed and auditable — this is enforced by including `activityId`/`projectId` references in the `ResumeDocument` schema.

### ResumeDocument schema (conceptual)

```python
class ResumeBullet(BaseModel):
    text: str
    evidenceActivityIds: list[str]

class ResumeSection(BaseModel):
    title: str
    bullets: list[ResumeBullet]

class ResumeDocument(BaseModel):
    summary: str
    sections: list[ResumeSection]
```

## 9. Confidence Handling

- All AI-derived confidence values are floats in `[0, 1]`.
- Confidence is surfaced to the user (e.g. on the Skills page) rather than hidden — this keeps the "evidence-backed" promise honest.
- Low-confidence extractions (below a configurable threshold, e.g. 0.4) are still stored, but the frontend should visually flag them as low-confidence rather than silently dropping them.

## 10. Error / Fallback Behavior

- If the Gemini call fails (network error, malformed response, schema validation failure):
  - `Activity.status` is set to `Failed`.
  - The raw content is preserved unchanged — nothing is lost.
  - The user can retry via `POST /growth-records/{activityId}/reprocess`.
- Retries are user-triggered in MVP — no automatic background retry queue.
- If Gemini returns a response that fails Pydantic validation, the backend logs the raw response for debugging and treats it as a failure (does not attempt partial/best-effort parsing).

## 11. Explicitly Out of Scope for MVP

- Autonomous multi-agent orchestration (no agent "decides" what to do next — every AI call is triggered by a specific backend event).
- Long-running/background AI jobs — all AI calls happen synchronously within a request (or a simple retry via reprocess).
- Semantic search / embeddings (`embedding_generated` field is reserved for a future pgvector-based feature, not implemented in MVP).
