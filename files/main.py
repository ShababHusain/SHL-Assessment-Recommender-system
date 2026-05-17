"""
FastAPI application for SHL Assessment Recommender.
Provides /health and /chat endpoints.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from schemas import ChatRequest, ChatResponse, HealthResponse, Message, MessageRole
from embeddings import EmbeddingsManager
from faiss_index import FAISSIndexManager
from rag_retriever import RAGRetriever
from llm_service import LLMService
from agent import ConversationalAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
app_state = {
    "agent": None,
    "ready": False
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for app startup/shutdown.
    Initializes RAG components on startup.
    """
    # Startup
    logger.info("Starting SHL Assessment Recommender...")
    
    try:
        # Initialize components
        embeddings = EmbeddingsManager(model_name="all-MiniLM-L6-v2")
        
        # Check for pre-built indices
        index_path = "data/faiss.index"
        metadata_path = "data/metadata.json"
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            logger.error(
                f"Index files not found at {index_path} and {metadata_path}. "
                "Run build_embeddings.py first."
            )
            raise FileNotFoundError("FAISS indices not found. Please build indices first.")
        
        # Load FAISS index
        faiss_manager = FAISSIndexManager(embeddings.get_embedding_dimension())
        faiss_manager.load(index_path, metadata_path)
        logger.info(f"Loaded FAISS index with {faiss_manager.index.ntotal} assessments")
        
        # Initialize retriever
        retriever = RAGRetriever(embeddings, faiss_manager, top_k=5)
        logger.info("RAG retriever initialized")
        
        # Initialize LLM service
        llm = LLMService()
        logger.info("LLM service initialized")
        
        # Initialize agent
        agent = ConversationalAgent(retriever, llm)
        app_state["agent"] = agent
        app_state["ready"] = True
        
        logger.info("✓ SHL Assessment Recommender ready")
    
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        app_state["ready"] = False
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down SHL Assessment Recommender")


# Create FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender",
    description="AI-powered conversational system for discovering SHL assessments",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if not app_state["ready"]:
        raise HTTPException(status_code=503, detail="Service not ready")
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational chat endpoint.
    
    Accepts multi-turn conversation history and returns:
    - Natural language reply
    - Assessment recommendations (if applicable)
    - End-of-conversation flag
    """
    if not app_state["ready"]:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        agent = app_state["agent"]
        
        # Process messages through agent
        response = agent.process_message(request.messages)
        
        # Validate response schema
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Chat processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing request"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "SHL Assessment Recommender",
        "version": "1.0.0",
        "status": "ready" if app_state["ready"] else "initializing",
        "endpoints": {
            "health": "/health",
            "chat": "/chat"
        }
    }


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
