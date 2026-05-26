INSERT INTO roles(role_id, name)
SELECT
    '11111111-1111-1111-1111-111111111111',
    'super_admin'
WHERE NOT EXISTS (
    SELECT 1 FROM roles
);

INSERT INTO shifts(shift_id, name)
SELECT
    '22222222-2222-2222-2222-222222222222',
    'General Shift'
WHERE NOT EXISTS (
    SELECT 1 FROM shifts
);