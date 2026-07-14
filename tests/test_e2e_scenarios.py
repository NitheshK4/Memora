import pytest
from app.memory_agent import MemoryAgent
from app.models import DB_Memory

def test_scenario_employer_location_change(db_session):
    agent = MemoryAgent(db_session)
    user_id = "e2e_user_1"
    
    # Session 1:
    r1 = agent.process_message(user_id, "I work at Google in San Francisco", "session_1")
    assert "Google" in r1.response
    assert "San Francisco" in r1.response
    
    # Session 2:
    r2 = agent.process_message(user_id, "I just moved to New York for my new job at Meta", "session_2")
    assert "Meta" in r2.response
    assert "New York" in r2.response
    
    # Check states
    google_mem = db_session.query(DB_Memory).filter(DB_Memory.user_id == user_id, DB_Memory.value_canonical == "Google").first()
    meta_mem = db_session.query(DB_Memory).filter(DB_Memory.user_id == user_id, DB_Memory.value_canonical == "Meta").first()
    
    assert google_mem.status == "superseded"
    assert meta_mem.status == "active"

def test_scenario_dog_name_recall(db_session):
    agent = MemoryAgent(db_session)
    user_id = "e2e_user_2"
    
    # Session 1:
    agent.process_message(user_id, "My dog's name is Max", "session_1")
    
    # Session 2:
    r2 = agent.process_message(user_id, "What's my dog's name?", "session_2")
    assert "Max" in r2.response

def test_scenario_birthday_recall_and_conflict(db_session):
    agent = MemoryAgent(db_session)
    user_id = "e2e_user_3"
    
    # Session 1:
    agent.process_message(user_id, "My birthday is July 15th", "session_1")
    
    # Session 2: Ask
    r2 = agent.process_message(user_id, "When is my birthday?", "session_2")
    assert "July 15" in r2.response
    
    # Session 3: Conflicting birthday
    r3 = agent.process_message(user_id, "My birthday is July 20th", "session_3")
    
    # System should detect stable conflict, keep first as active, mark second as disputed
    active_bday = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id,
        DB_Memory.canonical_property == "birthday",
        DB_Memory.status == "active"
    ).first()
    
    disputed_bday = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id,
        DB_Memory.canonical_property == "birthday",
        DB_Memory.status == "disputed"
    ).first()
    
    assert active_bday is not None
    assert active_bday.value_canonical == "July 15"
    
    assert disputed_bday is not None
    assert disputed_bday.value_canonical == "July 20"
    
    # Response should raise warning or ask for clarification
    assert "clarify" in r3.response or "conflict" in r3.response or "conflicting" in r3.response

def test_scenario_preference_reversal(db_session):
    agent = MemoryAgent(db_session)
    user_id = "e2e_user_4"
    
    # Session 1:
    agent.process_message(user_id, "I hate spicy food", "session_1")
    
    # Session 2:
    r2 = agent.process_message(user_id, "I love spicy food actually", "session_2")
    
    # Old preference should be superseded, new active
    old_pref = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id, 
        DB_Memory.value_canonical == "hates spicy food"
    ).first()
    new_pref = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id, 
        DB_Memory.value_canonical == "likes spicy food"
    ).first()
    
    assert old_pref.status == "superseded"
    assert new_pref.status == "active"
    assert "likes spicy food" in r2.response or "updated" in r2.response

def test_scenario_multi_property_extraction(db_session):
    agent = MemoryAgent(db_session)
    user_id = "e2e_user_5"
    
    # Send a dialog that has employer and city first
    agent.process_message(user_id, "I work at Google in San Francisco", "session_multi")
    # Send a dialog that has email and phone
    agent.process_message(user_id, "my email is alice@example.com and my phone number is +1-800-555-0199", "session_multi")
    
    # Verify DB records
    active_mems = db_session.query(DB_Memory).filter(
        DB_Memory.user_id == user_id,
        DB_Memory.status == "active"
    ).all()
    
    # We expect 4 active memories
    assert len(active_mems) == 4
    
    properties = {m.canonical_property: m.value_canonical for m in active_mems}
    assert properties["employer"] == "Google"
    assert properties["city"] == "San Francisco"
    assert properties["email"] == "alice@example.com"
    assert properties["phone"] == "+18005550199"

