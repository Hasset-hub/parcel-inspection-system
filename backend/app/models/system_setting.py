"""System Settings model"""
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.db.session import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    setting_key = Column(String(100), primary_key=True)
    setting_value = Column(Text)
    value_type = Column(String(20))  # string, number, boolean, json
    category = Column(String(50))  # auto_resolution, ml, notifications
    description = Column(Text)
    
    # For JSON settings
    json_value = Column(JSONB)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemSetting {self.setting_key}>"
