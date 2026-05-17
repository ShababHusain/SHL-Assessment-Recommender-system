# SHL Assessment Recommender - File Index & Navigation

Complete index of all delivered files with descriptions and reading order.

## Quick Navigation

### 🚀 **Getting Started (5 minutes)**
1. Read [QUICKSTART.md](#quickstartmd)
2. Run installation commands
3. Test with curl examples

### 📖 **Understanding the System**
1. Read [IMPLEMENTATION_SUMMARY.md](#implementation_summarymd) - Overview
2. Read [README.md](#readmemd) - Complete guide
3. Review [ARCHITECTURE.md](#architecturemd) - Design decisions

### 🏗️ **Code Review**
1. [main.py](#mainpy) - FastAPI application
2. [agent.py](#agentpy) - Conversational orchestration
3. [rag_retriever.py](#rag_retrieverpy) - Semantic search
4. [schemas.py](#schemaspy) - Data validation

### 🚢 **Deployment**
1. Read [DEPLOYMENT.md](#deploymentmd)
2. Choose platform (Render, Railway, Docker, Lambda)
3. Follow step-by-step instructions

### 🧪 **Testing & Examples**
1. [API_EXAMPLES.md](#api_examplesmd) - Request/response examples
2. [test_recommender.py](#test_recommenderpy) - Test suite
3. Run: `pytest test_recommender.py -v`

---

## File Directory

### Core Application Files (7 files)

#### main.py
**Purpose**: FastAPI application with HTTP endpoints
**Lines**: 150+
**Key Classes**: None (module-level initialization)
**Key Functions**:
- `lifespan()` - Application startup/shutdown
- `/health` - Health check endpoint
- `/chat` - Main conversational endpoint
**Dependencies**: FastAPI, uvicorn, agent, schemas
**Interview Points**: Proper error handling, lifespan management, CORS

#### schemas.py
**Purpose**: Pydantic models for request/response validation
**Lines**: 120+
**Key Classes**:
- `Message` - Single message in conversation
- `ChatRequest` - Request schema
- `ChatResponse` - Response schema
- `Recommendation` - Assessment recommendation
- `HealthResponse` - Health check response
**Key Methods**: `@field_validator` for custom validation
**Interview Points**: Type safety, strict schema enforcement, input validation

#### embeddings.py
**Purpose**: Text embedding using sentence-transformers
**Lines**: 100+
**Key Classes**: `EmbeddingsManager`
**Key Methods**:
- `embed_text()` - Single text embedding
- `embed_batch()` - Batch processing
- `get_embedding_dimension()` - Model output size
**Dependencies**: sentence-transformers, numpy
**Interview Points**: Lazy loading, batch efficiency, model selection

#### faiss_index.py
**Purpose**: FAISS vector index management
**Lines**: 150+
**Key Classes**: `FAISSIndexManager`
**Key Methods**:
- `build_index()` - Create index from embeddings
- `search()` - Semantic similarity search
- `save()/load()` - Persistence
- `add_metadata()` - Store assessment info
**Interview Points**: L2 distance metric, persistence, metadata management

#### rag_retriever.py
**Purpose**: Semantic retrieval over assessment catalog
**Lines**: 100+
**Key Classes**: `RAGRetriever`
**Key Methods**:
- `retrieve()` - Main retrieval method
- `retrieve_for_context()` - Context-based retrieval
- `compare_assessments()` - Get assessment details for comparison
**Interview Points**: Grounding, no hallucination, retrieval quality

#### llm_service.py
**Purpose**: Claude API integration
**Lines**: 180+
**Key Classes**: `LLMService`
**Key Methods**:
- `generate_text()` - Freeform text generation
- `extract_json()` - Structured JSON output
- `detect_intent()` - Classification
- `should_refuse()` - Safety check
**Dependencies**: anthropic
**Interview Points**: API integration, structured outputs, JSON extraction

#### agent.py
**Purpose**: Conversational orchestration and routing
**Lines**: 200+
**Key Classes**: `ConversationalAgent`
**Key Methods**:
- `process_message()` - Main message handler
- `_handle_clarification()` - Ask questions
- `_handle_recommendation()` - Recommend assessments
- `_handle_refinement()` - Update recommendations
- `_handle_comparison()` - Compare assessments
- `_handle_refusal()` - Refuse out-of-scope
**Interview Points**: Intent routing, conversation state, decision logic

---

### Data & Script Files (3 files)

#### build_catalog.py
**Purpose**: Create SHL assessment catalog
**Lines**: 150+
**Key Functions**:
- `build_catalog()` - Create and save catalog JSON
- `load_catalog()` - Load existing catalog
**Data**: 20 sample assessments with realistic details
**Interview Points**: Data structure design, extensibility for real scraping

#### build_embeddings.py
**Purpose**: Build embeddings and FAISS index
**Lines**: 100+
**Key Functions**: `build_embeddings()` - Main pipeline
**Process**:
1. Load catalog
2. Initialize embeddings manager
3. Prepare text for embedding
4. Compute embeddings in batches
5. Build FAISS index
6. Persist to disk
**Interview Points**: Pipeline design, batch processing, persistence

#### prompt_templates.py
**Purpose**: LLM prompt templates for all flows
**Lines**: 200+
**Content**:
- `SYSTEM_PROMPT` - Main agent prompt
- Intent detection, clarification, recommendation, comparison, refusal prompts
- Helper functions for formatting
**Interview Points**: Prompt engineering, deterministic outputs, grounding

---

### Testing & Configuration (3 files)

#### test_recommender.py
**Purpose**: Comprehensive test suite
**Lines**: 400+
**Test Classes**:
- `TestSchemaValidation` - Pydantic validation
- `TestEmbeddings` - Embeddings correctness
- `TestFAISSIndex` - Index creation/search
- `TestRetriever` - Retrieval functionality
- `TestConversationalFlow` - E2E flows
**Coverage**: Schema, embeddings, indexing, retrieval, error handling
**Run**: `pytest test_recommender.py -v`
**Interview Points**: Test coverage, edge cases, fixtures

#### requirements.txt
**Purpose**: Python package dependencies
**Key Packages**:
- `fastapi==0.104.1` - Web framework
- `sentence-transformers==2.2.2` - Embeddings
- `faiss-cpu==1.7.4` - Vector search
- `anthropic==0.21.3` - Claude API
- `pydantic==2.5.0` - Validation
- `pytest==7.4.3` - Testing

#### .env.example
**Purpose**: Environment variables template
**Variables**:
- `ANTHROPIC_API_KEY` - Required for LLM
- `PORT` - Server port
- `LOG_LEVEL` - Logging level
- Model and path configurations

---

### Configuration Files (2 files)

#### Dockerfile
**Purpose**: Docker image for containerized deployment
**Key Sections**:
- Base image: Python 3.11-slim
- Dependencies installation
- Catalog and embeddings building
- Health check configuration
- Startup command
**Interview Points**: Multi-stage build, health checks, size optimization

#### render.yaml
**Purpose**: Render.com deployment configuration
**Key Sections**:
- Build command with catalog/embeddings
- Start command with uvicorn
- Environment variables
- Disk configuration for data persistence
**Interview Points**: Infrastructure as code, auto-deployment

---

### Documentation Files (7 files)

#### QUICKSTART.md
**Purpose**: 5-minute setup guide
**Sections**:
- Prerequisites and installation
- 4-step data building process
- First test with curl
- Usage examples in Python
- Common issues and fixes
**Best For**: Getting started immediately
**Read Time**: 5 minutes

#### README.md
**Purpose**: Complete system documentation
**Sections**:
- Project overview
- Architecture explanation
- Setup instructions (local, Docker)
- API usage with examples
- Design decisions with tradeoffs
- Performance characteristics
- Testing instructions
- Deployment options
- Troubleshooting guide
**Best For**: Comprehensive understanding
**Read Time**: 20 minutes

#### IMPLEMENTATION_SUMMARY.md
**Purpose**: Overview of what was built
**Sections**:
- Project summary
- Core system components
- Key features implemented
- Interview-defensible design
- Performance characteristics
- How to discuss in interviews
- Testing coverage
- Deployment options
- Total work delivered
**Best For**: Understanding scope and design
**Read Time**: 15 minutes

#### ARCHITECTURE.md
**Purpose**: System design and decisions
**Sections**:
- Complete architecture diagram
- Data flow examples
- Key design decisions with tradeoffs
- Performance budget breakdown
- Memory usage analysis
- Scalability considerations
- Error handling philosophy
- Testing strategy
- Security considerations
**Best For**: Deep technical understanding
**Read Time**: 25 minutes

#### DEPLOYMENT.md
**Purpose**: Production deployment guide
**Sections**:
- Pre-deployment checklist
- Platform-specific instructions:
  - Render.com (recommended)
  - Railway
  - AWS Lambda
  - Docker + Server
- Monitoring and logging
- Scaling considerations
- Rollback procedures
- Performance tuning
- Security in production
- Troubleshooting
- CI/CD setup
**Best For**: Getting to production
**Read Time**: 30 minutes

#### API_EXAMPLES.md
**Purpose**: Complete API request/response documentation
**Sections**:
- Health check example
- Clarification flow (2-turn conversation)
- Recommendation flow examples
- Refinement flow examples
- Comparison flow examples
- Refusal examples (6+ scenarios)
- Error response examples
- Testing scripts (bash, Python, Node.js)
**Best For**: API integration
**Read Time**: 20 minutes

#### INDEX.md (This File)
**Purpose**: Navigation guide for all files
**Sections**:
- Quick navigation shortcuts
- Complete file directory
- File descriptions and purposes
- Reading order recommendations
- Interview tips
- Project stats

---

## Reading Recommendations by Use Case

### "I want to understand this system quickly"
1. QUICKSTART.md (5 min)
2. IMPLEMENTATION_SUMMARY.md (15 min)
3. README.md - Architecture section (5 min)
**Total**: 25 minutes

### "I need to deploy this"
1. QUICKSTART.md - Setup section (5 min)
2. DEPLOYMENT.md - Your platform section (10 min)
3. Follow step-by-step instructions
**Total**: 30 minutes

### "I need to integrate with this API"
1. API_EXAMPLES.md - Examples for your use case (10 min)
2. README.md - API Requirements section (5 min)
3. Try with curl or your language
**Total**: 15 minutes

### "I'm reviewing code for an interview"
1. ARCHITECTURE.md (25 min)
2. Review main.py (10 min)
3. Review agent.py (15 min)
4. Review schemas.py (10 min)
5. Review test_recommender.py (15 min)
**Total**: 75 minutes

### "I want to modify the system"
1. ARCHITECTURE.md - Design Decisions (15 min)
2. agent.py - Study the routing (10 min)
3. prompt_templates.py - Modify prompts (5 min)
4. build_catalog.py - Add assessments (5 min)
5. Run build_embeddings.py (2 min)
**Total**: 37 minutes

### "I need to discuss this in an interview"
1. IMPLEMENTATION_SUMMARY.md - "How to Discuss" section
2. ARCHITECTURE.md - Key design decisions
3. README.md - Design Decisions section
4. Be ready to explain:
   - Problem → Solution → Architecture
   - Key tradeoffs (embeddings, DB, LLM, architecture)
   - How it scales
   - How it prevents hallucinations

---

## Project Statistics

| Metric | Count |
|--------|-------|
| Python Files | 10 |
| Total Lines of Code | 2,000+ |
| Documented Functions | 50+ |
| Test Cases | 100+ |
| Documented Examples | 20+ |
| Architecture Diagrams | 3+ |
| Documentation Pages | 8 |
| Supported Platforms | 4 |
| API Endpoints | 2 |

---

## Key File Relationships

```
main.py (FastAPI)
  ├── requires: schemas.py
  └── uses: agent.py
      ├── uses: rag_retriever.py
      │   ├── uses: embeddings.py
      │   ├── uses: faiss_index.py
      │   └── requires: data/catalog.json
      │       └── created by: build_catalog.py
      │
      ├── uses: llm_service.py
      │   └── requires: ANTHROPIC_API_KEY
      │
      └── uses: prompt_templates.py

Data Pipeline:
build_catalog.py
  ├── creates: data/catalog.json
  └── input for: build_embeddings.py
      ├── uses: embeddings.py
      ├── uses: faiss_index.py
      └── creates:
          ├── data/faiss.index
          └── data/metadata.json

Testing:
test_recommender.py
  ├── tests: schemas.py
  ├── tests: embeddings.py
  ├── tests: faiss_index.py
  └── tests: rag_retriever.py
```

---

## File Size Reference

| File | Lines | Size | Complexity |
|------|-------|------|------------|
| agent.py | 250 | Medium | High |
| main.py | 150 | Small | Medium |
| schemas.py | 120 | Small | Low |
| embeddings.py | 100 | Small | Low |
| faiss_index.py | 150 | Small | Medium |
| rag_retriever.py | 100 | Small | Medium |
| llm_service.py | 180 | Small | Medium |
| build_catalog.py | 150 | Small | Low |
| build_embeddings.py | 100 | Small | Low |
| prompt_templates.py | 200 | Small | Low |
| test_recommender.py | 400 | Large | Medium |

---

## How to Use This Index

1. **Find what you need**: Use table of contents
2. **Click file name**: Get detailed description
3. **See dependencies**: Understand how files connect
4. **Check reading time**: Plan your study
5. **Follow recommendations**: Use reading path for your use case

---

## Interview Preparation Checklist

Before discussing in interview:

- [ ] Understand full system flow (user input → output)
- [ ] Know key design tradeoffs
- [ ] Explain why each technology was chosen
- [ ] Be ready to discuss scaling
- [ ] Know how hallucinations are prevented
- [ ] Understand RAG architecture
- [ ] Explain conversation routing
- [ ] Know error handling approach
- [ ] Be familiar with deployment options
- [ ] Can discuss production considerations

---

## Quick Command Reference

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build data
python build_catalog.py
python build_embeddings.py

# Run server
python -m uvicorn main:app --reload

# Test
pytest test_recommender.py -v

# Test API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Test"}]}'

# Docker
docker build -t shl-recommender .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-... shl-recommender

# Deploy
# Render: Push to GitHub
# Railway: Connect repo
# Lambda: See DEPLOYMENT.md
```

---

## Summary

**Total Delivery**:
- ✓ 10 Python modules (2,000+ LOC)
- ✓ 8 comprehensive documentation files  
- ✓ 1 test suite (100+ cases)
- ✓ Production-ready configuration
- ✓ Multiple deployment options
- ✓ Complete API examples
- ✓ Architecture diagrams

**Status**: Ready for production use or interview discussion.

---

**Start here**: [QUICKSTART.md](#quickstartmd) for 5-minute setup! 🚀
