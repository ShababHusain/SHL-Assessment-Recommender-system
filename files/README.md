# SHL Assessment Recommender

Production-quality AI-powered conversational system for discovering relevant SHL assessments.

## Overview

The SHL Assessment Recommender is a RAG-based conversational agent that helps recruiters find the right assessment tools through natural dialogue. It:

- **Asks clarifying questions** when context is unclear
- **Recommends relevant assessments** based on hiring needs
- **Refines recommendations** dynamically as requirements change
- **Compares assessments** using grounded catalog data
- **Refuses out-of-scope requests** with clear explanations
- **Stays grounded** in SHL catalog data (no hallucinations)

## Architecture

### System Design

```
User Query
    ↓
FastAPI Router (/chat)
    ↓
Conversational Agent
    ├─ Intent Detection (Claude)
    ├─ Conversation Analysis (Claude)
    └─ Decision Logic (rule-based)
    ↓
    ├─→ Clarification Path: Generate clarifying question
    ├─→ Recommendation Path: Retrieve + Generate response
    ├─→ Refinement Path: Re-retrieve with updated query
    ├─→ Comparison Path: Retrieve and compare assessments
    └─→ Refusal Path: Explain why request is out-of-scope
    ↓
Structured API Response
```

### Components

#### 1. **Embeddings Pipeline** (`embeddings.py`)
- Uses `sentence-transformers` (all-MiniLM-L6-v2)
- Lightweight (~22MB), fast, and effective for semantic search
- Lazy-loads model on first use
- Batch processing for efficiency

#### 2. **FAISS Indexing** (`faiss_index.py`)
- L2 (Euclidean) distance metric for similarity
- Persistent on-disk storage (index + metadata)
- Efficient O(log n) similarity search
- Metadata tied to index positions

#### 3. **RAG Retriever** (`rag_retriever.py`)
- Combines embeddings + FAISS indexing
- Returns grounded recommendations from catalog
- Supports context-based filtering
- Capped at 10 results per PRD

#### 4. **LLM Service** (`llm_service.py`)
- Uses Anthropic Claude API
- Structured JSON extraction for intent detection
- Grounded text generation (no free-form hallucination)
- Refusal detection for out-of-scope requests

#### 5. **Conversational Agent** (`agent.py`)
- Multi-turn conversation orchestration
- Intent-driven routing logic
- Clarification, recommendation, refinement, comparison, refusal flows
- Deterministic behavior

#### 6. **FastAPI Application** (`main.py`)
- RESTful endpoints: `/health` and `/chat`
- CORS support
- Proper error handling and validation
- Lifespan management for startup/shutdown

### Data Flow

1. **Startup**: Load embeddings, FAISS index, LLM service
2. **Inference**: 
   - User sends message
   - Detect intent from conversation history
   - Route to appropriate handler
   - Retrieve relevant assessments (if needed)
   - Generate response using LLM
   - Return structured response

## Setup & Installation

### Prerequisites

- Python 3.11+
- 2GB+ available disk space (for embeddings model)
- Anthropic API key (free credits available)

### Local Development

```bash
# Clone repository
git clone <repo>
cd shl-assessment-recommender

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Build catalog (creates sample data)
python build_catalog.py

# Build embeddings and FAISS indices
python build_embeddings.py

# Start server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### Docker Setup

```bash
# Build image
docker build -t shl-recommender .

# Run container
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_api_key \
  shl-recommender
```

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok"
}
```

### Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "I need to hire a Java developer"
      }
    ]
  }'
```

### Response Format

```json
{
  "reply": "What specific skills are you looking to assess? For example, core Java, system design, or concurrency?",
  "recommendations": [],
  "end_of_conversation": false
}
```

Or with recommendations:

```json
{
  "reply": "Based on your needs for a Java backend engineer, here are the most relevant assessments...",
  "recommendations": [
    {
      "name": "Java Programming",
      "url": "https://www.shl.com/en/solutions/assessments/java-programming/",
      "test_type": "Technical Skills"
    },
    {
      "name": "Verify G+ Interactive",
      "url": "https://www.shl.com/en/solutions/assessments/verify-interactive/",
      "test_type": "Cognitive Ability"
    }
  ],
  "end_of_conversation": false
}
```

### Example Conversation Flow

**Turn 1 - Vague Request:**
```json
User: "I need an assessment"

Response: "What role are you hiring for?"
(recommendations: [])
```

**Turn 2 - Providing Context:**
```json
User: "Java developer for our backend team"

Response: "Great! Are you primarily assessing technical skills (Java knowledge), 
cognitive ability for problem-solving, or personality/cultural fit?"
(recommendations: [])
```

**Turn 3 - Clarified Requirements:**
```json
User: "Technical Java skills mainly"

Response: "Here are the most relevant Java assessments for your backend roles..."
(recommendations: [Java Programming, Verify G+])
```

**Turn 4 - Refinement:**
```json
User: "Can you add personality tests too?"

Response: "I've updated the recommendations to include personality assessments..."
(recommendations: [Java Programming, Verify G+, OPQ32r+])
```

## Design Decisions

### 1. **Embeddings Model Choice**
- **Chose**: `all-MiniLM-L6-v2`
- **Why**: 
  - Lightweight (~22MB) vs large models (1GB+)
  - Fast inference (10-50ms per embedding)
  - Strong performance on semantic similarity
  - Trade-off: Slightly less nuanced than large models (acceptable for this domain)

### 2. **FAISS Over VectorDB**
- **Chose**: FAISS with on-disk persistence
- **Why**:
  - No external database dependency
  - Simple to manage and version
  - Sufficient for 1000s of assessments
  - Trade-off: Not ideal for millions of vectors

### 3. **Claude API Over Open Source LLM**
- **Chose**: Anthropic Claude (Opus model)
- **Why**:
  - Superior instruction following
  - Excellent for structured JSON extraction
  - Strong refusal capabilities
  - Fast inference
  - Trade-off: Requires API key and internet connection

### 4. **Stateless API Design**
- **Why**:
  - Horizontally scalable
  - No session management complexity
  - Conversation history is stateless (client tracks it)
  - Easier to deploy and test

### 5. **Intent Detection via LLM**
- **Chose**: Claude for intent detection
- **Why**:
  - More flexible than rule-based
  - Handles nuanced language
  - Easy to extend with new intents
  - Trade-off: Adds API call overhead (mitigated by caching)

## Conversational Behaviors

### Clarification
Triggered when intent is unclear or insufficient context exists.

```python
Conditions:
- Role not mentioned
- Assessment goals ambiguous
- Multiple interpretations possible

Response:
- Single focused question
- No recommendations yet
```

### Recommendation
Triggered when enough context exists.

```python
Conditions:
- Clear role + skills/goals identified
- Sufficient hiring context available

Response:
- 1-10 relevant assessments
- Brief explanation of matches
- Ready for refinement or comparison
```

### Refinement
Triggered when user updates requirements.

```python
Conditions:
- Previous recommendations exist
- User modifies criteria ("Add personality", "Also need...")

Response:
- Updated recommendations
- Acknowledgment of changes
```

### Comparison
Triggered when user asks to compare assessments.

```python
Conditions:
- User mentions two assessment names
- Explicit "compare" or "difference" language

Response:
- 2-3 sentence comparison
- Grounded in catalog data only
```

### Refusal
Triggered when request is out-of-scope.

```python
Conditions:
- Non-SHL assessment requested
- Legal/compliance advice requested
- Unrelated domain
- Prompt injection attempt

Response:
- Clear refusal with reason
- Redirection to SHL topics
```

## Performance Characteristics

| Operation | Duration | Notes |
|-----------|----------|-------|
| Embeddings | 10-50ms | Per text string |
| FAISS Search | 5-20ms | Top-k retrieval |
| Intent Detection | 200-500ms | Claude API call |
| Full Response | <2s | End-to-end (typical) |
| **Target SLA** | **<30s** | Per PRD |

## Testing

### Unit Tests
```bash
pytest test_recommender.py -v
```

Tests cover:
- Schema validation (Pydantic models)
- Embeddings generation
- FAISS indexing and search
- Retriever functionality
- Intent detection
- Conversation flows

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test clarification flow
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Need help with hiring"}]}'

# Test recommendation flow
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hiring a Java developer"},
      {"role": "assistant", "content": "What specific aspects..."},
      {"role": "user", "content": "Core Java and system design"}
    ]
  }'
```

## Deployment

### Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...
PORT=8000
LOG_LEVEL=info
```

### Render.com

1. **Create app.yaml**:
```yaml
services:
  - type: web
    name: shl-recommender
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ANTHROPIC_API_KEY
        scope: run
        value: ${ANTHROPIC_API_KEY}
```

2. **Deploy**:
```bash
render deploy
```

### Railway

1. **Connect GitHub repo**
2. **Set environment variables** in Railway dashboard
3. **Railway auto-detects** Python and installs requirements
4. **Auto-starts** with `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### AWS Lambda (with API Gateway)

```bash
# Build deployment package
pip install -r requirements.txt -t package/
cp -r app data *.py package/

# Create Lambda function from zip
cd package && zip -r ../lambda.zip . && cd ..
aws lambda create-function \
  --function-name shl-recommender \
  --zip-file fileb://lambda.zip \
  --handler main.handler \
  --runtime python3.11 \
  --environment Variables={ANTHROPIC_API_KEY=...}
```

## Evaluation Metrics

### Schema Correctness
- All responses match ChatResponse schema
- No missing required fields
- Recommendations always have name, url, test_type
- All URLs are real catalog URLs

### Retrieval Quality
- Recall@10 > 0.8 (top 10 results contain relevant assessments)
- Precision > 0.7 (most results are relevant)
- No hallucinated assessments

### Conversation Quality
- Clarification appropriate for ambiguous queries
- Recommendations match context
- Refinements incorporate user feedback
- Comparisons are accurate and grounded

### Hallucination Rate
- **Target**: 0% hallucinated assessments
- **Monitoring**: Every recommendation checked against catalog

## Troubleshooting

### "Index files not found"
```bash
# Run embedding pipeline
python build_embeddings.py
```

### "ANTHROPIC_API_KEY not found"
```bash
# Set environment variable
export ANTHROPIC_API_KEY=your_key_here

# Or create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### Slow responses
- Embeddings model lazy-loads on first request (takes 5-10s)
- FAISS search should be <20ms
- Claude API calls take 200-800ms
- Check network connectivity

### Memory issues
- Embeddings model: ~500MB in memory
- FAISS index: ~50MB for 1000 assessments
- Minimum 2GB RAM recommended

## Future Enhancements

1. **Feedback Loop**: Store successful assessments to improve ranking
2. **Multi-language**: Support questions in multiple languages
3. **Assessment Bundling**: Recommend assessment combinations
4. **Analytics**: Track most-requested assessments and roles
5. **Fine-tuning**: Custom embeddings model for SHL domain
6. **Caching**: Redis for frequently asked comparisons

## Code Quality

### Principles
- **Clean Architecture**: Separation of concerns (routes → agent → services)
- **Type Safety**: Full Pydantic validation
- **Error Handling**: Comprehensive try-catch with logging
- **Testability**: Dependency injection, mocked components
- **Documentation**: Docstrings on all public functions
- **Logging**: Structured logging at appropriate levels

### Linting & Formatting
```bash
pip install black flake8 mypy
black . --line-length 100
flake8 . --max-line-length 100
mypy . --ignore-missing-imports
```

## Security Considerations

1. **Prompt Injection**: Detected via refusal mechanism
2. **URL Validation**: All URLs must start with http/https
3. **Input Validation**: Pydantic models enforce constraints
4. **Rate Limiting**: Implement via API gateway (Render/Railway)
5. **CORS**: Restricted to necessary origins only

## License

[Specify License]

## Support

For issues or questions:
1. Check troubleshooting section
2. Review example API requests
3. Check logs: `docker logs <container_id>`
4. Open issue with reproduction steps

---

Built with production-grade architecture, tested, and ready for interview defense.
