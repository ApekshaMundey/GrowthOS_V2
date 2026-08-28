-- GrowthOS Initial Schema Migration
-- Matches DatabaseSchemas.md

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- ENUM TYPES
-- -----------------------------------------------------------------------------

CREATE TYPE activity_type_enum AS ENUM (
    'manual_note',
    'project_update',
    'github_commit',
    'youtube_video',
    'meeting_notes',
    'research_note'
);

CREATE TYPE activity_source_enum AS ENUM (
    'Manual',
    'GitHub'
);

CREATE TYPE activity_status_enum AS ENUM (
    'Pending',
    'Processing',
    'Completed',
    'Failed'
);

CREATE TYPE goal_priority_enum AS ENUM (
    'Low',
    'Medium',
    'High'
);

CREATE TYPE goal_status_enum AS ENUM (
    'Pending',
    'Completed',
    'Skipped'
);

CREATE TYPE report_type_enum AS ENUM (
    'Weekly',
    'Monthly',
    'Yearly'
);

-- -----------------------------------------------------------------------------
-- TABLES
-- -----------------------------------------------------------------------------

-- 1. users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    profile_image TEXT,
    profession VARCHAR,
    bio TEXT,
    timezone VARCHAR NOT NULL DEFAULT 'UTC',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. activities
CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type activity_type_enum NOT NULL,
    source activity_source_enum NOT NULL,
    title TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    source_metadata JSONB,
    activity_date TIMESTAMPTZ NOT NULL,
    status activity_status_enum NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_activities_user_date ON activities(user_id, activity_date DESC);

-- 3. growth_records
CREATE TABLE IF NOT EXISTS growth_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID UNIQUE NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    insights JSONB,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    embedding_generated BOOLEAN NOT NULL DEFAULT false,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. skills
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_name VARCHAR NOT NULL,
    category VARCHAR,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    last_used DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_skill_name UNIQUE (user_id, skill_name)
);

CREATE INDEX IF NOT EXISTS idx_skills_user_id ON skills(user_id);

-- 5. skill_evidence
CREATE TABLE IF NOT EXISTS skill_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_skill_evidence_skill_id ON skill_evidence(skill_id);

-- 6. projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    github_repo TEXT,
    status VARCHAR NOT NULL DEFAULT 'active',
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- 7. project_activities
CREATE TABLE IF NOT EXISTS project_activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    CONSTRAINT uq_project_activity UNIQUE (project_id, activity_id)
);

-- 8. goals
CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    description TEXT,
    priority goal_priority_enum NOT NULL,
    target_date DATE,
    status goal_status_enum NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);

-- 9. goal_reflections
CREATE TABLE IF NOT EXISTS goal_reflections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal_id UUID UNIQUE NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    completed BOOLEAN NOT NULL,
    reflection TEXT,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 10. connected_accounts
CREATE TABLE IF NOT EXISTS connected_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    last_synced TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_platform UNIQUE (user_id, platform)
);

CREATE INDEX IF NOT EXISTS idx_connected_accounts_user_id ON connected_accounts(user_id);

-- 11. resume_versions
CREATE TABLE IF NOT EXISTS resume_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    resume_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_resume_versions_user_id ON resume_versions(user_id);

-- 12. reports
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type report_type_enum NOT NULL,
    content JSONB NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);

-- -----------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES
-- -----------------------------------------------------------------------------

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE growth_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE goal_reflections ENABLE ROW LEVEL SECURITY;
ALTER TABLE connected_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE resume_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- 1. users policy
CREATE POLICY users_owner_policy ON users
    FOR ALL USING (id = auth.uid());

-- 2. activities policy
CREATE POLICY activities_owner_policy ON activities
    FOR ALL USING (user_id = auth.uid());

-- 3. growth_records policy (owned via activities)
CREATE POLICY growth_records_owner_policy ON growth_records
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM activities
            WHERE activities.id = growth_records.activity_id
            AND activities.user_id = auth.uid()
        )
    );

-- 4. skills policy
CREATE POLICY skills_owner_policy ON skills
    FOR ALL USING (user_id = auth.uid());

-- 5. skill_evidence policy (owned via skills)
CREATE POLICY skill_evidence_owner_policy ON skill_evidence
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM skills
            WHERE skills.id = skill_evidence.skill_id
            AND skills.user_id = auth.uid()
        )
    );

-- 6. projects policy
CREATE POLICY projects_owner_policy ON projects
    FOR ALL USING (user_id = auth.uid());

-- 7. project_activities policy (owned via projects)
CREATE POLICY project_activities_owner_policy ON project_activities
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = project_activities.project_id
            AND projects.user_id = auth.uid()
        )
    );

-- 8. goals policy
CREATE POLICY goals_owner_policy ON goals
    FOR ALL USING (user_id = auth.uid());

-- 9. goal_reflections policy (owned via goals)
CREATE POLICY goal_reflections_owner_policy ON goal_reflections
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM goals
            WHERE goals.id = goal_reflections.goal_id
            AND goals.user_id = auth.uid()
        )
    );

-- 10. connected_accounts policy
CREATE POLICY connected_accounts_owner_policy ON connected_accounts
    FOR ALL USING (user_id = auth.uid());

-- 11. resume_versions policy
CREATE POLICY resume_versions_owner_policy ON resume_versions
    FOR ALL USING (user_id = auth.uid());

-- 12. reports policy
CREATE POLICY reports_owner_policy ON reports
    FOR ALL USING (user_id = auth.uid());
