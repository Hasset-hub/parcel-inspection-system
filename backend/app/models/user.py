from sqlalchemy import Column, String, Boolean, TIMESTAMP, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.db.session import Base

class UserRole(str, enum.Enum):
    """User role enumeration"""
    SCANNER = "scanner"
    INSPECTOR = "inspector"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"

class User(Base):
    """User model for authentication and authorization"""
    
    __tablename__ = "users"
    
    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(
        Enum(UserRole, native_enum=False, length=50),
        nullable=False,
        default=UserRole.SCANNER,
        index=True
    )
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"
