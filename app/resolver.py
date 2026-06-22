import requests
import json
from typing import Optional
from app.config import settings
from app.models import ConflictInfo, ResolutionAction
from app.property_registry import registry
from app.utils import logger

class ConflictResolver:
    def resolve(self, conflict: ConflictInfo) -> ResolutionAction:
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
            try:
                return self._resolve_with_llm(conflict)
            except Exception as e:
                logger.warning("LLM resolver failed, falling back to rules: %s", e)
                return self._resolve_with_rules(conflict)
        else:
            return self._resolve_with_rules(conflict)

    def _resolve_with_llm(self, conflict: ConflictInfo) -> ResolutionAction:
        prop_name = conflict.new_fact.property_name
        prop_def = registry.get(prop_name)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }
        
        system_prompt = (
            "You are a memory resolution engine for an LLM agent. A conflict has occurred between an existing memory and a new fact.\n"
            "Analyze the stability and nature of the property and decide the correct resolution.\n"
            "\n"
            "Property Registry Definition:\n"
            f"- Property: {prop_name}\n"
            f"- Stable: {prop_def.stable} (Should not change over time, e.g. birthday)\n"
            f"- Multi-value: {prop_def.multi_value} (Can have multiple active values)\n"
            "\n"
            "Conflict Details:\n"
            f"- Existing memory value: '{conflict.existing_value}'\n"
            f"- New fact candidate value: '{conflict.new_fact.value_raw}'\n"
            f"- Source text of new fact: '{conflict.new_fact.source_text or ''}'\n"
            "\n"
            "Return a JSON object containing:\n"
            "- action: 'replace' (supersede old, make new active), 'keep_existing' (ignore new), 'dispute' (mark new disputed), or 'merge' (hobbies/lists)\n"
            "- status: 'active', 'superseded', 'disputed', or 'rejected'\n"
            "- reason: A clear explanation of why you made this choice (useful for user logs)\n"
            "- resolver_type: 'llm_reasoning'"
        )
        
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Resolve conflict for property: {prop_name}"}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        res_data = response.json()
        content = res_data["choices"][0]["message"]["content"]
        
        parsed = json.loads(content)
        return ResolutionAction(
            action=parsed.get("action", "replace"),
            status=parsed.get("status", "active"),
            reason=parsed.get("reason", "Resolved via LLM reasoning."),
            resolver_type="llm_reasoning"
        )

    def _resolve_with_rules(self, conflict: ConflictInfo) -> ResolutionAction:
        prop_name = conflict.new_fact.property_name
        prop_def = registry.get(prop_name)
        
        if conflict.conflict_type == "stable_contradiction":
            return ResolutionAction(
                action="dispute",
                status="disputed",
                reason=f"Stable property '{prop_name}' cannot have conflicting values ('{conflict.existing_value}' vs '{conflict.new_fact.value_raw}'). Marked new fact as disputed.",
                resolver_type="rule_stability"
            )
            
        if prop_name == "preference":
            return ResolutionAction(
                action="replace",
                status="active",
                reason=f"Preference updated from '{conflict.existing_value}' to '{conflict.new_fact.value_raw}' due to preference reversal.",
                resolver_type="rule_preference"
            )

        if conflict.conflict_type == "temporal_update":
            return ResolutionAction(
                action="replace",
                status="active",
                reason=f"Time-varying property '{prop_name}' updated from '{conflict.existing_value}' to '{conflict.new_fact.value_raw}' due to recency.",
                resolver_type="rule_recency"
            )

        return ResolutionAction(
            action="keep_existing",
            status="rejected",
            reason="Unresolved conflict fallback, rejected new fact.",
            resolver_type="rule_fallback"
        )

resolver = ConflictResolver()
