-- Auto-Resolution Settings
INSERT INTO system_settings (setting_key, setting_value, value_type, category, description, json_value) VALUES

-- Confidence thresholds
('auto_approve_confidence_threshold', '0.95', 'number', 'auto_resolution', 'Minimum confidence to auto-approve (no damage detected)', 
 '{"min": 0.0, "max": 1.0, "default": 0.95}'),

('auto_quarantine_confidence_threshold', '0.70', 'number', 'auto_resolution', 'Minimum confidence to auto-quarantine (damage detected)', 
 '{"min": 0.0, "max": 1.0, "default": 0.70}'),

-- Damage severity rules
('auto_approve_max_damage_score', '0.10', 'number', 'auto_resolution', 'Maximum damage score to auto-approve',
 '{"min": 0.0, "max": 1.0, "default": 0.10}'),

('auto_quarantine_min_damage_score', '0.30', 'number', 'auto_resolution', 'Minimum damage score to auto-quarantine',
 '{"min": 0.0, "max": 1.0, "default": 0.30}'),

-- Image requirements
('min_images_for_auto_resolution', '6', 'number', 'auto_resolution', 'Minimum images required for auto-resolution',
 '{"min": 1, "max": 10, "default": 6}'),

-- Supplier-based rules
('use_supplier_history', 'true', 'boolean', 'auto_resolution', 'Use supplier damage history in decisions',
 '{"default": true}'),

('supplier_damage_rate_threshold', '0.15', 'number', 'auto_resolution', 'Supplier damage rate threshold for stricter inspection',
 '{"min": 0.0, "max": 1.0, "default": 0.15}'),

-- Value-based rules
('high_value_threshold', '500.00', 'number', 'auto_resolution', 'Value threshold for manual review (USD)',
 '{"default": 500.00}'),

('auto_approve_enabled', 'true', 'boolean', 'auto_resolution', 'Enable automatic approval',
 '{"default": true}'),

('auto_quarantine_enabled', 'true', 'boolean', 'auto_resolution', 'Enable automatic quarantine',
 '{"default": true}'),

('auto_reject_enabled', 'false', 'boolean', 'auto_resolution', 'Enable automatic rejection',
 '{"default": false}')

ON CONFLICT (setting_key) DO UPDATE SET
    setting_value = EXCLUDED.setting_value,
    json_value = EXCLUDED.json_value,
    updated_at = NOW();