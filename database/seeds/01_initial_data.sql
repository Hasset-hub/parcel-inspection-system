-- Insert admin user (password: Admin123!)
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin',
    'admin@parcelsinspect.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7QfNJh3kha',
    'System Administrator',
    'admin',
    TRUE
);

-- Insert test warehouse
INSERT INTO warehouses (warehouse_code, name, city, state, country, is_active)
VALUES (
    'WH001',
    'Main Distribution Center',
    'Los Angeles',
    'CA',
    'USA',
    TRUE
);

-- Insert test supplier
INSERT INTO suppliers (supplier_code, name, email, is_active)
VALUES (
    'SUP001',
    'Global Logistics Inc',
    'contact@globallogistics.com',
    TRUE
);

-- Insert test SKUs
INSERT INTO skus (sku_code, name, category, is_fragile)
VALUES 
    ('SKU001', 'Electronics - Laptop', 'Electronics', TRUE),
    ('SKU002', 'Home Goods - Pillow', 'Home', FALSE),
    ('SKU003', 'Fragile - Glassware Set', 'Kitchen', TRUE);

-- Insert packaging types
INSERT INTO packaging_types (type_code, name, material)
VALUES
    ('BOX-STD', 'Standard Cardboard Box', 'cardboard'),
    ('BOX-HVY', 'Heavy-Duty Box', 'cardboard'),
    ('CRATE', 'Wooden Crate', 'wood');

-- Insert system settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description)
VALUES
    ('auto_approve_confidence_threshold', '0.40', 'decimal', 'Auto-approve if damage confidence below this'),
    ('auto_accept_low_value_threshold', '20.00', 'decimal', 'Auto-accept damage if SKU value below this (USD)'),
    ('enable_multi_angle_scan', 'true', 'boolean', 'Require multiple angle scans'),
    ('ocr_enabled', 'true', 'boolean', 'Enable OCR on labels')
ON CONFLICT (setting_key) DO NOTHING;
