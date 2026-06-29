import os
import json
import re
import requests
from typing import List, Dict, Any
from app.config import settings
from app.models import ExtractedFact
from app.utils import logger

class FactExtractor:
    def extract_facts(self, text: str) -> List[ExtractedFact]:
        if settings.is_openai_configured:
            try:
                return self._extract_with_llm(text)
            except Exception as e:
                # Log error and fallback
                logger.warning("LLM extraction failed, falling back to rules: %s", e)
                return self._extract_with_rules(text)
        else:
            return self._extract_with_rules(text)

    def _extract_with_llm(self, text: str) -> List[ExtractedFact]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }
        
        system_prompt = (
            "You are a structured fact extraction assistant. Extract personal facts about the user from their message. "
            "Return a JSON object with a single key 'facts' containing a list of objects. Each object must have these fields:\n"
            "- property_name: (e.g. 'employer', 'city', 'birthday', 'dog_name', 'preference', 'hobby')\n"
            "- value_raw: the raw value extracted from the text\n"
            "- entity_type: 'self' or 'dog' or 'person' depending on who the fact is about\n"
            "- entity_id: 'self' or a name (e.g. if the user talks about a specific dog or person)\n"
            "- confidence: a float between 0.0 and 1.0 representing your confidence\n"
            "\n"
            "Only extract clear factual statements. Do not extract questions, opinions, or general conversation. "
            "If no facts are present, return an empty list."
        )
        
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
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
        facts_list = parsed.get("facts", [])
        
        results = []
        for f in facts_list:
            results.append(ExtractedFact(
                entity_type=f.get("entity_type", "self"),
                entity_id=f.get("entity_id", "self"),
                property_name=f.get("property_name"),
                value_raw=f.get("value_raw"),
                confidence=f.get("confidence", 0.9),
                source_text=text
            ))
        return results

    def _extract_with_rules(self, text: str) -> List[ExtractedFact]:
        facts = []
        
        # 1. Employer + City (e.g., "I work at Google in San Francisco")
        m = re.search(r"i work at ([A-Za-z0-9\s\.\-]+?)\s+in\s+([A-Za-z0-9\s\.\-]+?)(?:\s+(?:on|for|at|with|my|due|actually)\b|$)", text, re.IGNORECASE)
        if m:
            facts.append(ExtractedFact(
                property_name="employer",
                value_raw=m.group(1).strip(),
                confidence=0.9,
                source_text=text
            ))
            facts.append(ExtractedFact(
                property_name="city",
                value_raw=m.group(2).strip(),
                confidence=0.9,
                source_text=text
            ))
            return facts

        # 2. Employer single (e.g., "I work at Google", "my job at Meta", "new job at Meta")
        m = re.search(r"i work at ([A-Za-z0-9\s\.\-]+?)(?:\s+(?:in|on|for|at|with|my|due|actually)\b|$)", text, re.IGNORECASE)
        if not m:
            m = re.search(r"job at ([A-Za-z0-9\s\.\-]+?)(?:\s+(?:in|on|for|at|with|my|due|actually)\b|$)", text, re.IGNORECASE)
        if m:
            facts.append(ExtractedFact(
                property_name="employer",
                value_raw=m.group(1).strip(),
                confidence=0.85,
                source_text=text
            ))

        # 3. City single (e.g., "I live in San Francisco", "I moved to New York")
        m = re.search(r"i live in ([A-Za-z0-9\s\.\-]+?)(?:\s+(?:on|for|at|with|my|due|actually)\b|$)", text, re.IGNORECASE)
        if not m:
            m = re.search(r"i (?:just )?moved to ([A-Za-z0-9\s\.\-]+?)(?:\s+(?:for|at|in|my|on|to|with|due|actually)\b|$)", text, re.IGNORECASE)
        if m:
            facts.append(ExtractedFact(
                property_name="city",
                value_raw=m.group(1).strip(),
                confidence=0.85,
                source_text=text
            ))

        # 4. Dog's name (e.g., "My dog's name is Max", "My dog is named Max")
        m = re.search(r"my dog's name is ([A-Za-z]+)", text, re.IGNORECASE)
        if not m:
            m = re.search(r"my dog is named ([A-Za-z]+)", text, re.IGNORECASE)
        if m:
            facts.append(ExtractedFact(
                entity_type="dog",
                entity_id="dog_primary",
                property_name="dog_name",
                value_raw=m.group(1).strip(),
                confidence=0.9,
                source_text=text
            ))

        # 5. Birthday (e.g., "My birthday is July 15th")
        m = re.search(r"my birthday is ([A-Za-z0-9\s\d,/\-]+?)(?:\s+(?:and|for|on|due|actually)\b|$)", text, re.IGNORECASE)
        if m:
            facts.append(ExtractedFact(
                property_name="birthday",
                value_raw=m.group(1).strip(),
                confidence=0.9,
                source_text=text
            ))

        # 6. Preference (e.g., "I hate spicy food", "I love spicy food actually", "I like sushi")
        m = re.search(r"i (love|like) ([A-Za-z0-9\s\.\-]+?)(?:\s+(?:actually|but|and)\b|$)", text, re.IGNORECASE)
        if m:
            action = m.group(1).lower()
            food = m.group(2).strip()
            # If the user specified food preference, keep it clean
            facts.append(ExtractedFact(
                property_name="preference",
                value_raw=f"likes {food}",
                confidence=0.85,
                source_text=text
            ))
            
        m = re.search(r"i (hate|dislike) ([A-Za-z0-9\s\.\-]+?)(?:\s+(?:actually|but|and)\b|$)", text, re.IGNORECASE)
        if m:
            food = m.group(2).strip()
            facts.append(ExtractedFact(
                property_name="preference",
                value_raw=f"hates {food}",
                confidence=0.85,
                source_text=text
            ))

        # 7. Hobby (e.g., "I enjoy painting", "My hobby is swimming", "I like to play chess")
        m = re.search(r"i (?:enjoy|do|practice|play)\s+([A-Za-z0-9\s\.\-]+?)(?:\s+(?:on|every|at|with|in|for|and|but)\b|$)", text, re.IGNORECASE)
        if not m:
            m = re.search(r"my hobb(?:y|ies)\s+(?:is|are|include)\s+([A-Za-z0-9\s,\.\-]+?)(?:\s+(?:and|but|on|at)\b|$)", text, re.IGNORECASE)
        if m:
            hobby_val = m.group(1).strip().rstrip(",.")
            if hobby_val and len(hobby_val) > 1:
                facts.append(ExtractedFact(
                    property_name="hobby",
                    value_raw=hobby_val,
                    confidence=0.8,
                    source_text=text
                ))

        # 8. User's name (e.g., "My name is Alice", "I'm Bob", "Call me Charlie")
        m = re.search(r"(?:my name is|i'm|i am|call me)\s+([A-Z][a-z]+)", text)
        if m:
            name_val = m.group(1).strip()
            if len(name_val) >= 2:
                facts.append(ExtractedFact(
                    property_name="name",
                    value_raw=name_val,
                    confidence=0.9,
                    source_text=text
                ))

        return facts

extractor = FactExtractor()
