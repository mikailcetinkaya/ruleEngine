import qdrant_client as qc
from qdrant_client.http import models
from typing import List, Dict, Optional
import numpy as np
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDB:
    def __init__(self, collection_name: str = "rule_embeddings"):
        """Initialize Qdrant vector database client"""
        self.client = qc.QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure collection exists with the right schema"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,  # Size matches the MiniLM model's output
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection: {str(e)}")

    def store_embedding(self,
                        embedding: np.ndarray,
                        text: str,
                        rule_id: str,
                        metadata: Optional[Dict] = None) -> bool:
        """Store embedding and associated text in vector database"""
        try:
            # Prepare metadata
            payload = {
                "text": text,
                "rule_id": rule_id
            }
            if metadata:
                payload.update(metadata)

            # Store vector
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=str(uuid.uuid4()),  # Use UUID for point ID
                        vector=embedding.tolist(),
                        payload=payload
                    )
                ]
            )
            return True
        except Exception as e:
            logger.error(f"Error storing embedding: {str(e)}")
            return False

    def search_similar(self,
                       embedding: np.ndarray,
                       threshold: float = 0.8,
                       limit: int = 5) -> List[Dict]:
        """Search for similar embeddings in the database"""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding.tolist(),
                limit=limit,
                score_threshold=threshold
            )

            return [
                {
                    "text": hit.payload["text"],
                    "rule_id": hit.payload["rule_id"],
                    "similarity": hit.score,
                    **{k: v for k, v in hit.payload.items()
                       if k not in ["text", "rule_id"]}
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Error searching embeddings: {str(e)}")
            return []

    def delete_rule_embeddings(self, rule_id: str) -> bool:
        """Delete all embeddings associated with a rule"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="rule_id",
                                match=models.MatchValue(value=rule_id)
                            )
                        ]
                    )
                )
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting rule embeddings: {str(e)}")
            return False