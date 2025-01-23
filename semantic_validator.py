import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
import logging
import uuid
from vector_db import VectorDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticValidator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the SemanticValidator with vector database integration"""
        self.model = SentenceTransformer(model_name)
        self.vector_db = VectorDB()
        self.similarity_threshold = 0.8
        self.min_context_length = 10

    def get_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings for the given text"""
        cleaned_text = self._preprocess_text(text)
        if not cleaned_text:
            return np.zeros(384)
        return self.model.encode([cleaned_text])[0]

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better embedding generation"""
        if not isinstance(text, str):
            return ""
        cleaned = ' '.join(text.strip().split())
        return cleaned

    def store_rule_embeddings(self, rule: Dict) -> str:
        """Store embeddings for a new valid rule"""
        rule_id = str(uuid.uuid4())
        context = rule.get('context', '')
        segments = [s.strip() for s in context.split('\n') if s.strip()]

        for segment in segments:
            if len(segment) < self.min_context_length:
                continue

            embedding = self.get_embeddings(segment)
            metadata = {
                "title": rule.get('title', ''),
                "created_at": rule.get('created_at', '')
            }
            
            self.vector_db.store_embedding(
                embedding=embedding,
                text=segment,
                rule_id=rule_id,
                metadata=metadata
            )

        return rule_id

    def find_similar_segments(self, text: str) -> List[Dict]:
        """Find similar segments using vector database"""
        segments = [s.strip() for s in text.split('\n') if s.strip()]
        all_similar = []

        for segment in segments:
            if len(segment) < self.min_context_length:
                continue

            embedding = self.get_embeddings(segment)
            similar = self.vector_db.search_similar(
                embedding=embedding,
                threshold=self.similarity_threshold
            )
            
            if similar:
                all_similar.extend(similar)

        return all_similar

    def check_semantic_overlap(self, rule1: Dict, rule2: Dict = None) -> Tuple[bool, List[Dict]]:
        """Check semantic overlap using vector database"""
        text = rule1.get('context', '')
        if not text:
            return False, []

        similar_segments = self.find_similar_segments(text)
        
        if not similar_segments:
            return False, []

        overlap_details = [
            {
                'segment1': segment['text'],
                'segment2': text,
                'similarity': segment['similarity'],
                'rule_id': segment['rule_id'],
                'title': segment.get('title', '')
            }
            for segment in similar_segments
        ]

        return True, overlap_details


def validate_rule(new_rule: Dict, existing_rules: List[Dict]) -> Dict:
    """Validate a new rule and store if valid"""
    validator = SemanticValidator()
    
    # Check for semantic overlap
    has_overlap, overlap_details = validator.check_semantic_overlap(new_rule)
    
    if has_overlap:
        return {
            "is_valid": False,
            "message": "Semantic overlap detected",
            "details": overlap_details
        }
    
    # If valid, store embeddings and return success
    rule_id = validator.store_rule_embeddings(new_rule)
    logging.error(f"rule id: {rule_id}")
    return {
        "is_valid": True,
        "message": "Rule is valid",
        "details": [],
        "rule_id": rule_id
    }