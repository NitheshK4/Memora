import os
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust path to find app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import Base
from app.models import DB_Memory, ExtractedFact
from app.memory_db import MemoryDB
from app.vector_store import vector_store

def run_benchmarks():
    print("====================================================")
    print("             Memora Performance Benchmarks          ")
    print("====================================================")
    
    # 1. Setup mock database session
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    memory_db = MemoryDB(db)
    
    user_id = "bench_user"
    
    # Seed 100 mock memories
    print("Seeding 100 mock memories...")
    for i in range(100):
        fact = ExtractedFact(
            property_name=f"property_{i}",
            value_raw=f"value_value_{i}",
            confidence=0.8
        )
        memory_db.store_fact(user_id, fact, f"property_{i}", f"value_{i}")
        
    print("Seed complete.\n")
    
    # Benchmark SQL retrieval
    print("Benchmark 1: SQL Relational Query Latency (1000 iterations)...")
    start_time = time.perf_counter()
    for _ in range(1000):
        # Query active fact
        memory_db.get_active_fact(user_id, "property_50")
    end_time = time.perf_counter()
    sql_total = end_time - start_time
    sql_avg = (sql_total / 1000) * 1000 # ms
    print(f"  Total time: {sql_total:.4f} seconds")
    print(f"  Average latency: {sql_avg:.4f} milliseconds per query\n")
    
    # Benchmark Vector Retrieval
    print("Benchmark 2: Local Vector Index Cosine Matching Latency (1000 iterations)...")
    start_time = time.perf_counter()
    for _ in range(1000):
        # Query vector similarity matching
        vector_store.search("property_50", user_id, limit=5)
    end_time = time.perf_counter()
    vec_total = end_time - start_time
    vec_avg = (vec_total / 1000) * 1000 # ms
    print(f"  Total time: {vec_total:.4f} seconds")
    print(f"  Average latency: {vec_avg:.4f} milliseconds per search\n")
    
    print("====================================================")
    print(f"SQL Lookup is {vec_avg/sql_avg:.2f}x faster than Local Vector Search.")
    print("Hybrid Search combines both structures for accuracy.")
    print("====================================================")
    
    db.close()
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    run_benchmarks()
