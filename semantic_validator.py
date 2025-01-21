import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticValidator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the SemanticValidator with configurable parameters

        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = 0.8
        self.min_context_length = 10  # Minimum context length to analyze

    def get_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings for the given text"""
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        if not cleaned_text:
            return np.zeros(384)  # Return zero vector for empty text
        return self.model.encode([cleaned_text])[0]

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better embedding generation"""
        if not isinstance(text, str):
            return ""

        # Basic cleaning
        cleaned = text.strip()
        # Remove excessive whitespace
        cleaned = ' '.join(cleaned.split())
        return cleaned

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings with error handling
        """
        try:
            if np.all(embedding1 == 0) or np.all(embedding2 == 0):
                return 0.0

            similarity = np.dot(embedding1, embedding2) / (
                    np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    def find_similar_segments(self, text1: str, text2: str) -> List[Tuple[str, str, float]]:
        """
        Find similar segments between two texts

        Returns:
            List of tuples containing (segment1, segment2, similarity_score)
        """
        # Split texts into sentences or meaningful segments
        segments1 = [s.strip() for s in text1.split('\n') if s.strip()]
        segments2 = [s.strip() for s in text2.split('\n') if s.strip()]

        similar_pairs = []

        for seg1 in segments1:
            if len(seg1) < self.min_context_length:
                continue

            emb1 = self.get_embeddings(seg1)

            for seg2 in segments2:
                if len(seg2) < self.min_context_length:
                    continue

                emb2 = self.get_embeddings(seg2)
                similarity = self.calculate_similarity(emb1, emb2)

                if similarity >= self.similarity_threshold:
                    similar_pairs.append((seg1, seg2, similarity))

        return similar_pairs

    def check_semantic_overlap(self, rule1: Dict, rule2: Dict) -> Tuple[bool, List[Dict]]:
        """
        Check if two rules have semantic overlap and provide detailed feedback

        Returns:
            Tuple of (has_overlap: bool, overlap_details: List[Dict])
        """
        text1 = rule1.get('context', '')
        text2 = rule2.get('context', '')

        if not text1 or not text2:
            return False, []

        similar_segments = self.find_similar_segments(text1, text2)

        if not similar_segments:
            return False, []

        overlap_details = [
            {
                'segment1': seg1,
                'segment2': seg2,
                'similarity': round(score, 3)
            }
            for seg1, seg2, score in similar_segments
        ]

        return True, overlap_details


def validate_rule(new_rule: Dict, existing_rules: List[Dict]) -> Dict:
    """
    Validate a new rule against existing rules with detailed feedback
    """
    validator = SemanticValidator()
    overlap_found = False
    detailed_feedback = []

    for existing_rule in existing_rules:
        has_overlap, overlap_details = validator.check_semantic_overlap(new_rule, existing_rule)

        if has_overlap:
            overlap_found = True
            detailed_feedback.append({
                'rule_title': existing_rule['title'],
                'overlaps': overlap_details
            })

    if overlap_found:
        return {
            "is_valid": False,
            "message": "Semantic overlap detected",
            "details": detailed_feedback
        }

    return {
        "is_valid": True,
        "message": "Rule is valid",
        "details": []
    }


if __name__ == "__main__":
    # Example usage
    validator = SemanticValidator()
    rule1 = {"context": "Payment processing must use secure channels"}
    rule2 = {"context": "All payments should be processed through encrypted channels"}
    print(validator.check_semantic_overlap(rule1, rule2))