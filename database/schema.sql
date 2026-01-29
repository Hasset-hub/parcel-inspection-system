-- ============================================================================
-- ENTERPRISE PARCEL INSPECTION & INVENTORY MANAGEMENT SYSTEM
-- Database Schema Design
-- ============================================================================
-- Version: 1.0
-- Database: PostgreSQL 14+
-- Purpose: Comprehensive parcel tracking, damage detection, supplier 
--          management, and compliance auditing system
-- ============================================================================

-- ============================================================================
-- CORE DOMAIN TABLES
-- ============================================================================

-- Users and Authentication
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('scanner', 'inspector', 'supervisor', 'admin')),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Warehouses/Facilities
CREATE TABLE warehouses (
    warehouse_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_warehouses_code ON warehouses(warehouse_code);

-- Suppliers
CREATE TABLE suppliers (
    supplier_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    country VARCHAR(100),
    
    -- Supplier performance metrics
    total_shipments INTEGER DEFAULT 0,
    total_damaged_parcels INTEGER DEFAULT 0,
    damage_rate DECIMAL(5,4) DEFAULT 0.0000,
    avg_packaging_quality_score DECIMAL(3,2),
    
    -- Contract & compliance
    contract_start_date DATE,
    contract_end_date DATE,
    sla_delivery_time_hours INTEGER,
    sla_damage_threshold DECIMAL(5,4),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX idx_suppliers_damage_rate ON suppliers(damage_rate);

-- SKUs (Stock Keeping Units)
CREATE TABLE skus (
    sku_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(300) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Physical properties
    expected_weight_kg DECIMAL(10,3),
    expected_length_cm DECIMAL(8,2),
    expected_width_cm DECIMAL(8,2),
    expected_height_cm DECIMAL(8,2),
    
    -- Value & handling
    unit_value DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'USD',
    is_fragile BOOLEAN DEFAULT FALSE,
    is_hazardous BOOLEAN DEFAULT FALSE,
    handling_instructions TEXT,
    
    -- Reference images for comparison
    reference_image_url VARCHAR(500),
    reference_image_hash VARCHAR(64),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skus_code ON skus(sku_code);
CREATE INDEX idx_skus_category ON skus(category);
CREATE INDEX idx_skus_fragile ON skus(is_fragile);

-- Packaging Types
CREATE TABLE packaging_types (
    packaging_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    material VARCHAR(100), -- cardboard, plastic, wood, etc.
    
    -- Dimensions
    length_cm DECIMAL(8,2),
    width_cm DECIMAL(8,2),
    height_cm DECIMAL(8,2),
    
    -- Performance tracking
    total_uses INTEGER DEFAULT 0,
    damage_incidents INTEGER DEFAULT 0,
    damage_rate DECIMAL(5,4) DEFAULT 0.0000,
    cushioning_effectiveness_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_packaging_damage_rate ON packaging_types(damage_rate);

-- ============================================================================
-- SHIPMENT & PARCEL TRACKING
-- ============================================================================

-- Shipments (collections of parcels from suppliers)
CREATE TABLE shipments (
    shipment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_number VARCHAR(100) UNIQUE NOT NULL,
    supplier_id UUID REFERENCES suppliers(supplier_id),
    origin_warehouse_id UUID REFERENCES warehouses(warehouse_id),
    destination_warehouse_id UUID REFERENCES warehouses(warehouse_id),
    
    -- Timeline
    expected_arrival TIMESTAMP WITH TIME ZONE,
    actual_arrival TIMESTAMP WITH TIME ZONE,
    is_late BOOLEAN DEFAULT FALSE,
    
    -- Manifest
    total_parcels INTEGER DEFAULT 0,
    total_weight_kg DECIMAL(12,3),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'in_transit', 'arrived', 'inspecting', 'completed', 'disputed'
    )),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_shipments_supplier ON shipments(supplier_id);
CREATE INDEX idx_shipments_status ON shipments(status);
CREATE INDEX idx_shipments_arrival ON shipments(actual_arrival);

-- Parcels (individual packages)
CREATE TABLE parcels (
    parcel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    shipment_id UUID REFERENCES shipments(shipment_id),
    sku_id UUID REFERENCES skus(sku_id),
    packaging_type_id UUID REFERENCES packaging_types(packaging_type_id),
    
    -- Physical properties
    weight_kg DECIMAL(10,3),
    length_cm DECIMAL(8,2),
    width_cm DECIMAL(8,2),
    height_cm DECIMAL(8,2),
    
    -- Validation flags
    dimension_mismatch BOOLEAN DEFAULT FALSE,
    weight_mismatch BOOLEAN DEFAULT FALSE,
    
    -- Current state
    current_warehouse_id UUID REFERENCES warehouses(warehouse_id),
    current_location VARCHAR(200), -- e.g., "Zone A, Shelf 12"
    status VARCHAR(50) DEFAULT 'received' CHECK (status IN (
        'received', 'inspecting', 'approved', 'damaged', 'quarantine', 
        'stored', 'picked', 'shipped', 'returned'
    )),
    
    -- Damage assessment
    has_damage BOOLEAN DEFAULT FALSE,
    damage_severity VARCHAR(20) CHECK (damage_severity IN (
        NULL, 'minor', 'moderate', 'severe', 'total_loss'
    )),
    damage_value_estimate DECIMAL(12,2),
    
    -- Auto-resolution
    auto_resolved BOOLEAN DEFAULT FALSE,
    auto_resolution_reason TEXT,
    
    -- Tags
    tags TEXT[], -- e.g., ['high_risk', 'fragile', 'quarantine']
    
    -- Timestamps
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inspected_at TIMESTAMP WITH TIME ZONE,
    stored_at TIMESTAMP WITH TIME ZONE,
    shipped_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parcels_tracking ON parcels(tracking_number);
CREATE INDEX idx_parcels_shipment ON parcels(shipment_id);
CREATE INDEX idx_parcels_sku ON parcels(sku_id);
CREATE INDEX idx_parcels_warehouse ON parcels(current_warehouse_id);
CREATE INDEX idx_parcels_status ON parcels(status);
CREATE INDEX idx_parcels_damage ON parcels(has_damage);
CREATE INDEX idx_parcels_tags ON parcels USING GIN(tags);

-- ============================================================================
-- INSPECTION & DAMAGE DETECTION
-- ============================================================================

-- Inspections (container for multi-angle scan)
CREATE TABLE inspections (
    inspection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcel_id UUID REFERENCES parcels(parcel_id) ON DELETE CASCADE,
    inspector_user_id UUID REFERENCES users(user_id),
    device_id VARCHAR(100),
    
    -- Inspection type
    inspection_type VARCHAR(50) DEFAULT 'receiving' CHECK (inspection_type IN (
        'receiving', 'storage', 'pre_shipment', 'audit', 'claim_verification'
    )),
    
    -- Results
    overall_status VARCHAR(20) CHECK (overall_status IN (
        'pass', 'fail', 'review_required', 'auto_approved'
    )),
    overall_confidence DECIMAL(5,4), -- 0.0000 to 1.0000
    
    -- OCR results
    ocr_text TEXT,
    labels_detected TEXT[],
    hazard_warnings TEXT[],
    missing_labels TEXT[],
    
    -- Expected vs Observed
    expected_appearance_match_score DECIMAL(5,4),
    tampering_detected BOOLEAN DEFAULT FALSE,
    wrong_packaging_detected BOOLEAN DEFAULT FALSE,
    
    notes TEXT,
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER
);

CREATE INDEX idx_inspections_parcel ON inspections(parcel_id);
CREATE INDEX idx_inspections_inspector ON inspections(inspector_user_id);
CREATE INDEX idx_inspections_status ON inspections(overall_status);

-- Inspection Images (multi-angle support)
CREATE TABLE inspection_images (
    image_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inspection_id UUID REFERENCES inspections(inspection_id) ON DELETE CASCADE,
    
    angle VARCHAR(20) NOT NULL CHECK (angle IN ('top', 'bottom', 'front', 'back', 'left', 'right')),
    image_url VARCHAR(500) NOT NULL,
    image_hash VARCHAR(64),
    image_size_bytes INTEGER,
    
    -- ML processing results
    processed BOOLEAN DEFAULT FALSE,
    processing_time_ms INTEGER,
    
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inspection_images_inspection ON inspection_images(inspection_id);
CREATE INDEX idx_inspection_images_angle ON inspection_images(angle);

-- Damage Detections (YOLO results per image)
CREATE TABLE damage_detections (
    detection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_id UUID REFERENCES inspection_images(image_id) ON DELETE CASCADE,
    inspection_id UUID REFERENCES inspections(inspection_id) ON DELETE CASCADE,
    
    -- Detection details
    damage_type VARCHAR(50) NOT NULL, -- 'dent', 'tear', 'crush', 'water', 'puncture', etc.
    confidence DECIMAL(5,4) NOT NULL,
    
    -- Bounding box (normalized 0-1)
    bbox_x DECIMAL(6,5) NOT NULL,
    bbox_y DECIMAL(6,5) NOT NULL,
    bbox_width DECIMAL(6,5) NOT NULL,
    bbox_height DECIMAL(6,5) NOT NULL,
    
    -- Severity assessment
    severity_score DECIMAL(3,2), -- 0.00 to 1.00
    
    model_version VARCHAR(50),
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_damage_detections_image ON damage_detections(image_id);
CREATE INDEX idx_damage_detections_inspection ON damage_detections(inspection_id);
CREATE INDEX idx_damage_detections_type ON damage_detections(damage_type);
CREATE INDEX idx_damage_detections_confidence ON damage_detections(confidence);

-- ============================================================================
-- IMMUTABLE EVENT LEDGER (Audit Trail)
-- ============================================================================

CREATE TABLE event_log (
    event_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- 'SCAN', 'INSPECT', 'STORE', 'MOVE', 'SHIP', etc.
    
    -- Related entities
    parcel_id UUID REFERENCES parcels(parcel_id),
    user_id UUID REFERENCES users(user_id),
    warehouse_id UUID REFERENCES warehouses(warehouse_id),
    
    -- Event details
    event_data JSONB NOT NULL,
    
    -- Metadata
    device_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    
    -- Immutability
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    event_hash VARCHAR(64) NOT NULL -- SHA-256 of event + previous hash
);

-- Prevent updates and deletes
CREATE RULE event_log_no_update AS ON UPDATE TO event_log DO INSTEAD NOTHING;
CREATE RULE event_log_no_delete AS ON DELETE TO event_log DO INSTEAD NOTHING;

CREATE INDEX idx_event_log_parcel ON event_log(parcel_id);
CREATE INDEX idx_event_log_user ON event_log(user_id);
CREATE INDEX idx_event_log_type ON event_log(event_type);
CREATE INDEX idx_event_log_created ON event_log(created_at);
CREATE INDEX idx_event_log_data ON event_log USING GIN(event_data);

-- ============================================================================
-- DWELL TIME & FLOW TRACKING
-- ============================================================================

CREATE TABLE parcel_movements (
    movement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parcel_id UUID REFERENCES parcels(parcel_id) ON DELETE CASCADE,
    
    from_location VARCHAR(200),
    to_location VARCHAR(200),
    from_warehouse_id UUID REFERENCES warehouses(warehouse_id),
    to_warehouse_id UUID REFERENCES warehouses(warehouse_id),
    
    movement_type VARCHAR(50) CHECK (movement_type IN (
        'arrival', 'storage', 'relocation', 'picking', 'shipment', 'return'
    )),
    
    moved_by_user_id UUID REFERENCES users(user_id),
    moved_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    notes TEXT
);

CREATE INDEX idx_movements_parcel ON parcel_movements(parcel_id);
CREATE INDEX idx_movements_warehouse ON parcel_movements(to_warehouse_id);
CREATE INDEX idx_movements_moved_at ON parcel_movements(moved_at);

-- Dwell time tracking (materialized view for performance)
CREATE MATERIALIZED VIEW parcel_dwell_times AS
SELECT 
    p.parcel_id,
    p.tracking_number,
    p.current_warehouse_id,
    
    -- Arrival to storage
    EXTRACT(EPOCH FROM (p.stored_at - p.received_at))/3600 AS arrival_to_storage_hours,
    
    -- Storage to shipment
    EXTRACT(EPOCH FROM (p.shipped_at - p.stored_at))/3600 AS storage_to_shipment_hours,
    
    -- Total dwell time
    EXTRACT(EPOCH FROM (COALESCE(p.shipped_at, CURRENT_TIMESTAMP) - p.received_at))/3600 AS total_dwell_hours,
    
    -- Inspection delay
    EXTRACT(EPOCH FROM (i.completed_at - i.started_at))/60 AS inspection_duration_minutes
    
FROM parcels p
LEFT JOIN inspections i ON p.parcel_id = i.parcel_id
WHERE p.received_at IS NOT NULL;

CREATE UNIQUE INDEX idx_dwell_parcel ON parcel_dwell_times(parcel_id);

-- ============================================================================
-- CLAIMS & DISPUTES
-- ============================================================================

CREATE TABLE damage_claims (
    claim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(100) UNIQUE NOT NULL,
    
    parcel_id UUID REFERENCES parcels(parcel_id),
    inspection_id UUID REFERENCES inspections(inspection_id),
    supplier_id UUID REFERENCES suppliers(supplier_id),
    
    -- Claim details
    claim_type VARCHAR(50) CHECK (claim_type IN (
        'supplier_damage', 'transit_damage', 'handling_damage', 'missing_items'
    )),
    claimed_value DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status VARCHAR(50) DEFAULT 'submitted' CHECK (status IN (
        'submitted', 'under_review', 'approved', 'rejected', 'settled', 'disputed'
    )),
    
    -- Evidence package
    evidence_package_url VARCHAR(500), -- PDF or JSON
    
    -- Resolution
    approved_amount DECIMAL(12,2),
    rejection_reason TEXT,
    settlement_date DATE,
    
    filed_by_user_id UUID REFERENCES users(user_id),
    reviewed_by_user_id UUID REFERENCES users(user_id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_claims_parcel ON damage_claims(parcel_id);
CREATE INDEX idx_claims_supplier ON damage_claims(supplier_id);
CREATE INDEX idx_claims_status ON damage_claims(status);
CREATE INDEX idx_claims_created ON damage_claims(created_at);

-- ============================================================================
-- SUPPLIER PERFORMANCE & SLA TRACKING
-- ============================================================================

CREATE TABLE supplier_violations (
    violation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID REFERENCES suppliers(supplier_id),
    
    violation_type VARCHAR(50) CHECK (violation_type IN (
        'late_delivery', 'excessive_damage', 'missing_quantity', 
        'packaging_quality', 'missing_documentation'
    )),
    
    -- Reference
    shipment_id UUID REFERENCES shipments(shipment_id),
    
    severity VARCHAR(20) CHECK (severity IN ('minor', 'major', 'critical')),
    description TEXT,
    
    -- Impact
    financial_impact DECIMAL(12,2),
    
    -- Resolution
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_violations_supplier ON supplier_violations(supplier_id);
CREATE INDEX idx_violations_type ON supplier_violations(violation_type);
CREATE INDEX idx_violations_resolved ON supplier_violations(resolved);

-- Supplier scorecards (aggregated metrics)
CREATE MATERIALIZED VIEW supplier_scorecards AS
SELECT 
    s.supplier_id,
    s.supplier_code,
    s.name,
    s.damage_rate,
    
    -- Shipment metrics
    COUNT(DISTINCT sh.shipment_id) AS total_shipments,
    SUM(CASE WHEN sh.is_late THEN 1 ELSE 0 END) AS late_deliveries,
    ROUND(SUM(CASE WHEN sh.is_late THEN 1 ELSE 0 END)::NUMERIC / 
          NULLIF(COUNT(DISTINCT sh.shipment_id), 0) * 100, 2) AS late_delivery_rate,
    
    -- Damage metrics
    COUNT(DISTINCT CASE WHEN p.has_damage THEN p.parcel_id END) AS damaged_parcels,
    
    -- Violation count
    COUNT(DISTINCT sv.violation_id) AS total_violations,
    
    -- Claim metrics
    COUNT(DISTINCT dc.claim_id) AS total_claims,
    COALESCE(SUM(dc.approved_amount), 0) AS total_claim_value,
    
    -- Packaging quality
    AVG(pt.damage_rate) AS avg_packaging_damage_rate,
    
    -- Last incident
    MAX(sv.created_at) AS last_violation_date,
    
    CURRENT_TIMESTAMP AS last_updated

FROM suppliers s
LEFT JOIN shipments sh ON s.supplier_id = sh.supplier_id
LEFT JOIN parcels p ON sh.shipment_id = p.shipment_id
LEFT JOIN packaging_types pt ON p.packaging_type_id = pt.packaging_type_id
LEFT JOIN supplier_violations sv ON s.supplier_id = sv.supplier_id
LEFT JOIN damage_claims dc ON s.supplier_id = dc.supplier_id

GROUP BY s.supplier_id, s.supplier_code, s.name, s.damage_rate;

CREATE UNIQUE INDEX idx_scorecard_supplier ON supplier_scorecards(supplier_id);

-- ============================================================================
-- ML TRAINING & ACTIVE LEARNING
-- ============================================================================

CREATE TABLE ml_training_queue (
    queue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_id UUID REFERENCES damage_detections(detection_id),
    image_id UUID REFERENCES inspection_images(image_id),
    
    -- Original prediction
    predicted_class VARCHAR(50),
    predicted_confidence DECIMAL(5,4),
    
    -- Human correction
    corrected_class VARCHAR(50),
    correction_reason TEXT,
    corrected_by_user_id UUID REFERENCES users(user_id),
    corrected_at TIMESTAMP WITH TIME ZONE,
    
    -- Training status
    added_to_training_set BOOLEAN DEFAULT FALSE,
    training_batch_id VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_training_queue_detection ON ml_training_queue(detection_id);
CREATE INDEX idx_training_queue_added ON ml_training_queue(added_to_training_set);

-- Model versions and performance
CREATE TABLE ml_models (
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_version VARCHAR(50) UNIQUE NOT NULL,
    model_type VARCHAR(50), -- 'yolo', 'classification', 'anomaly_detection'
    
    -- Training info
    trained_on TIMESTAMP WITH TIME ZONE,
    training_samples INTEGER,
    
    -- Performance metrics
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    
    -- Deployment
    is_active BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP WITH TIME ZONE,
    
    model_file_url VARCHAR(500),
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_models_version ON ml_models(model_version);
CREATE INDEX idx_models_active ON ml_models(is_active);

-- ============================================================================
-- SYSTEM CONFIGURATION
-- ============================================================================

CREATE TABLE system_settings (
    setting_key VARCHAR(100) PRIMARY KEY,
    setting_value TEXT NOT NULL,
    setting_type VARCHAR(50) CHECK (setting_type IN (
        'string', 'integer', 'decimal', 'boolean', 'json'
    )),
    description TEXT,
    updated_by_user_id UUID REFERENCES users(user_id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO system_settings (setting_key, setting_value, setting_type, description) VALUES
('auto_approve_confidence_threshold', '0.40', 'decimal', 'Auto-approve parcels if damage confidence below this'),
('auto_accept_low_value_threshold', '20.00', 'decimal', 'Auto-accept damage if SKU value below this (USD)'),
('sla_inspection_time_hours', '24', 'integer', 'Maximum hours for inspection completion'),
('enable_multi_angle_scan', 'true', 'boolean', 'Require multiple angle scans'),
('ocr_enabled', 'true', 'boolean', 'Enable OCR on labels'),
('active_ml_model_version', '', 'string', 'Currently active YOLO model version');

-- ============================================================================
-- API INTEGRATIONS
-- ============================================================================

CREATE TABLE api_keys (
    api_key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_name VARCHAR(200) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL UNIQUE,
    
    -- Permissions
    scopes TEXT[] NOT NULL, -- ['inventory:read', 'damage:write', etc.]
    
    -- Usage tracking
    last_used_at TIMESTAMP WITH TIME ZONE,
    request_count INTEGER DEFAULT 0,
    
    -- Lifecycle
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by_user_id UUID REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_hash ON api_keys(api_key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);

-- ============================================================================
-- TRIGGERS & FUNCTIONS
-- ============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skus_updated_at BEFORE UPDATE ON skus
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parcels_updated_at BEFORE UPDATE ON parcels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shipments_updated_at BEFORE UPDATE ON shipments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_claims_updated_at BEFORE UPDATE ON damage_claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-update supplier metrics
CREATE OR REPLACE FUNCTION update_supplier_metrics()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE suppliers s
    SET 
        total_shipments = (
            SELECT COUNT(*) FROM shipments WHERE supplier_id = s.supplier_id
        ),
        total_damaged_parcels = (
            SELECT COUNT(*) 
            FROM parcels p 
            JOIN shipments sh ON p.shipment_id = sh.shipment_id
            WHERE sh.supplier_id = s.supplier_id AND p.has_damage = TRUE
        ),
        damage_rate = (
            SELECT COALESCE(
                CAST(COUNT(*) FILTER (WHERE p.has_damage) AS DECIMAL) / 
                NULLIF(COUNT(*), 0), 
                0
            )
            FROM parcels p 
            JOIN shipments sh ON p.shipment_id = sh.shipment_id
            WHERE sh.supplier_id = s.supplier_id
        )
    WHERE s.supplier_id = (
        SELECT supplier_id FROM shipments WHERE shipment_id = NEW.shipment_id
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_supplier_metrics 
AFTER INSERT OR UPDATE ON parcels
FOR EACH ROW 
WHEN (NEW.has_damage IS NOT NULL)
EXECUTE FUNCTION update_supplier_metrics();

-- ============================================================================
-- MATERIALIZED VIEW REFRESH
-- ============================================================================

-- Create function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY parcel_dwell_times;
    REFRESH MATERIALIZED VIEW CONCURRENTLY supplier_scorecards;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA QUERIES (for documentation)
-- ============================================================================

-- Example: Get parcel journey timeline
-- SELECT 
--     p.tracking_number,
--     pm.movement_type,
--     pm.from_location,
--     pm.to_location,
--     pm.moved_at
-- FROM parcels p
-- JOIN parcel_movements pm ON p.parcel_id = pm.parcel_id
-- WHERE p.tracking_number = 'TRACK123456'
-- ORDER BY pm.moved_at;

-- Example: Get damage hotspots
-- SELECT 
--     damage_type,
--     COUNT(*) as count,
--     AVG(confidence) as avg_confidence
-- FROM damage_detections
-- GROUP BY damage_type
-- ORDER BY count DESC;

-- ============================================================================
-- INDEXES FOR ANALYTICS & REPORTING
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX idx_parcels_warehouse_status ON parcels(current_warehouse_id, status);
CREATE INDEX idx_parcels_damage_severity ON parcels(has_damage, damage_severity);
CREATE INDEX idx_inspections_status_date ON inspections(overall_status, completed_at);
CREATE INDEX idx_event_log_parcel_type ON event_log(parcel_id, event_type);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE event_log IS 'Immutable append-only audit log. Cannot be updated or deleted.';
COMMENT ON TABLE damage_detections IS 'YOLO model output for each inspection image.';
COMMENT ON TABLE ml_training_queue IS 'Active learning pipeline for model improvement.';
COMMENT ON COLUMN parcels.tags IS 'Flexible array for auto-generated labels like high_risk, fragile, quarantine.';
COMMENT ON MATERIALIZED VIEW parcel_dwell_times IS 'Pre-calculated dwell times for performance. Refresh hourly.';
COMMENT ON MATERIALIZED VIEW supplier_scorecards IS 'Aggregated supplier performance metrics. Refresh daily.';

-- ============================================================================
-- GRANTS (example - adjust based on your security needs)
-- ============================================================================

-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_role;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_role;
-- REVOKE ALL ON event_log FROM app_role;
-- GRANT SELECT, INSERT ON event_log TO app_role;
