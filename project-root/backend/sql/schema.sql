-- =====================================================================
-- ORBIT MVP DATABASE SCHEMA
-- Focused tables: roles, permissions, role_permissions, shifts, users,
-- user_sessions.
--
-- This file creates ENUMs and TABLES only (PKs + CHECK/UNIQUE/NOT NULL).
-- Foreign keys live in alter.sql so the bootstrap order can be:
--     1) schema.sql  (tables)
--     2) seed.sql    (rows)
--     3) alter.sql   (FKs + indexes)
-- All statements are idempotent.
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ---------------------------------------------------------------------
-- ENUMs
-- ---------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE role_name_enum AS ENUM ('super_admin', 'admin', 'qa', 'recorder');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE shift_name_enum AS ENUM ('morning', 'evening', 'night');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE device_type_enum AS ENUM ('mobile', 'web', 'tablet', 'desktop');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_status_enum AS ENUM ('draft', 'approved', 'rejected', 'archived');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_type_enum AS ENUM ('general', 'niche');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_priority AS ENUM ('P0', 'P1', 'P2', 'P3');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_environment AS ENUM ('office/outdoor', 'outdoor', 'office');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE assignment_status_enum AS ENUM (
        'assigned', 'in_progress', 'submitted', 'qa_review_pending',
        'completed', 'rejected', 'skipped', 'reassigned'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE recording_status_enum AS ENUM (
        'pending_review', 'approved', 'rejected', 'rework_needed'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE feedback_category_enum AS ENUM (
        'accuracy', 'completeness', 'speed', 'guidelines'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_comment_kind AS ENUM (
        'comment', 'status_change', 'skip_requested', 'skip_approved',
        'skip_rejected', 'submitted', 'created', 'assigned'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ---------------------------------------------------------------------
-- roles
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    role_id BIGSERIAL PRIMARY KEY,

    name        role_name_enum UNIQUE NOT NULL,
    description TEXT NOT NULL,

    can_assign_tasks   BOOLEAN NOT NULL DEFAULT FALSE,
    can_create_tasks   BOOLEAN NOT NULL DEFAULT FALSE,
    can_review_quality BOOLEAN NOT NULL DEFAULT FALSE,
    can_manage_users   BOOLEAN NOT NULL DEFAULT FALSE,
    can_view_reports   BOOLEAN NOT NULL DEFAULT FALSE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ---------------------------------------------------------------------
-- shifts
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shifts (
    shift_id BIGSERIAL PRIMARY KEY,

    name shift_name_enum UNIQUE NOT NULL,

    start_time TIME NOT NULL,
    end_time   TIME NOT NULL,

    description TEXT NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_shift_time CHECK (start_time <> end_time)
);


-- ---------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,

    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    labeller_id VARCHAR(50)  UNIQUE NOT NULL,

    role_id  BIGINT NOT NULL,
    shift_id BIGINT NOT NULL,

    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT,
    updated_by BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_users_email CHECK (POSITION('@' IN email) > 1)
);


-- ---------------------------------------------------------------------
-- permissions  (managed by the app's permissions registry)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS permissions (
    permission_id BIGSERIAL PRIMARY KEY,

    code        VARCHAR(150) UNIQUE NOT NULL,
    description TEXT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT,
    updated_by BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ---------------------------------------------------------------------
-- role_permissions
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS role_permissions (
    role_permission_id BIGSERIAL PRIMARY KEY,

    role_id       BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT,
    updated_by BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id)
);


-- ---------------------------------------------------------------------
-- user_sessions
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    device_id   VARCHAR(100),
    device_type device_type_enum NOT NULL,

    hashed_refresh_token TEXT NOT NULL,

    expires_at TIMESTAMPTZ NOT NULL,
    last_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_session_expiry CHECK (expires_at > created_at)
);


-- ---------------------------------------------------------------------
-- task_categories
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS task_categories (
    task_category_id BIGSERIAL PRIMARY KEY,

    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ---------------------------------------------------------------------
-- tasks
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    task_id BIGSERIAL PRIMARY KEY,

    task_key    VARCHAR(50) UNIQUE NOT NULL,
    category_id BIGINT      NOT NULL,
    environment task_environment NOT NULL,
    priority    task_priority    NOT NULL DEFAULT 'P2',

    task_type   task_type_enum NOT NULL DEFAULT 'general',
    title       VARCHAR(500)   NOT NULL,
    description TEXT           NOT NULL,
    task_script TEXT,

    estimated_time_minutes INTEGER NOT NULL,

    source_sheet_name VARCHAR(255),
    source_row_id     VARCHAR(100),

    replicated_from BIGINT,

    status    task_status_enum NOT NULL DEFAULT 'draft',
    is_active BOOLEAN          NOT NULL DEFAULT TRUE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_tasks_estimated_time
        CHECK (estimated_time_minutes BETWEEN 2 AND 15)
);


-- ---------------------------------------------------------------------
-- recorder_assignments
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recorder_assignments (
    recorder_assignment_id BIGSERIAL PRIMARY KEY,

    task_id        BIGINT NOT NULL,
    recorder_id    BIGINT NOT NULL,
    assigned_by    BIGINT NOT NULL,
    assigned_date  DATE   NOT NULL DEFAULT CURRENT_DATE,
    shift_id       BIGINT NOT NULL,

    status assignment_status_enum NOT NULL DEFAULT 'assigned',

    completed_at        TIMESTAMPTZ,
    skipped_reason      TEXT,
    reassigned_from_id  BIGINT,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_completed_at
        CHECK (completed_at IS NULL OR completed_at >= created_at)
);


-- ---------------------------------------------------------------------
-- recording_logs
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recording_logs (
    recording_log_id BIGSERIAL PRIMARY KEY,

    assignment_id BIGINT UNIQUE NOT NULL,
    recorder_id   BIGINT        NOT NULL,

    status recording_status_enum NOT NULL DEFAULT 'pending_review',

    actual_time_minutes INTEGER NOT NULL,

    comment      TEXT,
    recorded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_recording_actual_time
        CHECK (actual_time_minutes BETWEEN 0 AND 60)
);


-- ---------------------------------------------------------------------
-- task_replications
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS task_replications (
    task_replication_id BIGSERIAL PRIMARY KEY,

    original_task_id BIGINT NOT NULL,
    recording_log_id BIGINT NOT NULL,

    environment_type       task_environment NOT NULL,
    environment_identifier VARCHAR(255)     NOT NULL,

    replicated_by BIGINT NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_task_replication_environment
        UNIQUE (recording_log_id, environment_identifier)
);


-- ---------------------------------------------------------------------
-- task_comments
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS task_comments (
    id        BIGSERIAL PRIMARY KEY,
    task_id   BIGINT NOT NULL,
    author_id BIGINT NOT NULL,

    kind        task_comment_kind NOT NULL,
    body        TEXT,
    status_from task_status_enum,
    status_to   task_status_enum,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ---------------------------------------------------------------------
-- qa_feedback
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS qa_feedback (
    qa_feedback_id BIGSERIAL PRIMARY KEY,

    recording_log_id BIGINT NOT NULL,
    qa_user_id       BIGINT NOT NULL,

    pass_rate           INTEGER NOT NULL,
    feedback_text       TEXT    NOT NULL,
    is_rework_required  BOOLEAN NOT NULL DEFAULT FALSE,
    feedback_category   feedback_category_enum NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_by BIGINT NOT NULL,
    updated_by BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_qa_feedback_pass_rate
        CHECK (pass_rate BETWEEN 0 AND 100)
);


-- =====================================================================
-- END schema.sql
-- =====================================================================
