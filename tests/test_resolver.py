import pytest
from app.models import ConflictInfo, ExtractedFact
from app.resolver import resolver

def test_resolve_temporal_update():
    new_fact = ExtractedFact(
        property_name="city",
        value_raw="San Francisco"
    )
    conflict = ConflictInfo(
        new_fact=new_fact,
        existing_memory_id=1,
        existing_value="New York",
        conflict_type="temporal_update"
    )
    
    action = resolver.resolve(conflict)
    assert action.action == "replace"
    assert action.status == "active"
    assert action.resolver_type == "rule_recency"

def test_resolve_stable_contradiction():
    new_fact = ExtractedFact(
        property_name="birthday",
        value_raw="July 20"
    )
    conflict = ConflictInfo(
        new_fact=new_fact,
        existing_memory_id=1,
        existing_value="July 15",
        conflict_type="stable_contradiction"
    )
    
    action = resolver.resolve(conflict)
    assert action.action == "dispute"
    assert action.status == "disputed"
    assert action.resolver_type == "rule_stability"

def test_resolve_preference_reversal():
    new_fact = ExtractedFact(
        property_name="preference",
        value_raw="likes sushi"
    )
    conflict = ConflictInfo(
        new_fact=new_fact,
        existing_memory_id=1,
        existing_value="hates sushi",
        conflict_type="temporal_update"  # preferences are time-varying
    )
    
    action = resolver.resolve(conflict)
    assert action.action == "replace"
    assert action.status == "active"
    assert action.resolver_type == "rule_preference"
