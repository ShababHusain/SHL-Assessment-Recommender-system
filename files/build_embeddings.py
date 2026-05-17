"""
Build embeddings and FAISS indices for SHL assessment catalog.
Run once after updating catalog, then reuse indices for inference.
"""

import logging
import os
import sys
from build_catalog import load_catalog
from embeddings import EmbeddingsManager
from faiss_index import FAISSIndexManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_embeddings(
    catalog_path: str = "data/catalog.json",
    index_output_path: str = "data/faiss.index",
    metadata_output_path: str = "data/metadata.json"
):
    """
    Build embeddings and FAISS index from catalog.
    
    Args:
        catalog_path: Path to catalog.json
        index_output_path: Path to save FAISS index
        metadata_output_path: Path to save metadata
    """
    try:
        logger.info("Starting embedding pipeline...")
        
        # Step 1: Load catalog
        logger.info(f"Loading catalog from {catalog_path}...")
        catalog = load_catalog(catalog_path)
        
        if not catalog:
            logger.error("Catalog is empty")
            sys.exit(1)
        
        # Step 2: Initialize embeddings manager
        logger.info("Initializing embeddings manager...")
        embeddings_manager = EmbeddingsManager(model_name="all-MiniLM-L6-v2")
        embedding_dim = embeddings_manager.get_embedding_dimension()
        logger.info(f"Embedding dimension: {embedding_dim}")
        
        # Step 3: Create text to embed - combine name, description, category, test_type
        logger.info("Preparing texts for embedding...")
        texts_to_embed = []
        for item in catalog:
            # Create rich text representation for better embeddings
            text = (
                f"{item.get('name', '')}. "
                f"{item.get('description', '')}. "
                f"Category: {item.get('category', '')}. "
                f"Type: {item.get('test_type', '')}"
            )
            texts_to_embed.append(text)
        
        logger.info(f"Embedding {len(texts_to_embed)} assessment descriptions...")
        embeddings = embeddings_manager.embed_batch(texts_to_embed, batch_size=32)
        logger.info(f"Generated {embeddings.shape[0]} embeddings of dimension {embeddings.shape[1]}")
        
        # Step 4: Build FAISS index
        logger.info("Building FAISS index...")
        faiss_manager = FAISSIndexManager(embedding_dim)
        faiss_manager.build_index(embeddings)
        
        # Step 5: Add metadata
        logger.info("Adding metadata...")
        metadata = [
            {
                "name": item.get("name", "Unknown"),
                "description": item.get("description", ""),
                "url": item.get("url", ""),
                "duration_minutes": item.get("duration_minutes"),
                "category": item.get("category", ""),
                "test_type": item.get("test_type", "")
            }
            for item in catalog
        ]
        faiss_manager.add_metadata(metadata)
        
        # Step 6: Save index and metadata
        logger.info(f"Saving FAISS index to {index_output_path}...")
        faiss_manager.save(index_output_path, metadata_output_path)
        
        logger.info("✓ Embedding pipeline complete!")
        logger.info(f"  - Index: {index_output_path}")
        logger.info(f"  - Metadata: {metadata_output_path}")
        logger.info(f"  - Total assessments: {len(catalog)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Embedding pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    build_embeddings()
