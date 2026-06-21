import pytest
from app.models import ExtractedFact, DB_Memory
from app.conflict_detector import conflict_detector
from app.normalizer import normalize_fact

def test_no_conflict_repeated_value():
    new_fact = ExtractedFact(
        property_name="city",
        value_raw="New York"
    )
    # Existing identical
    existing = DB_Memory(
        id=1,
        user_id="user1",
        canonical_property="city",
        value_canonical="New York",
        entity_id="self",
        status="active"
    )
    
    canon_prop, canon_val = normalize_fact(new_fact.property_name, new_fact.value_raw)
    conflicts = conflict_detector.detect_conflicts(new_fact, canon_prop, canon_val, [existing])
    assert len(conflicts) == 0

def test_temporal_update_conflict():
    new_fact = ExtractedFact(
        property_name="city",
        value_raw="San Francisco"
    )
    # Existing different
    existing = DB_Memory(
        id=1,
        user_id="user1",
        canonical_property="city",
        value_canonical="New York",
        entity_id="self",
        status="active"
    )
    
    canon_prop, canon_val = normalize_fact(new_fact.property_name, new_fact.value_raw)
    conflicts = conflict_detector.detect_conflicts(new_fact, canon_prop, canon_val, [existing])
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == "temporal_update"
    assert conflicts[0].existing_value == "New York"

def test_stable_contradiction_conflict():
    new_fact = ExtractedFact(
        property_name="birthday",
        value_raw="July 20"
    )
    # Existing different
    existing = DB_Memory(
        id=1,
        user_id="user1",
        canonical_property="birthday",
        value_canonical="July 15",
        entity_id="self",
        status="active"
    )
    
    canon_prop, canon_val = normalize_fact(new_fact.property_name, new_fact.value_raw)
    conflicts = conflict_detector.detect_conflicts(new_fact, canon_prop, canon_val, [existing])
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == "stable_contradiction"
    assert conflicts[0].existing_value == "July 15"
