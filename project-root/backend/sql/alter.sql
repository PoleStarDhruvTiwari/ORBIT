-- =====================================================================
-- ALTER: add all FOREIGN KEYS and INDEXES.
-- Runs LAST so that seed.sql has already populated the rows the FKs
-- reference. Every statement is idempotent.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Domain FKs
-- ---------------------------------------------------------------------
DO $$ BEGIN
    ALTER TABLE users ADD CONSTRAINT fk_users_role
        FOREIGN KEY (role_id) REFERENCES roles(role_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE users ADD CONSTRAINT fk_users_shift
        FOREIGN KEY (shift_id) REFERENCES shifts(shift_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_role
        FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_permission
        FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE user_sessions ADD CONSTRAINT fk_user_sessions_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ---------------------------------------------------------------------
-- Audit FKs (created_by / updated_by -> users.user_id)
-- ---------------------------------------------------------------------
DO $$ BEGIN
    ALTER TABLE roles ADD CONSTRAINT fk_roles_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE roles ADD CONSTRAINT fk_roles_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE shifts ADD CONSTRAINT fk_shifts_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE shifts ADD CONSTRAINT fk_shifts_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE users ADD CONSTRAINT fk_users_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE users ADD CONSTRAINT fk_users_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE permissions ADD CONSTRAINT fk_permissions_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE permissions ADD CONSTRAINT fk_permissions_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE role_permissions ADD CONSTRAINT fk_role_permissions_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ---------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_users_role_id     ON users(role_id);
CREATE INDEX IF NOT EXISTS idx_users_shift_id    ON users(shift_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active   ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_is_approved ON users(is_approved);
CREATE INDEX IF NOT EXISTS idx_users_created_at  ON users(created_at);

CREATE INDEX IF NOT EXISTS idx_permissions_is_active ON permissions(is_active);
CREATE INDEX IF NOT EXISTS idx_permissions_code      ON permissions(code);

CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id       ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_is_active     ON role_permissions(is_active);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id    ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_device_id  ON user_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_login ON user_sessions(last_login);


-- ---------------------------------------------------------------------
-- Domain FKs for the new tables
-- ---------------------------------------------------------------------
DO $$ BEGIN
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_category
        FOREIGN KEY (category_id) REFERENCES task_categories(task_category_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_replicated_from
        FOREIGN KEY (replicated_from) REFERENCES tasks(task_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recorder_assignments ADD CONSTRAINT fk_assignments_task
        FOREIGN KEY (task_id) REFERENCES tasks(task_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recorder_assignments ADD CONSTRAINT fk_assignments_recorder
        FOREIGN KEY (recorder_id) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recorder_assignments ADD CONSTRAINT fk_assignments_assigned_by
        FOREIGN KEY (assigned_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recorder_assignments ADD CONSTRAINT fk_assignments_shift
        FOREIGN KEY (shift_id) REFERENCES shifts(shift_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recorder_assignments ADD CONSTRAINT fk_assignments_reassigned
        FOREIGN KEY (reassigned_from_id) REFERENCES recorder_assignments(recorder_assignment_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recording_logs ADD CONSTRAINT fk_recording_logs_assignment
        FOREIGN KEY (assignment_id) REFERENCES recorder_assignments(recorder_assignment_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recording_logs ADD CONSTRAINT fk_recording_logs_recorder
        FOREIGN KEY (recorder_id) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_replications ADD CONSTRAINT fk_replications_original_task
        FOREIGN KEY (original_task_id) REFERENCES tasks(task_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_replications ADD CONSTRAINT fk_replications_recording_log
        FOREIGN KEY (recording_log_id) REFERENCES recording_logs(recording_log_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_replications ADD CONSTRAINT fk_replications_replicated_by
        FOREIGN KEY (replicated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_comments ADD CONSTRAINT fk_task_comments_task
        FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_comments ADD CONSTRAINT fk_task_comments_author
        FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE;
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE qa_feedback ADD CONSTRAINT fk_qa_feedback_recording_log
        FOREIGN KEY (recording_log_id) REFERENCES recording_logs(recording_log_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE qa_feedback ADD CONSTRAINT fk_qa_feedback_qa_user
        FOREIGN KEY (qa_user_id) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ---------------------------------------------------------------------
-- Audit FKs for new tables
-- ---------------------------------------------------------------------
DO $$ BEGIN
    ALTER TABLE task_categories ADD CONSTRAINT fk_task_categories_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_categories ADD CONSTRAINT fk_task_categories_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tasks ADD CONSTRAINT fk_tasks_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recorder_assignments ADD CONSTRAINT fk_assignments_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recorder_assignments ADD CONSTRAINT fk_assignments_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recording_logs ADD CONSTRAINT fk_recording_logs_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE recording_logs ADD CONSTRAINT fk_recording_logs_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_replications ADD CONSTRAINT fk_replications_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE task_replications ADD CONSTRAINT fk_replications_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE qa_feedback ADD CONSTRAINT fk_qa_feedback_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE qa_feedback ADD CONSTRAINT fk_qa_feedback_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;


-- ---------------------------------------------------------------------
-- Indexes for new tables
-- ---------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_task_categories_is_active ON task_categories(is_active);

CREATE INDEX IF NOT EXISTS idx_tasks_category_id  ON tasks(category_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status       ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_task_type    ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_is_active    ON tasks(is_active);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at   ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_priority     ON tasks(priority);

CREATE INDEX IF NOT EXISTS idx_assignments_task_id            ON recorder_assignments(task_id);
CREATE INDEX IF NOT EXISTS idx_assignments_recorder_id        ON recorder_assignments(recorder_id);
CREATE INDEX IF NOT EXISTS idx_assignments_assigned_by        ON recorder_assignments(assigned_by);
CREATE INDEX IF NOT EXISTS idx_assignments_assigned_date      ON recorder_assignments(assigned_date);
CREATE INDEX IF NOT EXISTS idx_assignments_shift_id           ON recorder_assignments(shift_id);
CREATE INDEX IF NOT EXISTS idx_assignments_status             ON recorder_assignments(status);
CREATE INDEX IF NOT EXISTS idx_assignments_completed_at       ON recorder_assignments(completed_at);
CREATE INDEX IF NOT EXISTS idx_assignments_is_active          ON recorder_assignments(is_active);
CREATE INDEX IF NOT EXISTS idx_assignments_reassigned_from_id ON recorder_assignments(reassigned_from_id);

CREATE INDEX IF NOT EXISTS idx_recording_logs_assignment_id ON recording_logs(assignment_id);
CREATE INDEX IF NOT EXISTS idx_recording_logs_recorder_id   ON recording_logs(recorder_id);
CREATE INDEX IF NOT EXISTS idx_recording_logs_status        ON recording_logs(status);
CREATE INDEX IF NOT EXISTS idx_recording_logs_recorded_at   ON recording_logs(recorded_at);
CREATE INDEX IF NOT EXISTS idx_recording_logs_is_active     ON recording_logs(is_active);

CREATE INDEX IF NOT EXISTS idx_task_replications_original_task_id ON task_replications(original_task_id);
CREATE INDEX IF NOT EXISTS idx_task_replications_recording_log_id ON task_replications(recording_log_id);
CREATE INDEX IF NOT EXISTS idx_task_replications_replicated_by    ON task_replications(replicated_by);
CREATE INDEX IF NOT EXISTS idx_task_replications_environment_type ON task_replications(environment_type);
CREATE INDEX IF NOT EXISTS idx_task_replications_is_active        ON task_replications(is_active);

CREATE INDEX IF NOT EXISTS idx_task_comments_task_id ON task_comments(task_id);
CREATE INDEX IF NOT EXISTS idx_task_comments_author_id ON task_comments(author_id);

CREATE INDEX IF NOT EXISTS idx_qa_feedback_recording_log_id  ON qa_feedback(recording_log_id);
CREATE INDEX IF NOT EXISTS idx_qa_feedback_qa_user_id        ON qa_feedback(qa_user_id);
CREATE INDEX IF NOT EXISTS idx_qa_feedback_feedback_category ON qa_feedback(feedback_category);
CREATE INDEX IF NOT EXISTS idx_qa_feedback_is_rework_required ON qa_feedback(is_rework_required);
CREATE INDEX IF NOT EXISTS idx_qa_feedback_is_active         ON qa_feedback(is_active);

-- One recorder cannot be assigned the same task on the same day twice.
CREATE UNIQUE INDEX IF NOT EXISTS uq_assignment_per_day
    ON recorder_assignments (task_id, recorder_id, assigned_date);


-- =====================================================================
-- END alter.sql
-- =====================================================================
