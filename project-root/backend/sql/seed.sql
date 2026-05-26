-- =====================================================================
-- SEED: bootstrap roles, shifts, and a super_admin user.
-- Runs AFTER schema.sql but BEFORE alter.sql
-- Every statement is idempotent.
-- =====================================================================

BEGIN;

-- Roles ---------------------------------------------------------------
INSERT INTO roles (role_id, name, description,
                   can_assign_tasks, can_create_tasks, can_review_quality,
                   can_manage_users, can_view_reports,
                   created_by, updated_by)
VALUES (1, 'super_admin', 'Full system access',
        TRUE, TRUE, TRUE, TRUE, TRUE, 1, 1)
ON CONFLICT (role_id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('roles', 'role_id'),
              COALESCE((SELECT MAX(role_id) FROM roles), 1));

INSERT INTO roles (name, description,
                   can_assign_tasks, can_create_tasks, can_review_quality,
                   can_manage_users, can_view_reports,
                   created_by, updated_by)
SELECT 'admin', 'Administrator',
       TRUE, TRUE, TRUE, TRUE, TRUE, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'admin');

INSERT INTO roles (name, description,
                   can_assign_tasks, can_create_tasks, can_review_quality,
                   can_manage_users, can_view_reports,
                   created_by, updated_by)
SELECT 'qa', 'Quality assurance reviewer',
       FALSE, FALSE, TRUE, FALSE, TRUE, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'qa');

INSERT INTO roles (name, description,
                   can_assign_tasks, can_create_tasks, can_review_quality,
                   can_manage_users, can_view_reports,
                   created_by, updated_by)
SELECT 'recorder', 'Recorder',
       FALSE, FALSE, FALSE, FALSE, FALSE, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'recorder');

-- Shifts --------------------------------------------------------------
INSERT INTO shifts (shift_id, name, start_time, end_time, description,
                    is_active, created_by, updated_by)
VALUES (1, 'morning', '06:00', '14:00', 'Morning shift', TRUE, 1, 1)
ON CONFLICT (shift_id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('shifts', 'shift_id'),
              COALESCE((SELECT MAX(shift_id) FROM shifts), 1));

INSERT INTO shifts (name, start_time, end_time, description,
                    is_active, created_by, updated_by)
SELECT 'evening', '14:00', '22:00', 'Evening shift', TRUE, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM shifts WHERE name = 'evening');

INSERT INTO shifts (name, start_time, end_time, description,
                    is_active, created_by, updated_by)
SELECT 'night', '22:00', '06:00', 'Night shift', TRUE, 1, 1
WHERE NOT EXISTS (SELECT 1 FROM shifts WHERE name = 'night');

-- Bootstrap super_admin user (user_id = 1)
INSERT INTO users (user_id, email, name, labeller_id,
                   role_id, shift_id,
                   is_approved, is_active,
                   created_by, updated_by)
VALUES (1, 'dhruvtiwari756placement@gmail.com', 'Super Admin', 'ADMIN-0001',
        (SELECT role_id FROM roles WHERE name = 'super_admin'),
        (SELECT shift_id FROM shifts WHERE name = 'morning'),
        TRUE, TRUE, 1, 1)
ON CONFLICT (user_id) DO UPDATE SET
    email = EXCLUDED.email,
    name = EXCLUDED.name,
    labeller_id = EXCLUDED.labeller_id,
    role_id = EXCLUDED.role_id,
    shift_id = EXCLUDED.shift_id,
    is_approved = EXCLUDED.is_approved,
    is_active = EXCLUDED.is_active,
    updated_by = EXCLUDED.updated_by,
    updated_at = now();

SELECT setval(pg_get_serial_sequence('users', 'user_id'),
              COALESCE((SELECT MAX(user_id) FROM users), 1));

-- =====================================================================
-- MOCK DATA  (idempotent; safe to re-run on every container start)
-- =====================================================================
DO $$
DECLARE
    r_admin    BIGINT;
    r_qa       BIGINT;
    r_recorder BIGINT;
    s_morning  BIGINT;
    s_evening  BIGINT;
    s_night    BIGINT;

    c_cleaning BIGINT;
    c_kitchen  BIGINT;
    c_home     BIGINT;
    c_office   BIGINT;
    c_retail   BIGINT;

    u_super  BIGINT := 1;
    u_adm1   BIGINT;  u_adm2 BIGINT;  u_adm3 BIGINT;  u_adm4 BIGINT;
    u_qa1    BIGINT;  u_qa2  BIGINT;  u_qa3  BIGINT;
    u_rec1   BIGINT;  u_rec2 BIGINT;  u_rec3 BIGINT;  u_rec4 BIGINT;
    u_rec5   BIGINT;  u_rec6 BIGINT;  u_rec7 BIGINT;  u_rec8 BIGINT;
    u_rec9   BIGINT;

    t001 BIGINT; t002 BIGINT; t003 BIGINT; t004 BIGINT; t005 BIGINT;
    t006 BIGINT; t007 BIGINT; t008 BIGINT; t009 BIGINT; t010 BIGINT;
    t011 BIGINT; t012 BIGINT; t013 BIGINT; t014 BIGINT; t015 BIGINT;

    a_arjun_t013 BIGINT;
    rl_tommy_t001 BIGINT;
    rl_ishita_t002 BIGINT;
    rl_arjun_t005 BIGINT;
    rl_zara_t013  BIGINT;
    rl_kabir_t009 BIGINT;
    rl_ishita_t007 BIGINT;
    rl_meera_t011 BIGINT;
    rl_ananya_t003 BIGINT;
BEGIN
    -- Lookups
    SELECT role_id INTO r_admin    FROM roles WHERE name = 'admin';
    SELECT role_id INTO r_qa       FROM roles WHERE name = 'qa';
    SELECT role_id INTO r_recorder FROM roles WHERE name = 'recorder';
    SELECT shift_id INTO s_morning FROM shifts WHERE name = 'morning';
    SELECT shift_id INTO s_evening FROM shifts WHERE name = 'evening';
    SELECT shift_id INTO s_night   FROM shifts WHERE name = 'night';

    -- Task categories (idempotent by name)
    INSERT INTO task_categories (name, description, created_by, updated_by) VALUES
        ('cleaning',             'General cleaning tasks across spaces',          u_super, u_super),
        ('kitchen_and_food',     'Kitchen prep, cooking, and food handling',      u_super, u_super),
        ('home_spaces',          'Home space tidying and organization',           u_super, u_super),
        ('office_and_workspace', 'Office and desk organization',                  u_super, u_super),
        ('retail_operations',    'Retail floor and customer-facing operations',   u_super, u_super)
    ON CONFLICT (name) DO NOTHING;

    SELECT task_category_id INTO c_cleaning FROM task_categories WHERE name = 'cleaning';
    SELECT task_category_id INTO c_kitchen  FROM task_categories WHERE name = 'kitchen_and_food';
    SELECT task_category_id INTO c_home     FROM task_categories WHERE name = 'home_spaces';
    SELECT task_category_id INTO c_office   FROM task_categories WHERE name = 'office_and_workspace';
    SELECT task_category_id INTO c_retail   FROM task_categories WHERE name = 'retail_operations';

    -- Users (idempotent by email)
    INSERT INTO users (email, name, labeller_id, role_id, shift_id, is_approved, is_active, created_by, updated_by) VALUES
        ('dhruvtiwari756@gmail.com',             'Dhruv Tiwari (personal)',  'LBL-ADM-002', r_admin,    s_morning, TRUE,  TRUE,  u_super, u_super),
        ('dhruv.tiwari@globallogic.com',         'Dhruv Tiwari',             'LBL-ADM-003', r_admin,    s_morning, TRUE,  TRUE,  u_super, u_super),
        ('pulkit.srivastava2@globallogic.com',   'Pulkit Srivastava',        'LBL-ADM-004', r_admin,    s_morning, TRUE,  TRUE,  u_super, u_super),
        ('surajbhan.kumar@globallogic.com',      'Surajbhan Kumar',          'LBL-ADM-005', r_admin,    s_evening, TRUE,  TRUE,  u_super, u_super),
        ('ankita.jain3@globallogic.com',         'Ankita Jain',              'LBL-QA-006',  r_qa,       s_morning, TRUE,  TRUE,  u_super, u_super),
        ('priya.sharma@example.com',             'Priya Sharma',             'LBL-QA-007',  r_qa,       s_evening, TRUE,  TRUE,  u_super, u_super),
        ('rahul.verma@example.com',              'Rahul Verma',              'LBL-QA-008',  r_qa,       s_night,   TRUE,  TRUE,  u_super, u_super),
        ('tommyshelby2702@gmail.com',            'Tommy Shelby',             'LBL-REC-009', r_recorder, s_morning, TRUE,  TRUE,  u_super, u_super),
        ('aarav.patel@example.com',              'Aarav Patel',              'LBL-REC-010', r_recorder, s_morning, TRUE,  TRUE,  u_super, u_super),
        ('ishita.singh@example.com',             'Ishita Singh',             'LBL-REC-011', r_recorder, s_morning, TRUE,  TRUE,  u_super, u_super),
        ('kabir.malhotra@example.com',           'Kabir Malhotra',           'LBL-REC-012', r_recorder, s_evening, TRUE,  TRUE,  u_super, u_super),
        ('ananya.iyer@example.com',              'Ananya Iyer',              'LBL-REC-013', r_recorder, s_evening, TRUE,  TRUE,  u_super, u_super),
        ('vikram.reddy@example.com',             'Vikram Reddy',             'LBL-REC-014', r_recorder, s_evening, TRUE,  TRUE,  u_super, u_super),
        ('meera.nair@example.com',               'Meera Nair',               'LBL-REC-015', r_recorder, s_night,   TRUE,  TRUE,  u_super, u_super),
        ('arjun.gupta@example.com',              'Arjun Gupta',              'LBL-REC-016', r_recorder, s_night,   TRUE,  TRUE,  u_super, u_super),
        ('zara.khan@example.com',                'Zara Khan',                'LBL-REC-017', r_recorder, s_morning, FALSE, TRUE,  u_super, u_super)
    ON CONFLICT (email) DO NOTHING;

    SELECT user_id INTO u_adm1 FROM users WHERE email = 'dhruvtiwari756@gmail.com';
    SELECT user_id INTO u_adm2 FROM users WHERE email = 'dhruv.tiwari@globallogic.com';
    SELECT user_id INTO u_adm3 FROM users WHERE email = 'pulkit.srivastava2@globallogic.com';
    SELECT user_id INTO u_adm4 FROM users WHERE email = 'surajbhan.kumar@globallogic.com';
    SELECT user_id INTO u_qa1  FROM users WHERE email = 'ankita.jain3@globallogic.com';
    SELECT user_id INTO u_qa2  FROM users WHERE email = 'priya.sharma@example.com';
    SELECT user_id INTO u_qa3  FROM users WHERE email = 'rahul.verma@example.com';
    SELECT user_id INTO u_rec1 FROM users WHERE email = 'tommyshelby2702@gmail.com';
    SELECT user_id INTO u_rec2 FROM users WHERE email = 'aarav.patel@example.com';
    SELECT user_id INTO u_rec3 FROM users WHERE email = 'ishita.singh@example.com';
    SELECT user_id INTO u_rec4 FROM users WHERE email = 'kabir.malhotra@example.com';
    SELECT user_id INTO u_rec5 FROM users WHERE email = 'ananya.iyer@example.com';
    SELECT user_id INTO u_rec6 FROM users WHERE email = 'vikram.reddy@example.com';
    SELECT user_id INTO u_rec7 FROM users WHERE email = 'meera.nair@example.com';
    SELECT user_id INTO u_rec8 FROM users WHERE email = 'arjun.gupta@example.com';
    SELECT user_id INTO u_rec9 FROM users WHERE email = 'zara.khan@example.com';

    -- Tasks (idempotent by task_key)
    INSERT INTO tasks (
        task_key, category_id, environment, priority, task_type,
        title, description, task_script, estimated_time_minutes,
        status, is_active, created_by, updated_by
    ) VALUES
        ('T-001', c_cleaning, 'office',         'P1', 'general', 'Vacuum Living Room', 'Vacuum every accessible floor area of the living room including under low furniture.', 'Step 1: plug in vacuum. Step 2: cover all visible floor.', 6, 'approved', TRUE, u_adm1, u_adm1),
        ('T-002', c_cleaning, 'office',         'P2', 'general', 'Mop Bathroom Floor', 'Mop the bathroom floor with a mild detergent.', NULL, 5, 'approved', TRUE, u_adm1, u_adm1),
        ('T-003', c_cleaning, 'office',         'P2', 'general', 'Wipe Kitchen Counters', 'Wipe down all kitchen counters with a damp cloth.', NULL, 4, 'approved', TRUE, u_adm2, u_adm2),
        ('T-004', c_cleaning, 'office',         'P3', 'general', 'Dust Window Sills', 'Dust all window sills in the apartment using a microfiber cloth.', NULL, 3, 'draft',    TRUE, u_adm2, u_adm2),
        ('T-005', c_kitchen,  'office',         'P2', 'general', 'Brew Coffee', 'Use the espresso machine to brew a single cup of coffee.', 'Step 1: fill water tank. Step 2: insert pod. Step 3: press brew.', 4, 'approved', TRUE, u_adm3, u_adm3),
        ('T-006', c_kitchen,  'office',         'P2', 'niche',   'Slice Vegetables', 'Slice an assortment of vegetables to a uniform thickness.', NULL, 8, 'approved', TRUE, u_adm3, u_adm3),
        ('T-007', c_kitchen,  'office',         'P2', 'general', 'Wash Dishes', 'Wash a small load of dishes by hand.', NULL, 7, 'approved', TRUE, u_adm3, u_adm3),
        ('T-008', c_kitchen,  'office',         'P3', 'general', 'Set Dining Table', 'Set the table for two people with plates, glasses, and cutlery.', NULL, 5, 'approved', TRUE, u_adm4, u_adm4),
        ('T-009', c_home,     'office',         'P2', 'general', 'Make Bed', 'Make the bed neatly with fitted sheet, top sheet, and pillow.', NULL, 3, 'approved', TRUE, u_adm4, u_adm4),
        ('T-010', c_home,     'office',         'P3', 'general', 'Organize Bookshelf', 'Organize the bookshelf alphabetically by author.', NULL, 10, 'draft',    TRUE, u_adm4, u_adm4),
        ('T-011', c_office,   'office',         'P2', 'general', 'Tidy Office Desk', 'Tidy a single office desk: papers, stationery, monitor wipe.', NULL, 5, 'approved', TRUE, u_adm2, u_adm2),
        ('T-012', c_office,   'office',         'P3', 'niche',   'File Documents', 'File a stack of paper documents into a labeled cabinet.', NULL, 9, 'draft',    TRUE, u_adm2, u_adm2),
        ('T-013', c_retail,   'office/outdoor', 'P1', 'general', 'Restock Shelf', 'Restock a retail shelf from a backroom cart.', NULL, 8, 'approved', TRUE, u_adm3, u_adm3),
        ('T-014', c_retail,   'office',         'P2', 'general', 'Bag Items',    'Bag items at a checkout counter for a small purchase.', NULL, 4, 'approved', TRUE, u_adm3, u_adm3),
        ('T-015', c_retail,   'office',         'P2', 'niche',   'Greet Customer', 'Greet an arriving customer and offer assistance.', NULL, 2, 'rejected', TRUE, u_adm4, u_adm4)
    ON CONFLICT (task_key) DO NOTHING;

    SELECT task_id INTO t001 FROM tasks WHERE task_key = 'T-001';
    SELECT task_id INTO t002 FROM tasks WHERE task_key = 'T-002';
    SELECT task_id INTO t003 FROM tasks WHERE task_key = 'T-003';
    SELECT task_id INTO t004 FROM tasks WHERE task_key = 'T-004';
    SELECT task_id INTO t005 FROM tasks WHERE task_key = 'T-005';
    SELECT task_id INTO t006 FROM tasks WHERE task_key = 'T-006';
    SELECT task_id INTO t007 FROM tasks WHERE task_key = 'T-007';
    SELECT task_id INTO t008 FROM tasks WHERE task_key = 'T-008';
    SELECT task_id INTO t009 FROM tasks WHERE task_key = 'T-009';
    SELECT task_id INTO t010 FROM tasks WHERE task_key = 'T-010';
    SELECT task_id INTO t011 FROM tasks WHERE task_key = 'T-011';
    SELECT task_id INTO t012 FROM tasks WHERE task_key = 'T-012';
    SELECT task_id INTO t013 FROM tasks WHERE task_key = 'T-013';
    SELECT task_id INTO t014 FROM tasks WHERE task_key = 'T-014';
    SELECT task_id INTO t015 FROM tasks WHERE task_key = 'T-015';

    -- Recorder assignments (idempotent using WHERE NOT EXISTS)
    -- Insert each row conditionally
    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t001, u_rec1, u_adm1, CURRENT_DATE, s_morning, 'completed', NOW(), u_adm1, u_adm1
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t001 AND recorder_id = u_rec1 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t002, u_rec3, u_adm1, CURRENT_DATE, s_morning, 'completed', NOW(), u_adm1, u_adm1
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t002 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t005, u_rec8, u_adm3, CURRENT_DATE, s_night, 'completed', NOW(), u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t005 AND recorder_id = u_rec8 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t007, u_rec3, u_adm3, CURRENT_DATE - INTERVAL '1 day', s_morning, 'completed', NOW(), u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t007 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t011, u_rec7, u_adm2, CURRENT_DATE, s_night, 'completed', NOW(), u_adm2, u_adm2
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t011 AND recorder_id = u_rec7 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t003, u_rec5, u_adm2, CURRENT_DATE, s_evening, 'completed', NOW(), u_adm2, u_adm2
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t003 AND recorder_id = u_rec5 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t005, u_rec7, u_adm3, CURRENT_DATE, s_night, 'submitted', NULL, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t005 AND recorder_id = u_rec7 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t009, u_rec4, u_adm4, CURRENT_DATE, s_evening, 'submitted', NULL, u_adm4, u_adm4
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t009 AND recorder_id = u_rec4 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t003, u_rec4, u_adm2, CURRENT_DATE, s_evening, 'in_progress', NULL, u_adm2, u_adm2
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t003 AND recorder_id = u_rec4 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t006, u_rec9, u_adm3, CURRENT_DATE, s_morning, 'in_progress', NULL, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t006 AND recorder_id = u_rec9 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t001, u_rec2, u_adm1, CURRENT_DATE, s_morning, 'assigned', NULL, u_adm1, u_adm1
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t001 AND recorder_id = u_rec2 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t008, u_rec2, u_adm4, CURRENT_DATE, s_morning, 'assigned', NULL, u_adm4, u_adm4
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t008 AND recorder_id = u_rec2 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t010, u_rec6, u_adm4, CURRENT_DATE, s_evening, 'assigned', NULL, u_adm4, u_adm4
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t010 AND recorder_id = u_rec6 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t014, u_rec2, u_adm3, CURRENT_DATE, s_morning, 'assigned', NULL, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t014 AND recorder_id = u_rec2 AND assigned_date = CURRENT_DATE);

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t004, u_rec6, u_adm2, CURRENT_DATE - INTERVAL '1 day', s_evening, 'skipped', NULL, u_adm2, u_adm2
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t004 AND recorder_id = u_rec6 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t007, u_rec3, u_adm3, CURRENT_DATE - INTERVAL '2 days', s_morning, 'rejected', NULL, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t007 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE - INTERVAL '2 days');

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t015, u_rec3, u_adm4, CURRENT_DATE, s_morning, 'completed', NOW(), u_adm4, u_adm4
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t015 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE);

    -- Reassignment flow
    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t013, u_rec8, u_adm3, CURRENT_DATE - INTERVAL '2 days', s_night, 'reassigned', NULL, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t013 AND recorder_id = u_rec8 AND assigned_date = CURRENT_DATE - INTERVAL '2 days');

    SELECT recorder_assignment_id INTO a_arjun_t013
      FROM recorder_assignments
     WHERE task_id = t013 AND recorder_id = u_rec8
       AND assigned_date = CURRENT_DATE - INTERVAL '2 days';

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, reassigned_from_id, created_by, updated_by)
    SELECT t013, u_rec9, u_adm3, CURRENT_DATE - INTERVAL '1 day', s_morning, 'completed', NOW(), a_arjun_t013, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t013 AND recorder_id = u_rec9 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

    INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
    SELECT t009, u_rec4, u_adm4, CURRENT_DATE - INTERVAL '1 day', s_evening, 'completed', NOW(), u_adm4, u_adm4
    WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t009 AND recorder_id = u_rec4 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

    -- Recording logs (idempotent by assignment_id, with enum cast)
    INSERT INTO recording_logs (assignment_id, recorder_id, status, actual_time_minutes, comment, created_by, updated_by)
    SELECT a.recorder_assignment_id, a.recorder_id, v.status::recording_status_enum, v.minutes, v.comment, u_adm1, u_adm1
      FROM (VALUES
            (t001, u_rec1, CURRENT_DATE,                     'approved',       6, 'Completed without issues'),
            (t002, u_rec3, CURRENT_DATE,                     'approved',       5, 'Clean finish'),
            (t005, u_rec8, CURRENT_DATE,                     'approved',       4, 'Standard brew'),
            (t007, u_rec3, CURRENT_DATE - INTERVAL '1 day',  'approved',       7, 'All dishes washed'),
            (t011, u_rec7, CURRENT_DATE,                     'approved',       5, 'Desk fully tidied'),
            (t003, u_rec5, CURRENT_DATE,                     'pending_review', 4, 'Counters look good'),
            (t005, u_rec7, CURRENT_DATE,                     'pending_review', 5, 'Brewed during shift'),
            (t009, u_rec4, CURRENT_DATE,                     'rework_needed',  3, 'Sheet bunched up — please redo'),
            (t007, u_rec3, CURRENT_DATE - INTERVAL '2 days', 'rejected',       9, 'Several dishes still dirty'),
            (t013, u_rec9, CURRENT_DATE - INTERVAL '1 day',  'approved',       8, 'Shelf restocked cleanly'),
            (t009, u_rec4, CURRENT_DATE - INTERVAL '1 day',  'approved',       3, 'Bed made neatly'),
            (t015, u_rec3, CURRENT_DATE,                     'approved',       2, 'Friendly greeting captured')
           ) AS v(task_id, recorder_id, assigned_date, status, minutes, comment)
      JOIN recorder_assignments a
        ON a.task_id = v.task_id
       AND a.recorder_id = v.recorder_id
       AND a.assigned_date = v.assigned_date
    WHERE NOT EXISTS (SELECT 1 FROM recording_logs rl WHERE rl.assignment_id = a.recorder_assignment_id);

    -- Get recording_log_ids for later use
    SELECT rl.recording_log_id INTO rl_tommy_t001 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t001 AND a.recorder_id = u_rec1;
    SELECT rl.recording_log_id INTO rl_ishita_t002 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t002 AND a.recorder_id = u_rec3;
    SELECT rl.recording_log_id INTO rl_arjun_t005 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t005 AND a.recorder_id = u_rec8;
    SELECT rl.recording_log_id INTO rl_zara_t013 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t013 AND a.recorder_id = u_rec9;
    SELECT rl.recording_log_id INTO rl_kabir_t009 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t009 AND a.recorder_id = u_rec4 AND rl.status = 'rework_needed';
    SELECT rl.recording_log_id INTO rl_ishita_t007 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t007 AND a.recorder_id = u_rec3 AND rl.status = 'rejected';
    SELECT rl.recording_log_id INTO rl_meera_t011 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t011 AND a.recorder_id = u_rec7;
    SELECT rl.recording_log_id INTO rl_ananya_t003 FROM recording_logs rl
      JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
     WHERE a.task_id = t003 AND a.recorder_id = u_rec5;

    -- QA feedback (insert only once)
    IF (SELECT COUNT(*) FROM qa_feedback) = 0 THEN
        INSERT INTO qa_feedback (recording_log_id, qa_user_id, pass_rate,
                                 feedback_text, is_rework_required, feedback_category,
                                 created_by, updated_by)
        VALUES
            (rl_tommy_t001,  u_qa1, 95, 'Clean execution, all corners covered.',          FALSE, 'completeness', u_qa1, u_qa1),
            (rl_ishita_t002, u_qa1, 88, 'Floor mostly clean, minor streaks visible.',     FALSE, 'accuracy',     u_qa1, u_qa1),
            (rl_arjun_t005,  u_qa2, 92, 'Brew timing was on point.',                      FALSE, 'speed',        u_qa2, u_qa2),
            (rl_kabir_t009,  u_qa2, 55, 'Sheet not fully tucked. Please redo and resubmit.', TRUE,  'guidelines', u_qa2, u_qa2),
            (rl_ishita_t007, u_qa3, 40, 'Several dishes still had food residue. Rejected.', TRUE,  'accuracy',  u_qa3, u_qa3),
            (rl_meera_t011,  u_qa3, 90, 'Desk neat. Monitor wipe-down could be cleaner.',  FALSE, 'guidelines',   u_qa3, u_qa3);
    END IF;

    -- Task replications (idempotent by recording_log_id, environment_identifier)
    INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
    SELECT t001, rl_tommy_t001, 'office', 'apt-3B-living', u_adm1, u_adm1, u_adm1
    WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_tommy_t001 AND environment_identifier = 'apt-3B-living');
    INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
    SELECT t005, rl_arjun_t005, 'office', 'kitchen-pod-12', u_adm3, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_arjun_t005 AND environment_identifier = 'kitchen-pod-12');
    INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
    SELECT t011, rl_meera_t011, 'office', 'workstation-A', u_adm2, u_adm2, u_adm2
    WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_meera_t011 AND environment_identifier = 'workstation-A');
    INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
    SELECT t013, rl_zara_t013, 'office/outdoor', 'aisle-7-shelf-3', u_adm3, u_adm3, u_adm3
    WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_zara_t013 AND environment_identifier = 'aisle-7-shelf-3');

    -- Task comments (insert only once)
    IF (SELECT COUNT(*) FROM task_comments) = 0 THEN
        INSERT INTO task_comments (task_id, author_id, kind, body, status_from, status_to) VALUES
            (t001, u_adm1, 'created',       NULL,                                                NULL,     NULL),
            (t001, u_adm1, 'status_change', 'Approved after review',                             'draft',  'approved'),
            (t001, u_rec1, 'submitted',     'Vacuumed all reachable floor area, included under coffee table.', NULL, NULL),
            (t001, u_qa1,  'comment',       'Nice job — pass.',                                  NULL,     NULL),
            (t002, u_adm1, 'created',       NULL,                                                NULL,     NULL),
            (t002, u_rec3, 'submitted',     'Floor mopped. A few corner streaks remain.',        NULL,     NULL),
            (t002, u_qa1,  'comment',       'Marked needs minor improvement next time.',         NULL,     NULL),
            (t003, u_adm2, 'created',       NULL,                                                NULL,     NULL),
            (t003, u_rec5, 'submitted',     'Counters wiped, awaiting QA.',                      NULL,     NULL),
            (t004, u_adm2, 'created',       NULL,                                                NULL,     NULL),
            (t004, u_rec6, 'skip_requested','Microfiber cloth not available on site today.',     NULL,     NULL),
            (t004, u_adm2, 'skip_approved', 'Approved — please re-attempt tomorrow.',            NULL,     NULL),
            (t005, u_adm3, 'created',       NULL,                                                NULL,     NULL),
            (t005, u_rec8, 'submitted',     'Coffee brewed in 4 min.',                           NULL,     NULL),
            (t005, u_qa2,  'comment',       'Timing acceptable.',                                NULL,     NULL),
            (t007, u_adm3, 'created',       NULL,                                                NULL,     NULL),
            (t007, u_rec3, 'submitted',     'Dishes done.',                                      NULL,     NULL),
            (t007, u_qa3,  'comment',       'Rejected — residue visible on plates.',             NULL,     NULL),
            (t009, u_adm4, 'created',       NULL,                                                NULL,     NULL),
            (t009, u_rec4, 'submitted',     'Bed made, please review.',                          NULL,     NULL),
            (t009, u_qa2,  'comment',       'Sheet bunched — needs rework.',                     NULL,     NULL),
            (t011, u_adm2, 'created',       NULL,                                                NULL,     NULL),
            (t011, u_rec7, 'submitted',     'Desk tidied, monitor wiped.',                       NULL,     NULL),
            (t013, u_adm3, 'created',       NULL,                                                NULL,     NULL),
            (t013, u_adm3, 'assigned',      'Initially assigned to Arjun.',                      NULL,     NULL),
            (t013, u_adm3, 'comment',       'Reassigned to Zara after morning shift change.',    NULL,     NULL),
            (t013, u_rec9, 'submitted',     'Shelf restocked from backroom cart.',               NULL,     NULL),
            (t013, u_qa3,  'comment',       'Approved.',                                         NULL,     NULL),
            (t015, u_adm4, 'created',       NULL,                                                NULL,     NULL),
            (t015, u_adm4, 'status_change', 'Niche scenario - blocked pending data review.',    'draft',  'rejected');
    END IF;
END $$;

-- Final sequence realignment (redundant but safe)
SELECT setval(pg_get_serial_sequence('roles',  'role_id'),  COALESCE((SELECT MAX(role_id)  FROM roles),  1));
SELECT setval(pg_get_serial_sequence('shifts', 'shift_id'), COALESCE((SELECT MAX(shift_id) FROM shifts), 1));
SELECT setval(pg_get_serial_sequence('users',  'user_id'),  COALESCE((SELECT MAX(user_id)  FROM users),  1));
SELECT setval(pg_get_serial_sequence('task_categories', 'task_category_id'),
              COALESCE((SELECT MAX(task_category_id) FROM task_categories), 1));
SELECT setval(pg_get_serial_sequence('tasks', 'task_id'),
              COALESCE((SELECT MAX(task_id) FROM tasks), 1));
SELECT setval(pg_get_serial_sequence('recorder_assignments', 'recorder_assignment_id'),
              COALESCE((SELECT MAX(recorder_assignment_id) FROM recorder_assignments), 1));
SELECT setval(pg_get_serial_sequence('recording_logs', 'recording_log_id'),
              COALESCE((SELECT MAX(recording_log_id) FROM recording_logs), 1));
SELECT setval(pg_get_serial_sequence('task_replications', 'task_replication_id'),
              COALESCE((SELECT MAX(task_replication_id) FROM task_replications), 1));
SELECT setval(pg_get_serial_sequence('task_comments', 'id'),
              COALESCE((SELECT MAX(id) FROM task_comments), 1));
SELECT setval(pg_get_serial_sequence('qa_feedback', 'qa_feedback_id'),
              COALESCE((SELECT MAX(qa_feedback_id) FROM qa_feedback), 1));

COMMIT;




=====================================================================
SEED: bootstrap roles, shifts, and a super_admin user.
Runs AFTER schema.sql but BEFORE alter.sql
Every statement is idempotent.
=====================================================================












-- commenting as this is filling role-permission as permissions are getting created from backend code and we want to avoid conflicts. We can uncomment this if we want to seed some default roles and permissions in the future.
-- commenting as this is filling role-permission as permissions are getting created from backend code and we want to avoid conflicts. We can uncomment this if we want to seed some default roles and permissions in the future.
-- commenting as this is filling role-permission as permissions are getting created from backend code and we want to avoid conflicts. We can uncomment this if we want to seed some default roles and permissions in the future.
-- commenting as this is filling role-permission as permissions are getting created from backend code and we want to avoid conflicts. We can uncomment this if we want to seed some default roles and permissions in the future.

-- commenting as this is filling role-permission as permissions are getting created from backend code and we want to avoid conflicts. We can uncomment this if we want to seed some default roles and permissions in the future.
















-- BEGIN;

-- -- Roles ---------------------------------------------------------------
-- INSERT INTO roles (role_id, name, description,
--                    can_assign_tasks, can_create_tasks, can_review_quality,
--                    can_manage_users, can_view_reports,
--                    created_by, updated_by)
-- VALUES (1, 'super_admin', 'Full system access',
--         TRUE, TRUE, TRUE, TRUE, TRUE, 1, 1)
-- ON CONFLICT (role_id) DO NOTHING;

-- SELECT setval(pg_get_serial_sequence('roles', 'role_id'),
--               COALESCE((SELECT MAX(role_id) FROM roles), 1));

-- INSERT INTO roles (name, description,
--                    can_assign_tasks, can_create_tasks, can_review_quality,
--                    can_manage_users, can_view_reports,
--                    created_by, updated_by)
-- SELECT 'admin', 'Administrator',
--        TRUE, TRUE, TRUE, TRUE, TRUE, 1, 1
-- WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'admin');

-- INSERT INTO roles (name, description,
--                    can_assign_tasks, can_create_tasks, can_review_quality,
--                    can_manage_users, can_view_reports,
--                    created_by, updated_by)
-- SELECT 'qa', 'Quality assurance reviewer',
--        FALSE, FALSE, TRUE, FALSE, TRUE, 1, 1
-- WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'qa');

-- INSERT INTO roles (name, description,
--                    can_assign_tasks, can_create_tasks, can_review_quality,
--                    can_manage_users, can_view_reports,
--                    created_by, updated_by)
-- SELECT 'recorder', 'Recorder',
--        FALSE, FALSE, FALSE, FALSE, FALSE, 1, 1
-- WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = 'recorder');

-- -- Shifts --------------------------------------------------------------
-- INSERT INTO shifts (shift_id, name, start_time, end_time, description,
--                     is_active, created_by, updated_by)
-- VALUES (1, 'morning', '06:00', '14:00', 'Morning shift', TRUE, 1, 1)
-- ON CONFLICT (shift_id) DO NOTHING;

-- SELECT setval(pg_get_serial_sequence('shifts', 'shift_id'),
--               COALESCE((SELECT MAX(shift_id) FROM shifts), 1));

-- INSERT INTO shifts (name, start_time, end_time, description,
--                     is_active, created_by, updated_by)
-- SELECT 'evening', '14:00', '22:00', 'Evening shift', TRUE, 1, 1
-- WHERE NOT EXISTS (SELECT 1 FROM shifts WHERE name = 'evening');

-- INSERT INTO shifts (name, start_time, end_time, description,
--                     is_active, created_by, updated_by)
-- SELECT 'night', '22:00', '06:00', 'Night shift', TRUE, 1, 1
-- WHERE NOT EXISTS (SELECT 1 FROM shifts WHERE name = 'night');

-- -- Bootstrap super_admin user (user_id = 1)
-- INSERT INTO users (user_id, email, name, labeller_id,
--                    role_id, shift_id,
--                    is_approved, is_active,
--                    created_by, updated_by)
-- VALUES (1, 'dhruvtiwari756placement@gmail.com', 'Super Admin', 'ADMIN-0001',
--         (SELECT role_id FROM roles WHERE name = 'super_admin'),
--         (SELECT shift_id FROM shifts WHERE name = 'morning'),
--         TRUE, TRUE, 1, 1)
-- ON CONFLICT (user_id) DO UPDATE SET
--     email = EXCLUDED.email,
--     name = EXCLUDED.name,
--     labeller_id = EXCLUDED.labeller_id,
--     role_id = EXCLUDED.role_id,
--     shift_id = EXCLUDED.shift_id,
--     is_approved = EXCLUDED.is_approved,
--     is_active = EXCLUDED.is_active,
--     updated_by = EXCLUDED.updated_by,
--     updated_at = now();

-- SELECT setval(pg_get_serial_sequence('users', 'user_id'),
--               COALESCE((SELECT MAX(user_id) FROM users), 1));

-- -- =====================================================================
-- -- MOCK DATA  (idempotent; safe to re-run on every container start)
-- -- =====================================================================
-- DO $$
-- DECLARE
--     r_admin    BIGINT;
--     r_qa       BIGINT;
--     r_recorder BIGINT;
--     s_morning  BIGINT;
--     s_evening  BIGINT;
--     s_night    BIGINT;

--     c_cleaning BIGINT;
--     c_kitchen  BIGINT;
--     c_home     BIGINT;
--     c_office   BIGINT;
--     c_retail   BIGINT;

--     u_super  BIGINT := 1;
--     u_adm1   BIGINT;  u_adm2 BIGINT;  u_adm3 BIGINT;  u_adm4 BIGINT;
--     u_qa1    BIGINT;  u_qa2  BIGINT;  u_qa3  BIGINT;
--     u_rec1   BIGINT;  u_rec2 BIGINT;  u_rec3 BIGINT;  u_rec4 BIGINT;
--     u_rec5   BIGINT;  u_rec6 BIGINT;  u_rec7 BIGINT;  u_rec8 BIGINT;
--     u_rec9   BIGINT;

--     t001 BIGINT; t002 BIGINT; t003 BIGINT; t004 BIGINT; t005 BIGINT;
--     t006 BIGINT; t007 BIGINT; t008 BIGINT; t009 BIGINT; t010 BIGINT;
--     t011 BIGINT; t012 BIGINT; t013 BIGINT; t014 BIGINT; t015 BIGINT;

--     a_arjun_t013 BIGINT;
--     rl_tommy_t001 BIGINT;
--     rl_ishita_t002 BIGINT;
--     rl_arjun_t005 BIGINT;
--     rl_zara_t013  BIGINT;
--     rl_kabir_t009 BIGINT;
--     rl_ishita_t007 BIGINT;
--     rl_meera_t011 BIGINT;
--     rl_ananya_t003 BIGINT;
-- BEGIN
--     -- Lookups
--     SELECT role_id INTO r_admin    FROM roles WHERE name = 'admin';
--     SELECT role_id INTO r_qa       FROM roles WHERE name = 'qa';
--     SELECT role_id INTO r_recorder FROM roles WHERE name = 'recorder';
--     SELECT shift_id INTO s_morning FROM shifts WHERE name = 'morning';
--     SELECT shift_id INTO s_evening FROM shifts WHERE name = 'evening';
--     SELECT shift_id INTO s_night   FROM shifts WHERE name = 'night';

--     -- Task categories (idempotent by name)
--     INSERT INTO task_categories (name, description, created_by, updated_by) VALUES
--         ('cleaning',             'General cleaning tasks across spaces',          u_super, u_super),
--         ('kitchen_and_food',     'Kitchen prep, cooking, and food handling',      u_super, u_super),
--         ('home_spaces',          'Home space tidying and organization',           u_super, u_super),
--         ('office_and_workspace', 'Office and desk organization',                  u_super, u_super),
--         ('retail_operations',    'Retail floor and customer-facing operations',   u_super, u_super)
--     ON CONFLICT (name) DO NOTHING;

--     SELECT task_category_id INTO c_cleaning FROM task_categories WHERE name = 'cleaning';
--     SELECT task_category_id INTO c_kitchen  FROM task_categories WHERE name = 'kitchen_and_food';
--     SELECT task_category_id INTO c_home     FROM task_categories WHERE name = 'home_spaces';
--     SELECT task_category_id INTO c_office   FROM task_categories WHERE name = 'office_and_workspace';
--     SELECT task_category_id INTO c_retail   FROM task_categories WHERE name = 'retail_operations';

--     -- Users (idempotent by email)
--     INSERT INTO users (email, name, labeller_id, role_id, shift_id, is_approved, is_active, created_by, updated_by) VALUES
--         ('dhruvtiwari756@gmail.com',             'Dhruv Tiwari (personal)',  'LBL-ADM-002', r_admin,    s_morning, TRUE,  TRUE,  u_super, u_super),
--         ('dhruv.tiwari@globallogic.com',         'Dhruv Tiwari',             'LBL-ADM-003', r_admin,    s_morning, TRUE,  TRUE,  u_super, u_super),
--         ('pulkit.srivastava2@globallogic.com',   'Pulkit Srivastava',        'LBL-ADM-004', r_admin,    s_morning, TRUE,  TRUE,  u_super, u_super),
--         ('surajbhan.kumar@globallogic.com',      'Surajbhan Kumar',          'LBL-ADM-005', r_admin,    s_evening, TRUE,  TRUE,  u_super, u_super),
--         ('ankita.jain3@globallogic.com',         'Ankita Jain',              'LBL-QA-006',  r_qa,       s_morning, TRUE,  TRUE,  u_super, u_super),
--         ('priya.sharma@example.com',             'Priya Sharma',             'LBL-QA-007',  r_qa,       s_evening, TRUE,  TRUE,  u_super, u_super),
--         ('rahul.verma@example.com',              'Rahul Verma',              'LBL-QA-008',  r_qa,       s_night,   TRUE,  TRUE,  u_super, u_super),
--         ('tommyshelby2702@gmail.com',            'Tommy Shelby',             'LBL-REC-009', r_recorder, s_morning, TRUE,  TRUE,  u_super, u_super),
--         ('aarav.patel@example.com',              'Aarav Patel',              'LBL-REC-010', r_recorder, s_morning, TRUE,  TRUE,  u_super, u_super),
--         ('ishita.singh@example.com',             'Ishita Singh',             'LBL-REC-011', r_recorder, s_morning, TRUE,  TRUE,  u_super, u_super),
--         ('kabir.malhotra@example.com',           'Kabir Malhotra',           'LBL-REC-012', r_recorder, s_evening, TRUE,  TRUE,  u_super, u_super),
--         ('ananya.iyer@example.com',              'Ananya Iyer',              'LBL-REC-013', r_recorder, s_evening, TRUE,  TRUE,  u_super, u_super),
--         ('vikram.reddy@example.com',             'Vikram Reddy',             'LBL-REC-014', r_recorder, s_evening, TRUE,  TRUE,  u_super, u_super),
--         ('meera.nair@example.com',               'Meera Nair',               'LBL-REC-015', r_recorder, s_night,   TRUE,  TRUE,  u_super, u_super),
--         ('arjun.gupta@example.com',              'Arjun Gupta',              'LBL-REC-016', r_recorder, s_night,   TRUE,  TRUE,  u_super, u_super),
--         ('zara.khan@example.com',                'Zara Khan',                'LBL-REC-017', r_recorder, s_morning, FALSE, TRUE,  u_super, u_super)
--     ON CONFLICT (email) DO NOTHING;

--     SELECT user_id INTO u_adm1 FROM users WHERE email = 'dhruvtiwari756@gmail.com';
--     SELECT user_id INTO u_adm2 FROM users WHERE email = 'dhruv.tiwari@globallogic.com';
--     SELECT user_id INTO u_adm3 FROM users WHERE email = 'pulkit.srivastava2@globallogic.com';
--     SELECT user_id INTO u_adm4 FROM users WHERE email = 'surajbhan.kumar@globallogic.com';
--     SELECT user_id INTO u_qa1  FROM users WHERE email = 'ankita.jain3@globallogic.com';
--     SELECT user_id INTO u_qa2  FROM users WHERE email = 'priya.sharma@example.com';
--     SELECT user_id INTO u_qa3  FROM users WHERE email = 'rahul.verma@example.com';
--     SELECT user_id INTO u_rec1 FROM users WHERE email = 'tommyshelby2702@gmail.com';
--     SELECT user_id INTO u_rec2 FROM users WHERE email = 'aarav.patel@example.com';
--     SELECT user_id INTO u_rec3 FROM users WHERE email = 'ishita.singh@example.com';
--     SELECT user_id INTO u_rec4 FROM users WHERE email = 'kabir.malhotra@example.com';
--     SELECT user_id INTO u_rec5 FROM users WHERE email = 'ananya.iyer@example.com';
--     SELECT user_id INTO u_rec6 FROM users WHERE email = 'vikram.reddy@example.com';
--     SELECT user_id INTO u_rec7 FROM users WHERE email = 'meera.nair@example.com';
--     SELECT user_id INTO u_rec8 FROM users WHERE email = 'arjun.gupta@example.com';
--     SELECT user_id INTO u_rec9 FROM users WHERE email = 'zara.khan@example.com';

--     -- Tasks (idempotent by task_key)
--     INSERT INTO tasks (
--         task_key, category_id, environment, priority, task_type,
--         title, description, task_script, estimated_time_minutes,
--         status, is_active, created_by, updated_by
--     ) VALUES
--         ('T-001', c_cleaning, 'office',         'P1', 'general', 'Vacuum Living Room', 'Vacuum every accessible floor area of the living room including under low furniture.', 'Step 1: plug in vacuum. Step 2: cover all visible floor.', 6, 'approved', TRUE, u_adm1, u_adm1),
--         ('T-002', c_cleaning, 'office',         'P2', 'general', 'Mop Bathroom Floor', 'Mop the bathroom floor with a mild detergent.', NULL, 5, 'approved', TRUE, u_adm1, u_adm1),
--         ('T-003', c_cleaning, 'office',         'P2', 'general', 'Wipe Kitchen Counters', 'Wipe down all kitchen counters with a damp cloth.', NULL, 4, 'approved', TRUE, u_adm2, u_adm2),
--         ('T-004', c_cleaning, 'office',         'P3', 'general', 'Dust Window Sills', 'Dust all window sills in the apartment using a microfiber cloth.', NULL, 3, 'draft',    TRUE, u_adm2, u_adm2),
--         ('T-005', c_kitchen,  'office',         'P2', 'general', 'Brew Coffee', 'Use the espresso machine to brew a single cup of coffee.', 'Step 1: fill water tank. Step 2: insert pod. Step 3: press brew.', 4, 'approved', TRUE, u_adm3, u_adm3),
--         ('T-006', c_kitchen,  'office',         'P2', 'niche',   'Slice Vegetables', 'Slice an assortment of vegetables to a uniform thickness.', NULL, 8, 'approved', TRUE, u_adm3, u_adm3),
--         ('T-007', c_kitchen,  'office',         'P2', 'general', 'Wash Dishes', 'Wash a small load of dishes by hand.', NULL, 7, 'approved', TRUE, u_adm3, u_adm3),
--         ('T-008', c_kitchen,  'office',         'P3', 'general', 'Set Dining Table', 'Set the table for two people with plates, glasses, and cutlery.', NULL, 5, 'approved', TRUE, u_adm4, u_adm4),
--         ('T-009', c_home,     'office',         'P2', 'general', 'Make Bed', 'Make the bed neatly with fitted sheet, top sheet, and pillow.', NULL, 3, 'approved', TRUE, u_adm4, u_adm4),
--         ('T-010', c_home,     'office',         'P3', 'general', 'Organize Bookshelf', 'Organize the bookshelf alphabetically by author.', NULL, 10, 'draft',    TRUE, u_adm4, u_adm4),
--         ('T-011', c_office,   'office',         'P2', 'general', 'Tidy Office Desk', 'Tidy a single office desk: papers, stationery, monitor wipe.', NULL, 5, 'approved', TRUE, u_adm2, u_adm2),
--         ('T-012', c_office,   'office',         'P3', 'niche',   'File Documents', 'File a stack of paper documents into a labeled cabinet.', NULL, 9, 'draft',    TRUE, u_adm2, u_adm2),
--         ('T-013', c_retail,   'office/outdoor', 'P1', 'general', 'Restock Shelf', 'Restock a retail shelf from a backroom cart.', NULL, 8, 'approved', TRUE, u_adm3, u_adm3),
--         ('T-014', c_retail,   'office',         'P2', 'general', 'Bag Items',    'Bag items at a checkout counter for a small purchase.', NULL, 4, 'approved', TRUE, u_adm3, u_adm3),
--         ('T-015', c_retail,   'office',         'P2', 'niche',   'Greet Customer', 'Greet an arriving customer and offer assistance.', NULL, 2, 'rejected', TRUE, u_adm4, u_adm4)
--     ON CONFLICT (task_key) DO NOTHING;

--     SELECT task_id INTO t001 FROM tasks WHERE task_key = 'T-001';
--     SELECT task_id INTO t002 FROM tasks WHERE task_key = 'T-002';
--     SELECT task_id INTO t003 FROM tasks WHERE task_key = 'T-003';
--     SELECT task_id INTO t004 FROM tasks WHERE task_key = 'T-004';
--     SELECT task_id INTO t005 FROM tasks WHERE task_key = 'T-005';
--     SELECT task_id INTO t006 FROM tasks WHERE task_key = 'T-006';
--     SELECT task_id INTO t007 FROM tasks WHERE task_key = 'T-007';
--     SELECT task_id INTO t008 FROM tasks WHERE task_key = 'T-008';
--     SELECT task_id INTO t009 FROM tasks WHERE task_key = 'T-009';
--     SELECT task_id INTO t010 FROM tasks WHERE task_key = 'T-010';
--     SELECT task_id INTO t011 FROM tasks WHERE task_key = 'T-011';
--     SELECT task_id INTO t012 FROM tasks WHERE task_key = 'T-012';
--     SELECT task_id INTO t013 FROM tasks WHERE task_key = 'T-013';
--     SELECT task_id INTO t014 FROM tasks WHERE task_key = 'T-014';
--     SELECT task_id INTO t015 FROM tasks WHERE task_key = 'T-015';

--     -- Recorder assignments (idempotent using WHERE NOT EXISTS)
--     -- Insert each row conditionally
--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t001, u_rec1, u_adm1, CURRENT_DATE, s_morning, 'completed', NOW(), u_adm1, u_adm1
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t001 AND recorder_id = u_rec1 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t002, u_rec3, u_adm1, CURRENT_DATE, s_morning, 'completed', NOW(), u_adm1, u_adm1
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t002 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t005, u_rec8, u_adm3, CURRENT_DATE, s_night, 'completed', NOW(), u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t005 AND recorder_id = u_rec8 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t007, u_rec3, u_adm3, CURRENT_DATE - INTERVAL '1 day', s_morning, 'completed', NOW(), u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t007 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t011, u_rec7, u_adm2, CURRENT_DATE, s_night, 'completed', NOW(), u_adm2, u_adm2
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t011 AND recorder_id = u_rec7 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t003, u_rec5, u_adm2, CURRENT_DATE, s_evening, 'completed', NOW(), u_adm2, u_adm2
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t003 AND recorder_id = u_rec5 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t005, u_rec7, u_adm3, CURRENT_DATE, s_night, 'submitted', NULL, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t005 AND recorder_id = u_rec7 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t009, u_rec4, u_adm4, CURRENT_DATE, s_evening, 'submitted', NULL, u_adm4, u_adm4
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t009 AND recorder_id = u_rec4 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t003, u_rec4, u_adm2, CURRENT_DATE, s_evening, 'in_progress', NULL, u_adm2, u_adm2
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t003 AND recorder_id = u_rec4 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t006, u_rec9, u_adm3, CURRENT_DATE, s_morning, 'in_progress', NULL, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t006 AND recorder_id = u_rec9 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t001, u_rec2, u_adm1, CURRENT_DATE, s_morning, 'assigned', NULL, u_adm1, u_adm1
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t001 AND recorder_id = u_rec2 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t008, u_rec2, u_adm4, CURRENT_DATE, s_morning, 'assigned', NULL, u_adm4, u_adm4
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t008 AND recorder_id = u_rec2 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t010, u_rec6, u_adm4, CURRENT_DATE, s_evening, 'assigned', NULL, u_adm4, u_adm4
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t010 AND recorder_id = u_rec6 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t014, u_rec2, u_adm3, CURRENT_DATE, s_morning, 'assigned', NULL, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t014 AND recorder_id = u_rec2 AND assigned_date = CURRENT_DATE);

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t004, u_rec6, u_adm2, CURRENT_DATE - INTERVAL '1 day', s_evening, 'skipped', NULL, u_adm2, u_adm2
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t004 AND recorder_id = u_rec6 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t007, u_rec3, u_adm3, CURRENT_DATE - INTERVAL '2 days', s_morning, 'rejected', NULL, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t007 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE - INTERVAL '2 days');

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t015, u_rec3, u_adm4, CURRENT_DATE, s_morning, 'completed', NOW(), u_adm4, u_adm4
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t015 AND recorder_id = u_rec3 AND assigned_date = CURRENT_DATE);

--     -- Reassignment flow
--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t013, u_rec8, u_adm3, CURRENT_DATE - INTERVAL '2 days', s_night, 'reassigned', NULL, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t013 AND recorder_id = u_rec8 AND assigned_date = CURRENT_DATE - INTERVAL '2 days');

--     SELECT recorder_assignment_id INTO a_arjun_t013
--       FROM recorder_assignments
--      WHERE task_id = t013 AND recorder_id = u_rec8
--        AND assigned_date = CURRENT_DATE - INTERVAL '2 days';

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, reassigned_from_id, created_by, updated_by)
--     SELECT t013, u_rec9, u_adm3, CURRENT_DATE - INTERVAL '1 day', s_morning, 'completed', NOW(), a_arjun_t013, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t013 AND recorder_id = u_rec9 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

--     INSERT INTO recorder_assignments (task_id, recorder_id, assigned_by, assigned_date, shift_id, status, completed_at, created_by, updated_by)
--     SELECT t009, u_rec4, u_adm4, CURRENT_DATE - INTERVAL '1 day', s_evening, 'completed', NOW(), u_adm4, u_adm4
--     WHERE NOT EXISTS (SELECT 1 FROM recorder_assignments WHERE task_id = t009 AND recorder_id = u_rec4 AND assigned_date = CURRENT_DATE - INTERVAL '1 day');

--     -- Recording logs (idempotent by assignment_id, with enum cast)
--     INSERT INTO recording_logs (assignment_id, recorder_id, status, actual_time_minutes, comment, created_by, updated_by)
--     SELECT a.recorder_assignment_id, a.recorder_id, v.status::recording_status_enum, v.minutes, v.comment, u_adm1, u_adm1
--       FROM (VALUES
--             (t001, u_rec1, CURRENT_DATE,                     'approved',       6, 'Completed without issues'),
--             (t002, u_rec3, CURRENT_DATE,                     'approved',       5, 'Clean finish'),
--             (t005, u_rec8, CURRENT_DATE,                     'approved',       4, 'Standard brew'),
--             (t007, u_rec3, CURRENT_DATE - INTERVAL '1 day',  'approved',       7, 'All dishes washed'),
--             (t011, u_rec7, CURRENT_DATE,                     'approved',       5, 'Desk fully tidied'),
--             (t003, u_rec5, CURRENT_DATE,                     'pending_review', 4, 'Counters look good'),
--             (t005, u_rec7, CURRENT_DATE,                     'pending_review', 5, 'Brewed during shift'),
--             (t009, u_rec4, CURRENT_DATE,                     'rework_needed',  3, 'Sheet bunched up — please redo'),
--             (t007, u_rec3, CURRENT_DATE - INTERVAL '2 days', 'rejected',       9, 'Several dishes still dirty'),
--             (t013, u_rec9, CURRENT_DATE - INTERVAL '1 day',  'approved',       8, 'Shelf restocked cleanly'),
--             (t009, u_rec4, CURRENT_DATE - INTERVAL '1 day',  'approved',       3, 'Bed made neatly'),
--             (t015, u_rec3, CURRENT_DATE,                     'approved',       2, 'Friendly greeting captured')
--            ) AS v(task_id, recorder_id, assigned_date, status, minutes, comment)
--       JOIN recorder_assignments a
--         ON a.task_id = v.task_id
--        AND a.recorder_id = v.recorder_id
--        AND a.assigned_date = v.assigned_date
--     WHERE NOT EXISTS (SELECT 1 FROM recording_logs rl WHERE rl.assignment_id = a.recorder_assignment_id);

--     -- Get recording_log_ids for later use
--     SELECT rl.recording_log_id INTO rl_tommy_t001 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t001 AND a.recorder_id = u_rec1;
--     SELECT rl.recording_log_id INTO rl_ishita_t002 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t002 AND a.recorder_id = u_rec3;
--     SELECT rl.recording_log_id INTO rl_arjun_t005 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t005 AND a.recorder_id = u_rec8;
--     SELECT rl.recording_log_id INTO rl_zara_t013 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t013 AND a.recorder_id = u_rec9;
--     SELECT rl.recording_log_id INTO rl_kabir_t009 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t009 AND a.recorder_id = u_rec4 AND rl.status = 'rework_needed';
--     SELECT rl.recording_log_id INTO rl_ishita_t007 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t007 AND a.recorder_id = u_rec3 AND rl.status = 'rejected';
--     SELECT rl.recording_log_id INTO rl_meera_t011 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t011 AND a.recorder_id = u_rec7;
--     SELECT rl.recording_log_id INTO rl_ananya_t003 FROM recording_logs rl
--       JOIN recorder_assignments a ON a.recorder_assignment_id = rl.assignment_id
--      WHERE a.task_id = t003 AND a.recorder_id = u_rec5;

--     -- QA feedback (insert only once)
--     IF (SELECT COUNT(*) FROM qa_feedback) = 0 THEN
--         INSERT INTO qa_feedback (recording_log_id, qa_user_id, pass_rate,
--                                  feedback_text, is_rework_required, feedback_category,
--                                  created_by, updated_by)
--         VALUES
--             (rl_tommy_t001,  u_qa1, 95, 'Clean execution, all corners covered.',          FALSE, 'completeness', u_qa1, u_qa1),
--             (rl_ishita_t002, u_qa1, 88, 'Floor mostly clean, minor streaks visible.',     FALSE, 'accuracy',     u_qa1, u_qa1),
--             (rl_arjun_t005,  u_qa2, 92, 'Brew timing was on point.',                      FALSE, 'speed',        u_qa2, u_qa2),
--             (rl_kabir_t009,  u_qa2, 55, 'Sheet not fully tucked. Please redo and resubmit.', TRUE,  'guidelines', u_qa2, u_qa2),
--             (rl_ishita_t007, u_qa3, 40, 'Several dishes still had food residue. Rejected.', TRUE,  'accuracy',  u_qa3, u_qa3),
--             (rl_meera_t011,  u_qa3, 90, 'Desk neat. Monitor wipe-down could be cleaner.',  FALSE, 'guidelines',   u_qa3, u_qa3);
--     END IF;

--     -- Task replications (idempotent by recording_log_id, environment_identifier)
--     INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
--     SELECT t001, rl_tommy_t001, 'office', 'apt-3B-living', u_adm1, u_adm1, u_adm1
--     WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_tommy_t001 AND environment_identifier = 'apt-3B-living');
--     INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
--     SELECT t005, rl_arjun_t005, 'office', 'kitchen-pod-12', u_adm3, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_arjun_t005 AND environment_identifier = 'kitchen-pod-12');
--     INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
--     SELECT t011, rl_meera_t011, 'office', 'workstation-A', u_adm2, u_adm2, u_adm2
--     WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_meera_t011 AND environment_identifier = 'workstation-A');
--     INSERT INTO task_replications (original_task_id, recording_log_id, environment_type, environment_identifier, replicated_by, created_by, updated_by)
--     SELECT t013, rl_zara_t013, 'office/outdoor', 'aisle-7-shelf-3', u_adm3, u_adm3, u_adm3
--     WHERE NOT EXISTS (SELECT 1 FROM task_replications WHERE recording_log_id = rl_zara_t013 AND environment_identifier = 'aisle-7-shelf-3');

--     -- Task comments (insert only once)
--     IF (SELECT COUNT(*) FROM task_comments) = 0 THEN
--         INSERT INTO task_comments (task_id, author_id, kind, body, status_from, status_to) VALUES
--             (t001, u_adm1, 'created',       NULL,                                                NULL,     NULL),
--             (t001, u_adm1, 'status_change', 'Approved after review',                             'draft',  'approved'),
--             (t001, u_rec1, 'submitted',     'Vacuumed all reachable floor area, included under coffee table.', NULL, NULL),
--             (t001, u_qa1,  'comment',       'Nice job — pass.',                                  NULL,     NULL),
--             (t002, u_adm1, 'created',       NULL,                                                NULL,     NULL),
--             (t002, u_rec3, 'submitted',     'Floor mopped. A few corner streaks remain.',        NULL,     NULL),
--             (t002, u_qa1,  'comment',       'Marked needs minor improvement next time.',         NULL,     NULL),
--             (t003, u_adm2, 'created',       NULL,                                                NULL,     NULL),
--             (t003, u_rec5, 'submitted',     'Counters wiped, awaiting QA.',                      NULL,     NULL),
--             (t004, u_adm2, 'created',       NULL,                                                NULL,     NULL),
--             (t004, u_rec6, 'skip_requested','Microfiber cloth not available on site today.',     NULL,     NULL),
--             (t004, u_adm2, 'skip_approved', 'Approved — please re-attempt tomorrow.',            NULL,     NULL),
--             (t005, u_adm3, 'created',       NULL,                                                NULL,     NULL),
--             (t005, u_rec8, 'submitted',     'Coffee brewed in 4 min.',                           NULL,     NULL),
--             (t005, u_qa2,  'comment',       'Timing acceptable.',                                NULL,     NULL),
--             (t007, u_adm3, 'created',       NULL,                                                NULL,     NULL),
--             (t007, u_rec3, 'submitted',     'Dishes done.',                                      NULL,     NULL),
--             (t007, u_qa3,  'comment',       'Rejected — residue visible on plates.',             NULL,     NULL),
--             (t009, u_adm4, 'created',       NULL,                                                NULL,     NULL),
--             (t009, u_rec4, 'submitted',     'Bed made, please review.',                          NULL,     NULL),
--             (t009, u_qa2,  'comment',       'Sheet bunched — needs rework.',                     NULL,     NULL),
--             (t011, u_adm2, 'created',       NULL,                                                NULL,     NULL),
--             (t011, u_rec7, 'submitted',     'Desk tidied, monitor wiped.',                       NULL,     NULL),
--             (t013, u_adm3, 'created',       NULL,                                                NULL,     NULL),
--             (t013, u_adm3, 'assigned',      'Initially assigned to Arjun.',                      NULL,     NULL),
--             (t013, u_adm3, 'comment',       'Reassigned to Zara after morning shift change.',    NULL,     NULL),
--             (t013, u_rec9, 'submitted',     'Shelf restocked from backroom cart.',               NULL,     NULL),
--             (t013, u_qa3,  'comment',       'Approved.',                                         NULL,     NULL),
--             (t015, u_adm4, 'created',       NULL,                                                NULL,     NULL),
--             (t015, u_adm4, 'status_change', 'Niche scenario - blocked pending data review.',    'draft',  'rejected');
--     END IF;

--     -- Role permissions (idempotent: only insert if mapping doesn't exist)
--     -- Ensure standard permissions exist first
--     INSERT INTO permissions (code, description, created_by, updated_by) VALUES
--         ('manage_all',       'Full system access',      1, 1),
--         ('admin_privileges', 'Administrative rights',   1, 1),
--         ('review_tasks',     'Can review and QA tasks', 1, 1),
--         ('record_tasks',     'Can record task results', 1, 1)
--     ON CONFLICT (code) DO NOTHING;

--     -- Then assign permissions to roles
--     INSERT INTO role_permissions (role_id, permission_id, is_active, created_by, updated_by)
--     SELECT r.role_id, p.permission_id, TRUE, 1, 1
--     FROM (VALUES
--         ('super_admin', 'manage_all'),
--         ('admin',        'admin_privileges'),
--         ('qa',           'review_tasks'),
--         ('recorder',     'record_tasks')
--     ) AS v(role_name, perm_code)
--     JOIN roles r ON r.name = v.role_name::role_name_enum
--     JOIN permissions p ON p.code = v.perm_code
--     WHERE NOT EXISTS (
--         SELECT 1 FROM role_permissions rp
--         WHERE rp.role_id = r.role_id AND rp.permission_id = p.permission_id
--     );
-- END $$;

-- -- Final sequence realignment (redundant but safe)
-- SELECT setval(pg_get_serial_sequence('roles',  'role_id'),  COALESCE((SELECT MAX(role_id)  FROM roles),  1));
-- SELECT setval(pg_get_serial_sequence('shifts', 'shift_id'), COALESCE((SELECT MAX(shift_id) FROM shifts), 1));
-- SELECT setval(pg_get_serial_sequence('users',  'user_id'),  COALESCE((SELECT MAX(user_id)  FROM users),  1));
-- SELECT setval(pg_get_serial_sequence('task_categories', 'task_category_id'),
--               COALESCE((SELECT MAX(task_category_id) FROM task_categories), 1));
-- SELECT setval(pg_get_serial_sequence('tasks', 'task_id'),
--               COALESCE((SELECT MAX(task_id) FROM tasks), 1));
-- SELECT setval(pg_get_serial_sequence('recorder_assignments', 'recorder_assignment_id'),
--               COALESCE((SELECT MAX(recorder_assignment_id) FROM recorder_assignments), 1));
-- SELECT setval(pg_get_serial_sequence('recording_logs', 'recording_log_id'),
--               COALESCE((SELECT MAX(recording_log_id) FROM recording_logs), 1));
-- SELECT setval(pg_get_serial_sequence('task_replications', 'task_replication_id'),
--               COALESCE((SELECT MAX(task_replication_id) FROM task_replications), 1));
-- SELECT setval(pg_get_serial_sequence('task_comments', 'id'),
--               COALESCE((SELECT MAX(id) FROM task_comments), 1));
-- SELECT setval(pg_get_serial_sequence('qa_feedback', 'qa_feedback_id'),
--               COALESCE((SELECT MAX(qa_feedback_id) FROM qa_feedback), 1));
-- SELECT setval(pg_get_serial_sequence('permissions', 'permission_id'),
--               COALESCE((SELECT MAX(permission_id) FROM permissions), 1));
-- SELECT setval(pg_get_serial_sequence('role_permissions', 'role_permission_id'),
--               COALESCE((SELECT MAX(role_permission_id) FROM role_permissions), 1));

-- COMMIT;