"""
Embeddings pipeline for converting text to vectors.
Uses sentence-transformers for semantic embeddings.
"""

import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """
    Manages embeddings generation using sentence-transformers.
    Lazy-loads model on first use for efficiency.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embeddings manager.
        
        Args:
            model_name: HuggingFace model identifier.
                       "all-MiniLM-L6-v2" is lightweight and fast (~22MB).
        """
        self.model_name = model_name
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load model on first access."""
        if self._model is None:
            logger.info(f"Loading embeddings model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed single text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector (numpy array)
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input must be non-empty string")
        
        embeddings = self.model.encode(text, convert_to_numpy=True)
        return embeddings

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed multiple texts efficiently.
        
        Args:
            texts: List of strings to embed
            batch_size: Number of texts to process at once
            
        Returns:
            Embeddings matrix (num_texts x embedding_dim)
        """
        if not texts:
            raise ValueError("Input texts cannot be empty")
        
        if not all(isinstance(t, str) for t in texts):
            raise ValueError("All inputs must be strings")

        logger.info(f"Embedding {len(texts)} texts in batches of {batch_size}")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get dimensionality of embeddings."""
        # Create dummy embedding to determine dimension
        dummy = self.embed_text("test")
        return len(dummy)
