"""
FAISS index manager for efficient semantic similarity search.
Handles indexing, persistence, and retrieval operations.
"""

import numpy as np
import faiss
from typing import List, Tuple, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)


class FAISSIndexManager:
    """
    Manages FAISS index for semantic search over assessment catalog.
    Supports building, saving, loading, and searching.
    """

    def __init__(self, embedding_dimension: int):
        """
        Initialize FAISS index manager.
        
        Args:
            embedding_dimension: Dimensionality of embedding vectors
        """
        self.embedding_dimension = embedding_dimension
        self.index = None
        self.metadata = []  # Stores assessment metadata in index order

    def build_index(self, embeddings: np.ndarray) -> None:
        """
        Build FAISS index from embeddings.
        Uses L2 (Euclidean) distance metric.
        
        Args:
            embeddings: Matrix of shape (num_items, embedding_dim)
        """
        if embeddings.shape[1] != self.embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.embedding_dimension}, "
                f"got {embeddings.shape[1]}"
            )

        logger.info(f"Building FAISS index from {len(embeddings)} embeddings")
        
        # Create L2 (Euclidean) index
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        
        # Add vectors to index
        embeddings_float32 = embeddings.astype(np.float32)
        self.index.add(embeddings_float32)
        
        logger.info(f"Index built successfully with {self.index.ntotal} items")

    def add_metadata(self, metadata_list: List[dict]) -> None:
        """
        Store metadata (assessment info) corresponding to index entries.
        Must be in same order as embeddings passed to build_index.
        
        Args:
            metadata_list: List of assessment dicts with 'name', 'url', 'test_type'
        """
        self.metadata = metadata_list.copy()

    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[dict], List[float]]:
        """
        Search index for most similar assessments.
        
        Args:
            query_embedding: Query vector (embedding_dim,)
            k: Number of results to return
            
        Returns:
            Tuple of (list of metadata dicts, list of distances/scores)
        """
        if self.index is None:
            raise RuntimeError("Index not built. Call build_index() first")

        if k > self.index.ntotal:
            logger.warning(f"k={k} exceeds index size {self.index.ntotal}, using max")
            k = self.index.ntotal

        # Reshape query for FAISS
        query = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query, k)
        
        # Extract results
        results = []
        scores = []
        
        for idx, distance in zip(indices[0], distances[0]):
            if 0 <= idx < len(self.metadata):
                results.append(self.metadata[int(idx)])
                # Convert L2 distance to similarity score (lower distance = higher similarity)
                similarity = 1.0 / (1.0 + float(distance))
                scores.append(similarity)
        
        return results, scores

    def save(self, index_path: str, metadata_path: str) -> None:
        """
        Save index and metadata to disk.
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save metadata JSON
        """
        if self.index is None:
            raise RuntimeError("Index not built. Nothing to save")

        # Save FAISS index
        os.makedirs(os.path.dirname(index_path) or ".", exist_ok=True)
        faiss.write_index(self.index, index_path)
        logger.info(f"Index saved to {index_path}")

        # Save metadata
        os.makedirs(os.path.dirname(metadata_path) or ".", exist_ok=True)
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)
        logger.info(f"Metadata saved to {metadata_path}")

    def load(self, index_path: str, metadata_path: str) -> None:
        """
        Load index and metadata from disk.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
        """
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        # Load FAISS index
        self.index = faiss.read_index(index_path)
        logger.info(f"Index loaded from {index_path} ({self.index.ntotal} items)")

        # Load metadata
        with open(metadata_path, "r") as f:
            self.metadata = json.load(f)
        
        if len(self.metadata) != self.index.ntotal:
            logger.warning(
                f"Metadata size ({len(self.metadata)}) != index size ({self.index.ntotal})"
            )

    def is_ready(self) -> bool:
        """Check if index is ready for searches."""
        return self.index is not None and len(self.metadata) > 0
