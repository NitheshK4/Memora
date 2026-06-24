from datetime import datetime, UTC
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from app.db import Base
from pydantic import BaseModel, ConfigDict, Field, field_validator

def get_utc_now():
    return datetime.now(UTC).replace(tzinfo=None)

# ==========================================
# SQLAlchemy Database Models
# ==========================================

class DB_User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

class DB_Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    entity_type = Column(String, nullable=False)  # person, organization, pet, place, self, etc.
    name = Column(String, nullable=False)          # Canonical name (e.g., 'Max', 'Google')
    created_at = Column(DateTime, default=get_utc_now)

class DB_Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    source_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    target_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    predicate = Column(String, nullable=False)      # works_at, lives_in, has_pet, etc.
    status = Column(String, default="active")       # active, superseded, disputed
    created_at = Column(DateTime, default=get_utc_now)

class DB_Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True)         # Property of a node
    relationship_id = Column(Integer, ForeignKey("relationships.id"), nullable=True) # Property of an edge
    property_name = Column(String, nullable=False)
    canonical_property = Column(String, index=True, nullable=False)
    value_raw = Column(String, nullable=False)
    value_canonical = Column(String, nullable=False)
    value_type = Column(String, default="string")
    confidence = Column(Float, default=1.0)
    source_text = Column(String, nullable=True)
    source_type = Column(String, default="user_message")
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    effective_from = Column(DateTime, default=get_utc_now)
    effective_to = Column(DateTime, nullable=True)
    status = Column(String, default="active")       # active, superseded, disputed, expired, rejected
    version = Column(Integer, default=1)
    validation_status = Column(String, default="valid")
    resolution_note = Column(String, nullable=True)

class DB_AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    memory_id = Column(Integer, ForeignKey("memories.id"), nullable=True)
    event_type = Column(String, nullable=False)     # created, superseded, disputed, resolved, cleared
    previous_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    resolver_type = Column(String, nullable=True)   # rule_recency, rule_stability, manual, llm_reasoning, etc.
    created_at = Column(DateTime, default=get_utc_now)

# ==========================================
# Pydantic Schemas (with input validation)
# ==========================================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ExtractedFact(BaseModel):
    entity_type: Optional[str] = "self"
    entity_id: Optional[str] = "self"
    property_name: str
    value_raw: str
    confidence: float = 0.8
    source_text: Optional[str] = None
    
    # Optional fields for relations
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    predicate: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Fact(BaseModel):
    property_name: str
    value_canonical: str
    entity_type: Optional[str] = "self"
    entity_id: Optional[str] = "self"

class ConflictInfo(BaseModel):
    new_fact: ExtractedFact
    existing_memory_id: int
    existing_value: str
    conflict_type: str

class ValidationResult(BaseModel):
    is_valid: bool
    reason: Optional[str] = None
    error_type: Optional[str] = None

class ResolutionAction(BaseModel):
    action: str
    status: str
    reason: str
    resolver_type: str

class EntitySnapshot(BaseModel):
    id: int
    entity_type: str
    name: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RelationshipSnapshot(BaseModel):
    id: int
    source_entity_id: int
    target_entity_id: int
    predicate: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MemorySnapshot(BaseModel):
    id: int
    user_id: str
    entity_id: Optional[int] = None
    relationship_id: Optional[int] = None
    property_name: str
    canonical_property: str
    value_raw: str
    value_canonical: str
    value_type: str
    confidence: float
    source_text: Optional[str] = None
    source_type: str
    session_id: Optional[str] = None
    created_at: datetime
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    status: str
    version: int
    validation_status: str
    resolution_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AuditEventSchema(BaseModel):
    id: int
    user_id: str
    memory_id: Optional[int] = None
    event_type: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None
    resolver_type: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    message: str = Field(..., min_length=1, max_length=4096)
    session_id: Optional[str] = Field(default="session_default", max_length=128)

    @field_validator("message")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or whitespace only")
        return stripped

class ChatResponse(BaseModel):
    response: str
    extracted_facts: List[ExtractedFact] = []
    conflicts_detected: List[ConflictInfo] = []
    audit_logs: List[AuditEventSchema] = []
    active_memories: List[MemorySnapshot] = []
