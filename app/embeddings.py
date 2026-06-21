import math
import re
from typing import Dict, List

def tokenize(text: str) -> List[str]:
    # Match alphanumeric characters
    return re.findall(r'\w+', text.lower())

def get_bow(text: str) -> Dict[str, int]:
    tokens = tokenize(text)
    bow: Dict[str, int] = {}
    for t in tokens:
        bow[t] = bow.get(t, 0) + 1
    return bow

def cosine_similarity_bow(text1: str, text2: str) -> float:
    if not text1 or not text2:
        return 0.0
    bow1 = get_bow(text1)
    bow2 = get_bow(text2)
    
    intersection = set(bow1.keys()) & set(bow2.keys())
    numerator = sum([bow1[x] * bow2[x] for x in intersection])
    
    sum1 = sum([val**2 for val in bow1.values()])
    sum2 = sum([val**2 for val in bow2.values()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if not denominator:
        return 0.0
    return float(numerator / denominator)

class SimpleSimilarityService:
    """
    Lightweight similarity service with zero dependencies.
    Can be replaced or extended with sentence-transformers.
    """
    def calculate_similarity(self, text1: str, text2: str) -> float:
        return cosine_similarity_bow(text1, text2)

    def rank_documents(self, query: str, documents: List[str]) -> List[float]:
        return [self.calculate_similarity(query, doc) for doc in documents]

similarity_service = SimpleSimilarityService()
