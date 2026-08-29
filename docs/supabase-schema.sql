-- AI HealthGuard — Supabase PostgreSQL schema
-- Run this once in the Supabase SQL Editor (Database → SQL Editor → New query)
-- to create the application tables before first deployment.
--
-- This schema mirrors the SQLAlchemy models exactly.
-- SQLAlchemy's create_all() will also create these on first startup,
-- but running this explicitly gives you visibility and control.

-- ─── health_profiles ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS health_profiles (
    id          SERIAL PRIMARY KEY,
    age         INTEGER NOT NULL,
    sex         VARCHAR(32) NOT NULL,
    conditions  JSONB DEFAULT '[]'::jsonb,
    allergies   JSONB DEFAULT '[]'::jsonb,
    medications JSONB DEFAULT '[]'::jsonb,
    history     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── analysis_sessions ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id                  VARCHAR(32) PRIMARY KEY,
    profile_id          INTEGER NOT NULL REFERENCES health_profiles(id) ON DELETE CASCADE,
    status              VARCHAR(32) NOT NULL DEFAULT 'created',
    follow_up_questions JSONB,
    follow_up_answers   JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_analysis_sessions_profile_id
    ON analysis_sessions(profile_id);

-- ─── symptom_inputs ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS symptom_inputs (
    id                  SERIAL PRIMARY KEY,
    session_id          VARCHAR(32) NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    primary_symptoms    JSONB DEFAULT '[]'::jsonb,
    description         TEXT DEFAULT '',
    duration_text       VARCHAR(128) DEFAULT '',
    severity            INTEGER NOT NULL,
    onset               VARCHAR(16) NOT NULL,
    additional_symptoms JSONB DEFAULT '[]'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_symptom_inputs_session_id
    ON symptom_inputs(session_id);

-- ─── reports ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    id                  SERIAL PRIMARY KEY,
    session_id          VARCHAR(32) NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    filename            VARCHAR(255) NOT NULL,
    file_type           VARCHAR(16) NOT NULL,
    status              VARCHAR(32) NOT NULL,
    raw_text            TEXT,
    extracted_findings  JSONB,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_reports_session_id
    ON reports(session_id);

-- ─── analysis_results ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analysis_results (
    id                      SERIAL PRIMARY KEY,
    session_id              VARCHAR(32) NOT NULL REFERENCES analysis_sessions(id) ON DELETE CASCADE,
    summary                 TEXT NOT NULL,
    symptoms                JSONB DEFAULT '[]'::jsonb,
    observations            JSONB DEFAULT '[]'::jsonb,
    possible_concerns       JSONB DEFAULT '[]'::jsonb,
    risk_level              VARCHAR(16) NOT NULL,
    red_flags               JSONB DEFAULT '[]'::jsonb,
    recommended_next_steps  JSONB DEFAULT '[]'::jsonb,
    questions_for_doctor    JSONB DEFAULT '[]'::jsonb,
    limitations             TEXT DEFAULT '',
    disclaimer              TEXT DEFAULT '',
    source                  VARCHAR(48) DEFAULT 'demo',
    safety_override         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_analysis_results_session_id
    ON analysis_results(session_id);
