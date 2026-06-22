import os
import math
import numpy as np
import requests
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.utils import logger

class LocalVectorStore:
    def __init__(self):
        # List of dicts: {"id": memory_id, "vector": np.ndarray, "text": str, "metadata": dict}
        self.registry: List[Dict[str, Any]] = []
        self._vocabulary: Dict[str, int] = {}
        self._idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        return [w for w in text.lower().split() if w.isalnum()]

    def _rebuild_vocabulary_and_idf(self):
        docs = [self._tokenize(item["text"]) for item in self.registry]
        if not docs:
            return
            
        all_words = set(w for doc in docs for w in doc)
        self._vocabulary = {word: idx for idx, word in enumerate(all_words)}
        
        # Calculate IDF
        num_docs = len(docs)
        self._idf = {}
        for word in all_words:
            df = sum(1 for doc in docs if word in doc)
            self._idf[word] = math.log((1 + num_docs) / (1 + df)) + 1

    def _get_tfidf_vector(self, text: str) -> np.ndarray:
        tokens = self._tokenize(text)
        vector = np.zeros(len(self._vocabulary))
        if not self._vocabulary:
            return vector
            
        # Count TF
        tf = {}
        for t in tokens:
            if t in self._vocabulary:
                tf[t] = tf.get(t, 0) + 1
                
        for word, count in tf.items():
            idx = self._vocabulary[word]
            vector[idx] = count * self._idf.get(word, 1.0)
            
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector

    def add_document(self, doc_id: int, text: str, metadata: Optional[Dict[str, Any]] = None):
        self.registry = [item for item in self.registry if item["id"] != doc_id]
        self.registry.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata or {},
            "vector": None  # Will compute/update dynamically
        })
        self._rebuild_vocabulary_and_idf()
        
        # Update all vectors with the new vocabulary
        for item in self.registry:
            item["vector"] = self._get_tfidf_vector(item["text"])

    def search(self, query: str, user_id: str, limit: int = 5) -> List[Tuple[int, float]]:
        # Filter by user_id metadata if present
        candidates = [item for item in self.registry if item["metadata"].get("user_id") == user_id]
        if not candidates:
            return []
            
        q_vector = self._get_tfidf_vector(query)
        q_norm = np.linalg.norm(q_vector)
        if q_norm == 0:
            return []
            
        results = []
        for item in candidates:
            if item["vector"] is None or len(item["vector"]) != len(q_vector):
                continue
            sim = float(np.dot(q_vector, item["vector"]))
            results.append((item["id"], sim))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

class OpenAIVectorStore:
    def __init__(self, local_fallback: LocalVectorStore):
        self.local_store = local_fallback
        self.registry: List[Dict[str, Any]] = []

    def _get_openai_embedding(self, text: str) -> List[float]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }
        payload = {
            "input": text,
            "model": "text-embedding-3-small"
        }
        res = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=payload,
            timeout=10
        )
        res.raise_for_status()
        return res.json()["data"][0]["embedding"]

    def add_document(self, doc_id: int, text: str, metadata: Optional[Dict[str, Any]] = None):
        if not settings.OPENAI_API_KEY or not settings.OPENAI_API_KEY.strip():
            self.local_store.add_document(doc_id, text, metadata)
            return

        try:
            vec = self._get_openai_embedding(text)
            self.registry = [item for item in self.registry if item["id"] != doc_id]
            self.registry.append({
                "id": doc_id,
                "text": text,
                "metadata": metadata or {},
                "vector": np.array(vec)
            })
        except Exception as e:
            logger.warning("OpenAI embedding generation failed, falling back to local: %s", e)
            self.local_store.add_document(doc_id, text, metadata)

    def search(self, query: str, user_id: str, limit: int = 5) -> List[Tuple[int, float]]:
        if not settings.OPENAI_API_KEY or not settings.OPENAI_API_KEY.strip():
            return self.local_store.search(query, user_id, limit)

        try:
            q_vec = np.array(self._get_openai_embedding(query))
            candidates = [item for item in self.registry if item["metadata"].get("user_id") == user_id]
            
            results = []
            for item in candidates:
                # Cosine similarity for normalized vectors is just dot product
                sim = float(np.dot(q_vec, item["vector"]))
                results.append((item["id"], sim))
                
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.warning("OpenAI embedding search failed, falling back to local: %s", e)
            return self.local_store.search(query, user_id, limit)

# Singleton local instance
local_vector_index = LocalVectorStore()
vector_store = OpenAIVectorStore(local_vector_index)
