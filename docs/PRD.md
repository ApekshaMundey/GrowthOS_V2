# GrowthOS — Product Requirements Document (MVP)

## 1. Product Vision

**Tagline:** Transform your daily efforts into measurable growth.

GrowthOS is an AI-powered personal growth platform that automatically captures a user's daily work, organizes it into a structured, persistent **Growth Memory**, and generates meaningful insights — progress analytics, learning timelines, and evidence-backed resumes — with minimal manual effort.

Unlike note-taking apps, GrowthOS focuses on understanding **how a person is growing**, not just storing what they wrote down.

## 2. Problem Statement

People learn every day through projects, courses, research, coding practice, reading, videos, meetings, and personal experience. However:

- Achievements are scattered across different platforms.
- People forget what they accomplished.
- Resumes become difficult to maintain.
- Skills cannot easily be backed with evidence.
- Long-term growth is difficult to measure.

Existing productivity tools help users **store information**, but none of them automatically understand personal growth. GrowthOS solves this.

## 3. Target Users

Anyone who continuously learns, including but not limited to:

- Students
- Software Engineers
- Researchers
- Designers
- Product Managers
- Content Creators
- Freelancers
- Lifelong Learners

## 4. Core Philosophy

**Users should spend their time learning, not documenting.**

The platform automatically organizes, analyzes, and connects information while requiring minimal manual input.

## 5. MVP Goals

GrowthOS (MVP) should allow users to:

- Capture daily work quickly (under 60 seconds).
- Build a long-term, persistent Growth Memory.
- Track learning and skill growth over time.
- Set goals and reflect on progress against them.
- Generate resumes from real, evidence-backed history.
- Visualize personal growth through a timeline and analytics dashboard.
- Sync lightweight metadata from GitHub to reduce manual documentation.

## 6. MVP Features

1. **User Authentication** — register, log in, log out, manage profile (via Supabase Auth).
2. **Daily Activity Capture** — quick free-text entry of work, links, notes, and updates.
3. **AI Extraction into GrowthRecords** — every Activity is processed by AI into a structured record.
4. **Persistent Growth Memory** — the accumulated, structured record of a user's skills, projects, and history.
5. **Skills** — inferred skills with a confidence score, evolving over time.
6. **Skill Evidence** — every skill is linked back to the specific activities that support it.
7. **Projects** — group related activities under a named project, optionally linked to a GitHub repo.
8. **Goals & Reflections** — set goals, mark completion, and record end-of-day reflections.
9. **Growth Timeline** — chronological view of activities and growth records.
10. **Analytics Dashboard** — weekly/monthly summaries, skill growth, goal completion, consistency streaks.
11. **Weekly AI Growth Report** — an AI-generated narrative summary of the week's progress.
12. **Evidence-Backed Resume Generation** — resumes generated from Growth Memory, citing real evidence.
13. **GitHub Integration** — connect a GitHub account and manually trigger a sync to pull repositories, languages, and commit/activity metadata as Activities.

## 7. User Journeys

**Daily capture:**
User logs in → writes a short free-text entry describing what they did → GrowthOS creates an Activity → AI extracts a GrowthRecord (skills, summary, insights) → Growth Memory, Timeline, and Skills update automatically.

**Goal-setting and reflection:**
User sets a morning goal → works through the day, logging activities → in the evening, marks the goal complete/incomplete and adds a reflection → GrowthOS compares planned vs. completed work.

**GitHub sync:**
User connects their GitHub account → manually triggers a sync → GrowthOS pulls repository, language, and commit metadata → creates `github_commit` Activities → these flow through the same AI extraction pipeline as manual entries.

**Weekly report:**
At the end of the week, the user (or a scheduled job) requests a report → AI summarizes the week's Activities and GrowthRecords into a narrative report with highlights and skill growth.

**Resume generation:**
User requests a resume for a target role → GrowthOS retrieves relevant projects, skills, and evidence from Growth Memory → AI assembles a resume document, with every claim traceable to underlying evidence.

## 8. Functional Requirements

The system shall allow users to:

- Register, log in, and log out.
- Connect a GitHub account and manually sync it.
- Create, view, edit, and delete daily Activities.
- Automatically generate structured GrowthRecords from Activities via AI.
- View a chronological Timeline of activities and growth.
- View inferred Skills and their supporting Evidence.
- Create and manage Projects, and link Activities to them.
- Create Goals and add end-of-day Reflections.
- View an Analytics Dashboard (weekly/monthly/skill growth/streaks).
- Generate a Weekly AI Growth Report.
- Generate an evidence-backed Resume.

## 9. Non-Functional Requirements

The system should be:

- Fast — daily capture should feel instantaneous.
- Secure — user data and tokens (e.g. GitHub access tokens) must be protected.
- Lightweight and simple — avoid unnecessary infrastructure for an MVP.
- Easy to use — minimal formatting required to log an activity.
- Privacy-aware — users control what is connected and synced.
- Modular — AI, backend, and integrations should be cleanly separated so features can be extended later.

## 10. AI Responsibilities (Summary)

AI is used only where reasoning is required: extracting structured information from activities, identifying skills, generating summaries, generating weekly growth insights, and generating evidence-backed resumes. See `AIArchitecture.md` for details.

Normal deterministic backend code handles authentication, CRUD, database operations, timelines, analytics calculations, goals, and GitHub synchronization. AI is not used for these.

## 11. Success Metrics

GrowthOS (MVP) is successful if users can:

- Record their daily work in under 60 seconds.
- Retrieve past work quickly via the timeline.
- Generate a resume without manually collecting achievements.
- Clearly understand their weekly progress from the dashboard and weekly report.
- Feel encouraged to keep documenting consistently.

## 12. Explicit MVP Exclusions

The following are **not** part of the MVP, regardless of whether they appear in earlier design discussions:

- ATS resume scoring
- PDF resume export
- LeetCode integration
- Duolingo integration
- Calendar integration
- Coursera integration
- LinkedIn integration
- Google Drive integration
- Mobile application
- Voice-based capture
- OCR from screenshots
- Autonomous multi-agent orchestration
- Background workers / job queues beyond what a manual GitHub sync requires
- Automatic/webhook-based GitHub synchronization (MVP sync is manual/on-demand)

## 13. Future Enhancements

The following may be reconsidered after the MVP ships:

- Voice-based daily capture
- OCR from screenshots
- PDF resume export
- ATS resume scoring
- Calendar integration
- LeetCode and Duolingo integrations
- Coursera, LinkedIn, and Google Drive integrations
- Mobile application
- AI-powered coaching
- Automatic/webhook-driven GitHub sync and background workers
- Semantic search over Growth Memory using pgvector
- Additional learning-platform integrations
