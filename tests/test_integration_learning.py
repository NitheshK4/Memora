import pytest
from app.memory_agent import MemoryAgent
from app.models import DB_Memory

def test_repeated_sessions_and_normalization(db_session):
    agent = MemoryAgent(db_session)
    user_id = "test_user_learn"
    
    # Session 1: State living in SF
    res1 = agent.process_message(user_id, "I live in SF", "session_1")
    active_mems = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id,
        DB_Memory.status == "active"
    ).all()
    assert len(active_mems) == 1
    assert active_mems[0].value_canonical == "San Francisco" # checks normalization
    
    # Session 2: State moving to NYC
    res2 = agent.process_message(user_id, "I just moved to NYC", "session_2")
    active_mems_2 = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id,
        DB_Memory.status == "active"
    ).all()
    assert len(active_mems_2) == 1
    assert active_mems_2[0].value_canonical == "New York" # checks normalization of NYC
    
    # Session 3: Ask where I live
    res3 = agent.process_message(user_id, "Where do I live?", "session_3")
    assert "New York" in res3.response
    assert "San Francisco" not in res3.response
