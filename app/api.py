from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.db import engine, Base, get_db
from app.models import (
    ChatRequest, ChatResponse, MemorySnapshot, AuditEventSchema, 
    UserRegister, Token, DB_User
)
from app.memory_agent import MemoryAgent
from app.memory_db import MemoryDB
from app.graph_store import GraphStore
from app.reflection import reflection_engine
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.rate_limiter import RateLimiterMiddleware
from app.security_headers import SecurityHeadersMiddleware
from app.config import settings


# Create Database tables on startup
Base.metadata.create_all(bind=engine)

def check_and_migrate_db():
    """Automatically run schema migration to add 'role' column to SQLite db if missing."""
    from sqlalchemy import text
    from app.utils import logger
    db = next(get_db())
    try:
        res = db.execute(text("PRAGMA table_info(users)")).fetchall()
        columns = [r[1] for r in res]
        if "role" not in columns:
            logger.info("Migrating database: adding 'role' column to 'users' table")
            db.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'standard'"))
            db.commit()
    except Exception as e:
        logger.error("Failed to migrate database for user role: %s", e)
    finally:
        db.close()

# Run SQLite migrations
check_and_migrate_db()

from contextlib import asynccontextmanager

def bootstrap_vector_store():
    """Populates the vector store with existing active memories from the database."""
    from app.utils import logger
    from app.models import DB_Memory
    from app.vector_store import vector_store
    
    db = next(get_db())
    try:
        active_memories = db.query(DB_Memory).filter(DB_Memory.status == "active").all()
        logger.info("Bootstrapping vector store index with %d active memories.", len(active_memories))
        
        for mem in active_memories:
            try:
                vector_store.add_document(
                    doc_id=mem.id,
                    text=f"{mem.canonical_property}: {mem.value_canonical} ({mem.source_text or ''})",
                    metadata={"user_id": mem.user_id, "canonical_property": mem.canonical_property}
                )
            except Exception as e:
                logger.warning("Failed to bootstrap fact %d to vector store: %s", mem.id, e)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_vector_store()
    yield

app = FastAPI(
    title="Memora Graph API",
    description="Persistent and Reconcilable Memory Graph Layer for LLM Agents",
    version="2.2.0",
    lifespan=lifespan
)

# CORS — allow the Streamlit frontend and local development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8503",
        "http://127.0.0.1:8503",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting — configurable via Settings
app.add_middleware(
    RateLimiterMiddleware,
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS,
    window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS
)

# Security headers — OWASP recommended protections
app.add_middleware(SecurityHeadersMiddleware)

_STARTUP_TIME = datetime.now(timezone.utc)



# ==========================================
# Authentication Endpoints
# ==========================================

@app.post("/register", tags=["Auth"])
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registers a new system user profile."""
    existing_user = db.query(DB_User).filter(DB_User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = DB_User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role=user_data.role or "standard"
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/token", response_model=Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Standard OAuth2 password flow returning a JWT claim token."""
    user = db.query(DB_User).filter(DB_User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# Core Memory Endpoints (Protected)
# ==========================================

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(
    request: ChatRequest, 
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Protected chat processing route.
    Auto-binds user context to the authenticated token.
    """
    try:
        agent = MemoryAgent(db)
        chat_response = agent.process_message(
            user_id=current_user,
            message=request.message,
            session_id=request.session_id
        )
        return chat_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/memories", response_model=List[MemorySnapshot], tags=["Memories"])
def get_active_memories(
    status: Optional[str] = Query("active", description="Filter memories by status (active, superseded, disputed, or all)"),
    limit: int = Query(100, description="Max number of memories to return", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, canonical_property, etc.)"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve memories for the authenticated user, optionally filtered by status, with sorting and pagination."""
    memory_db = MemoryDB(db)
    memories = memory_db.get_user_memories_by_status(
        user_id=current_user,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return [MemorySnapshot.model_validate(m) for m in memories]

@app.get("/memories/history", response_model=List[MemorySnapshot], tags=["Memories"])
def get_memory_history(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all versions of all memory properties for the authenticated user."""
    from app.models import DB_Memory
    memories = db.query(DB_Memory).filter(DB_Memory.user_id == current_user).all()
    return [MemorySnapshot.model_validate(m) for m in memories]

@app.get("/memories/search", response_model=List[MemorySnapshot], tags=["Memories"])
def search_memories(
    q: str = Query(..., description="Query text to search for similarity"),
    threshold: float = Query(0.35, description="Similarity threshold"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform hybrid search over the user's active memories."""
    memory_db = MemoryDB(db)
    matched = memory_db.search_similar_facts(current_user, q, threshold)
    return [MemorySnapshot.model_validate(m) for m in matched]

@app.post("/memories/clear", tags=["Memories"])
def clear_memories(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all memories and nodes in the user's graph."""
    memory_db = MemoryDB(db)
    memory_db.clear_user_memory(current_user)
    return {"status": "success", "message": f"All memories cleared for user {current_user}"}

@app.get("/memories/audit", response_model=List[AuditEventSchema], tags=["Audit"])
def get_audit_log(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve the full audit event history for the authenticated user."""
    memory_db = MemoryDB(db)
    logs = memory_db.get_audit_log(current_user)
    return [AuditEventSchema.model_validate(e) for e in logs]

# ==========================================
# Graph & Reflection Endpoints (Protected)
# ==========================================

@app.get("/graph/snapshot", tags=["Graph"])
def get_graph_snapshot(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the complete node-link ER graph representation for UI display."""
    graph_store = GraphStore(db)
    return graph_store.get_graph_snapshot(current_user)

@app.get("/graph/export", tags=["Graph"])
def export_graph(
    format: Optional[str] = Query("json", description="Export format: json or rdf"),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports the complete memory graph for the user as JSON or RDF Turtle."""
    graph_store = GraphStore(db)
    if format and format.lower() == "rdf":
        from fastapi import Response
        rdf_content = graph_store.export_to_rdf_turtle(current_user)
        return Response(content=rdf_content, media_type="text/turtle")
    return graph_store.get_graph_snapshot(current_user)

@app.post("/reflection/trigger", tags=["Reflection"])
def trigger_reflection(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Triggers an off-cycle consolidation and dispute reflection cycle."""
    actions = reflection_engine.reflect_and_consolidate(current_user, db)
    return {
        "status": "success", 
        "actions_performed": actions,
        "message": f"Consolidation complete. {len(actions)} optimizations executed."
    }

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Verify backend health status with uptime metadata and database connectivity."""
    from sqlalchemy import text
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        from app.utils import logger
        logger.error("Database health check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "database": "unhealthy", "reason": str(e)}
        )

    now = datetime.now(timezone.utc)
    uptime_seconds = (now - _STARTUP_TIME).total_seconds()
    return {
        "status": "healthy",
        "service": "memora-graph-api",
        "version": app.version,
        "database": db_status,
        "started_at": _STARTUP_TIME.isoformat(),
        "uptime_seconds": round(uptime_seconds, 1),
    }

@app.get("/stats", tags=["System"])
def get_user_stats(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns memory graph statistics for the authenticated user."""
    from app.models import DB_Memory, DB_Entity, DB_Relationship, DB_AuditEvent
    from sqlalchemy import func

    total_memories = db.query(func.count(DB_Memory.id)).filter(
        DB_Memory.user_id == current_user
    ).scalar() or 0

    active_memories = db.query(func.count(DB_Memory.id)).filter(
        DB_Memory.user_id == current_user,
        DB_Memory.status == "active"
    ).scalar() or 0

    disputed_memories = db.query(func.count(DB_Memory.id)).filter(
        DB_Memory.user_id == current_user,
        DB_Memory.status == "disputed"
    ).scalar() or 0

    superseded_memories = db.query(func.count(DB_Memory.id)).filter(
        DB_Memory.user_id == current_user,
        DB_Memory.status == "superseded"
    ).scalar() or 0

    total_entities = db.query(func.count(DB_Entity.id)).filter(
        DB_Entity.user_id == current_user
    ).scalar() or 0

    total_relationships = db.query(func.count(DB_Relationship.id)).filter(
        DB_Relationship.user_id == current_user
    ).scalar() or 0

    total_audit_events = db.query(func.count(DB_AuditEvent.id)).filter(
        DB_AuditEvent.user_id == current_user
    ).scalar() or 0

    # Property distribution
    property_counts = db.query(
        DB_Memory.canonical_property, func.count(DB_Memory.id)
    ).filter(
        DB_Memory.user_id == current_user,
        DB_Memory.status == "active"
    ).group_by(DB_Memory.canonical_property).all()

    return {
        "user_id": current_user,
        "memories": {
            "total": total_memories,
            "active": active_memories,
            "disputed": disputed_memories,
            "superseded": superseded_memories,
        },
        "graph": {
            "entities": total_entities,
            "relationships": total_relationships,
        },
        "audit_events": total_audit_events,
        "property_distribution": {
            prop: count for prop, count in property_counts
        },
    }

