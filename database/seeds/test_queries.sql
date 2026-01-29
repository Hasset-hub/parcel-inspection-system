-- Test 1: Check user
SELECT username, role FROM users WHERE username = 'admin';

-- Test 2: Check warehouse
SELECT warehouse_code, name FROM warehouses;

-- Test 3: Check foreign key relationships work
SELECT
    p.tracking_number,
    w.warehouse_code
FROM parcels p
LEFT JOIN warehouses w ON p.current_warehouse_id = w.warehouse_id
LIMIT 5;

-- Test 4: Check event_log immutability rules
-- UPDATE event_log SET event_type = 'TEST' WHERE event_id = 1;

-- Test 5: Verify materialized views exist
SELECT matviewname FROM pg_matviews;
