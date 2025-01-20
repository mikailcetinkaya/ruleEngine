import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticValidator:
    def __init__(self):
        # Load the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.8  # Adjust this threshold as needed

    def get_embeddings(self, text):
        """Generate embeddings for the given text"""
        return self.model.encode([text])[0]

    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def check_semantic_overlap(self, rule1, rule2):
        """Check if two rules have semantic overlap"""
        # Combine title and context for comprehensive comparison
        text1 = f"{rule1['context']}"
        text2 = f"{rule2['context']}"

        # Get embeddings
        embedding1 = self.get_embeddings(text1)
        embedding2 = self.get_embeddings(text2)

        # Calculate similarity
        similarity = self.calculate_similarity(embedding1, embedding2)

        return similarity >= self.similarity_threshold


def validate_rule(new_rule, existing_rules):
    """
    Validate a new rule against existing rules
    Returns a dict with validation result and message
    """
    validator = SemanticValidator()

    for existing_rule in existing_rules:
        if validator.check_semantic_overlap(new_rule, existing_rule):
            return {
                "is_valid": False,
                "message": f"Semantic overlap detected with existing rule: {existing_rule['title']}"
            }

    return {
        "is_valid": True,
        "message": "Rule is valid"
    }
