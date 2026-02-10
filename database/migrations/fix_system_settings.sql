-- Add missing columns to system_settings table
DO $$ 
BEGIN
    -- Add category if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='system_settings' AND column_name='category'
    ) THEN
        ALTER TABLE system_settings ADD COLUMN category VARCHAR(50);
    END IF;

    -- Add value_type if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='system_settings' AND column_name='value_type'
    ) THEN
        ALTER TABLE system_settings ADD COLUMN value_type VARCHAR(20);
    END IF;

    -- Add description if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='system_settings' AND column_name='description'
    ) THEN
        ALTER TABLE system_settings ADD COLUMN description TEXT;
    END IF;

    -- Add json_value if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='system_settings' AND column_name='json_value'
    ) THEN
        ALTER TABLE system_settings ADD COLUMN json_value JSONB;
    END IF;

    -- Add is_active if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='system_settings' AND column_name='is_active'
    ) THEN
        ALTER TABLE system_settings ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;

    -- Add created_at if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='system_settings' AND column_name='created_at'
    ) THEN
        ALTER TABLE system_settings ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
    END IF;

    -- Add updated_at if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='system_settings' AND column_name='updated_at'
    ) THEN
        ALTER TABLE system_settings ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_system_settings_category ON system_settings(category);
CREATE INDEX IF NOT EXISTS idx_system_settings_active ON system_settings(is_active);

-- Create/update trigger
CREATE OR REPLACE FUNCTION update_system_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_system_settings_updated_at ON system_settings;
CREATE TRIGGER trigger_update_system_settings_updated_at
    BEFORE UPDATE ON system_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_system_settings_updated_at();
