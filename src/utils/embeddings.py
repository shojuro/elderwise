from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def embed(self, text: Union[str, List[str]]) -> Union[np.ndarray, List[float]]:
        """
        Generate embeddings for text
        
        Args:
            text: Single string or list of strings to embed
            
        Returns:
            Numpy array for single text, list of embeddings for multiple texts
        """
        if isinstance(text, str):
            embedding = self.model.encode(text)
            return embedding.tolist()
        else:
            embeddings = self.model.encode(text)
            return embeddings.tolist()
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of strings to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(texts, batch_size=batch_size)
        return embeddings.tolist()


# Global instance
embedding_service = EmbeddingService()