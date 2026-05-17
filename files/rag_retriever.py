"""
RAG-based retriever for semantic search over SHL assessment catalog.
Combines embeddings + FAISS indexing for high-quality retrieval.
"""

from typing import List, Tuple, Optional
import logging
from embeddings import EmbeddingsManager
from faiss_index import FAISSIndexManager
from schemas import Recommendation

logger = logging.getLogger(__name__)


class RAGRetriever:
    """
    Semantic retriever using embeddings + FAISS.
    Returns grounded recommendations strictly from catalog.
    """

    def __init__(
        self,
        embeddings_manager: EmbeddingsManager,
        faiss_manager: FAISSIndexManager,
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ):
        """
        Initialize retriever.
        
        Args:
            embeddings_manager: EmbeddingsManager instance
            faiss_manager: FAISSIndexManager instance with loaded index
            top_k: Maximum number of results to return
            similarity_threshold: Minimum similarity score to include result
        """
        self.embeddings = embeddings_manager
        self.faiss = faiss_manager
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        if not self.faiss.is_ready():
            raise RuntimeError("FAISS index not ready. Load index before using retriever")

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_context: Optional[dict] = None
    ) -> List[Recommendation]:
        """
        Retrieve relevant assessments for query.
        
        Args:
            query: Natural language query
            top_k: Override default top_k for this search
            filter_context: Optional dict with context filters
                           (e.g., {'category': 'technical'})
        
        Returns:
            List of Recommendation objects, sorted by relevance
        """
        if not query or not isinstance(query, str):
            logger.warning("Invalid query received")
            return []

        k = top_k or self.top_k
        k = min(k, 10)  # Cap at 10 per PRD

        try:
            # Embed query
            query_embedding = self.embeddings.embed_text(query)
            
            # Search FAISS
            results, scores = self.faiss.search(query_embedding, k=k)
            
            # Filter by threshold and convert to Recommendation objects
            recommendations = []
            for metadata, score in zip(results, scores):
                if score >= self.similarity_threshold:
                    rec = Recommendation(
                        name=metadata.get("name", "Unknown"),
                        url=metadata.get("url", ""),
                        test_type=metadata.get("test_type", "Unknown")
                    )
                    recommendations.append(rec)
            
            logger.info(f"Retrieved {len(recommendations)} assessments for query")
            return recommendations[:10]  # Hard cap at 10

        except Exception as e:
            logger.error(f"Retrieval error: {e}", exc_info=True)
            return []

    def retrieve_for_context(
        self,
        role: Optional[str] = None,
        skills: Optional[List[str]] = None,
        assessment_goals: Optional[List[str]] = None
    ) -> List[Recommendation]:
        """
        Retrieve assessments based on structured hiring context.
        Builds query from context fields.
        
        Args:
            role: Job role/title
            skills: List of required skills
            assessment_goals: List of assessment goals
        
        Returns:
            List of relevant Recommendation objects
        """
        query_parts = []
        
        if role:
            query_parts.append(f"Assess {role}")
        
        if skills:
            query_parts.append(f"Skills: {', '.join(skills)}")
        
        if assessment_goals:
            query_parts.append(f"Needs: {', '.join(assessment_goals)}")
        
        if not query_parts:
            return []
        
        query = ". ".join(query_parts)
        return self.retrieve(query)

    def compare_assessments(
        self,
        assessment_names: List[str]
    ) -> Tuple[Optional[dict], Optional[dict]]:
        """
        Retrieve details for assessments to enable comparison.
        
        Args:
            assessment_names: Names of assessments to compare
            
        Returns:
            Tuple of two assessment metadata dicts (or None if not found)
        """
        results = {}
        for name in assessment_names:
            for metadata in self.faiss.metadata:
                if metadata.get("name", "").lower() == name.lower():
                    results[name] = metadata
                    break
        
        # Return tuple of up to 2 assessments
        values = list(results.values())
        return (
            values[0] if len(values) > 0 else None,
            values[1] if len(values) > 1 else None
        )
