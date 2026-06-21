import pytest
from app.memory_agent import MemoryAgent
from app.models import DB_Memory, DB_AuditEvent

def test_pipeline_integration(db_session):
    agent = MemoryAgent(db_session)
    user_id = "test_user_pipe"

    # Step 1: Set initial work and city
    res1 = agent.process_message(user_id, "I work at Google in San Francisco", "session_1")
    assert len(res1.extracted_facts) == 2
    
    active_mems = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id, 
        DB_Memory.status == "active"
    ).all()
    assert len(active_mems) == 2
    
    # Verify values stored
    m_map = {m.canonical_property: m.value_canonical for m in active_mems}
    assert m_map["employer"] == "Google"
    assert m_map["city"] == "San Francisco"

    # Step 2: Trigger time-varying conflict/update
    res2 = agent.process_message(user_id, "I just moved to New York for my new job at Meta", "session_2")
    
    # Google/SF should be superseded, Meta/New York should be active
    all_mems = db_session.query(DB_Memory).filter(DB_Memory.user_id == user_id).all()
    assert len(all_mems) == 4 # 2 old (superseded) + 2 new (active)
    
    active_mems_2 = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id, 
        DB_Memory.status == "active"
    ).all()
    assert len(active_mems_2) == 2
    
    m_map_2 = {m.canonical_property: m.value_canonical for m in active_mems_2}
    assert m_map_2["employer"] == "Meta"
    assert m_map_2["city"] == "New York"
    
    # Check audit log events
    audits = db_session.query(DB_AuditEvent).filter(DB_AuditEvent.user_id == user_id).all()
    assert len(audits) >= 4  # 2 creations in step 1, 2 updates + 2 creations in step 2 (can check details)
    
    superseded_events = [e for e in audits if e.event_type == "superseded"]
    assert len(superseded_events) == 2
