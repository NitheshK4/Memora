import time
import pytest
from app.memory_agent import MemoryAgent
from app.models import DB_Memory

def test_performance_memory_matching_latency(db_session):
    agent = MemoryAgent(db_session)
    user_id = "perf_user"
    
    # Measure time to insert and process
    start_time = time.time()
    res1 = agent.process_message(user_id, "I work at Google in San Francisco", "session_perf")
    end_time = time.time()
    
    latency = end_time - start_time
    # Assert latency is reasonable (e.g. < 500ms for pure local execution)
    assert latency < 0.5
    
    # Measure question matching latency
    start_time_q = time.time()
    res2 = agent.process_message(user_id, "Where do I work?", "session_perf")
    end_time_q = time.time()
    
    latency_q = end_time_q - start_time_q
    assert latency_q < 0.2
