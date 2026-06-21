from typing import List, Optional
from app.models import ExtractedFact, ConflictInfo, DB_Memory
from app.property_registry import registry

class ConflictDetector:
    def detect_conflicts(
        self,
        new_fact: ExtractedFact,
        canonical_property: str,
        value_canonical: str,
        active_memories: List[DB_Memory],
        db_entity_id: Optional[int] = None,
        db_relationship_id: Optional[int] = None
    ) -> List[ConflictInfo]:
        conflicts = []
        prop_def = registry.get(canonical_property)

        # If property allows multiple active values, they can coexist without conflict
        if prop_def.multi_value:
            if canonical_property == "preference":
                import re
                new_m = re.match(r"^(likes|hates)\s+(.+)$", value_canonical.lower())
                if new_m:
                    new_sent, new_target = new_m.group(1), new_m.group(2).strip()
                    for existing in active_memories:
                        # Match same entity (if db_entity_id matches or strings match)
                        entity_match = (
                            (db_entity_id is not None and existing.entity_id == db_entity_id) or 
                            (db_entity_id is None and existing.entity_id == new_fact.entity_id)
                        )
                        if existing.canonical_property == "preference" and entity_match:
                            exist_m = re.match(r"^(likes|hates)\s+(.+)$", existing.value_canonical.lower())
                            if exist_m:
                                exist_sent, exist_target = exist_m.group(1), exist_m.group(2).strip()
                                if new_target == exist_target and new_sent != exist_sent:
                                    conflicts.append(ConflictInfo(
                                        new_fact=new_fact,
                                        existing_memory_id=existing.id,
                                        existing_value=existing.value_canonical,
                                        conflict_type="temporal_update"
                                    ))
            return conflicts

        # Find any active memory with the same canonical property and entity
        for existing in active_memories:
            if existing.canonical_property == canonical_property:
                # Resolve entity match
                entity_match = False
                if db_entity_id is not None:
                    entity_match = (existing.entity_id == db_entity_id)
                else:
                    # Fallback to string comparison for backward-compatibility in tests
                    entity_match = (existing.entity_id == new_fact.entity_id or str(existing.entity_id) == str(new_fact.entity_id))
                
                if entity_match:
                    # Check if values differ
                    if existing.value_canonical.strip().lower() != value_canonical.strip().lower():
                        # Conflict detected!
                        if prop_def.stable:
                            conflict_type = "stable_contradiction"
                        else:
                            conflict_type = "temporal_update"
                            
                        conflicts.append(ConflictInfo(
                            new_fact=new_fact,
                            existing_memory_id=existing.id,
                            existing_value=existing.value_canonical,
                            conflict_type=conflict_type
                        ))
                    
        return conflicts

conflict_detector = ConflictDetector()
