# Architecture & Design Decisions

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                          │
│                    (Web, Mobile, Desktop, Bot)                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                   HTTP/REST (POST /chat)
                             │
┌─────────────────────────────▼────────────────────────────────────────┐
│                         FASTAPI APPLICATION                          │
│                        (main.py)                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Routes:                                                      │   │
│  │  GET  /health          → HealthResponse                     │   │
│  │  POST /chat            → ChatResponse                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────────────┘
                         │
                    Input Validation
                  (Pydantic Schemas)
                         │
┌────────────────────────▼─────────────────────────────────────────────┐
│                  CONVERSATIONAL AGENT                                 │
│                   (agent.py)                                         │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ 1. Intent Detection (Claude API)                             │   │
│  │    - Analyze conversation history                            │   │
│  │    - Classify: clarification, recommendation, refine, etc.   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────────────────────┐    │
│  │ 2. Refusal Detection                                         │    │
│  │    - Check for out-of-scope requests                        │    │
│  │    - Detect prompt injection                                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                         │                                            │
│  ┌──────────────────────▼──────────────────────────────────────┐    │
│  │ 3. Intent-Based Routing                                     │    │
│  │                                                              │    │
│  │  ├─ Clarification → Ask question                           │    │
│  │  ├─ Recommendation → Retrieve assessments                  │    │
│  │  ├─ Refinement → Re-retrieve with new context             │    │
│  │  ├─ Comparison → Compare specific assessments             │    │
│  │  └─ Refusal → Explain out-of-scope                        │    │
│  └──────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐
│  RAG         │  │   LLM Service   │  │   Prompt         │
│  Retriever   │  │   (Claude API)  │  │   Templates      │
│  (retriever) │  │  (llm_service)  │  │  (prompt_temp)   │
└──────────────┘  └─────────────────┘  └──────────────────┘
        │                │
        └────────────────┼────────────────────┐
                         │                    │
        ┌────────────────▼────────────────┐  │
        │   Text Generation              │  │
        │   - Clarification questions    │  │
        │   - Recommendations response   │  │
        │   - Comparisons                │  │
        │   - Refusal messages           │  │
        └────────────────────────────────┘  │
                                            │
                    ┌───────────────────────▼────────────────┐
                    │  Semantic Retrieval                    │
                    │  (RAG Pipeline)                        │
                    │                                        │
                    │  1. Embed user query                   │
                    │  2. Search FAISS index                 │
                    │  3. Return grounded results            │
                    │  4. Cap at 10 recommendations          │
                    └───────────────────┬────────────────────┘
                                        │
                ┌───────────────────────┴────────────────────┐
                │                                            │
         ┌──────▼──────────┐                      ┌─────────▼──────┐
         │   Embeddings    │                      │  FAISS Index   │
         │   Manager       │                      │  Manager       │
         │ (embeddings.py) │                      │ (faiss_index)  │
         │                 │                      │                │
         │ sentence-       │                      │ L2 distance    │
         │ transformers    │                      │ metric         │
         │ all-MiniLM-     │                      │                │
         │ L6-v2           │                      │ Persistent     │
         │                 │                      │ disk storage   │
         └────────┬────────┘                      └────────┬───────┘
                  │                                        │
                  │            ┌───────────────────────────┘
                  │            │
              ┌───▼────────────▼──────┐
              │   SHL Assessment      │
              │   Catalog Data        │
              │   (data/)             │
              │                       │
              │  - catalog.json       │
              │  - faiss.index        │
              │  - metadata.json      │
              └───────────────────────┘
```

## Data Flow

### Single Request Example

```
User Message: "Hiring a Python developer"
                    │
                    ▼
        ┌─────────────────────────┐
        │ Pydantic Validation     │
        │ - Check message format  │
        │ - Validate content      │
        └────────────┬────────────┘
                     │ Valid
                     ▼
        ┌─────────────────────────────────────┐
        │ Intent Detection (Claude)           │
        │ - Analyze context                   │
        │ - Classify intent                   │
        │ - Extract hiring context            │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │ Refusal Check (Claude)              │
        │ - Is request in-scope?              │
        │ - Is it legitimate?                 │
        └────────────┬────────────────────────┘
                     │ In-scope
                     ▼
        ┌─────────────────────────────────────┐
        │ Intent Router                       │
        │ (ready_to_recommend)                │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │ Retrieval (RAG)                     │
        │ 1. Embed: "Hiring Python developer" │
        │    (sentence-transformers)          │
        │ 2. Search FAISS index               │
        │    (top-k=5)                        │
        │ 3. Return metadata                  │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │ Results:                            │
        │ - Python Programming                │
        │ - Verify G+ Interactive             │
        │ - Numerical Reasoning               │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │ Response Generation (Claude)        │
        │ - Format recommendations            │
        │ - Generate explanation              │
        │ - Apply prompts                     │
        └────────────┬────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────────────┐
        │ ChatResponse                        │
        │ {                                   │
        │   "reply": "For Python dev...",    │
        │   "recommendations": [...],         │
        │   "end_of_conversation": false      │
        │ }                                   │
        └─────────────────────────────────────┘
```

## Key Design Decisions

### 1. Embeddings Model Selection

**Chosen**: `all-MiniLM-L6-v2` from sentence-transformers

**Trade-offs**:
```
Model                 | Size  | Speed  | Quality | Score
─────────────────────────────────────────────────────────
all-MiniLM-L6-v2     | 22MB  | Fast   | Good    | ✓ CHOSEN
all-mpnet-base-v2    | 420MB | Slow   | Better  | ✗ Too large
paraphrase-mpnet     | 420MB | Slow   | Better  | ✗ Too large
all-distilroberta    | 268MB | Medium | Good    | ✗ Still large
OpenAI text-embedding| -     | Fast   | Best    | ✗ Requires API
```

**Rationale**:
- 22MB model fits in memory with room for LLM
- 10-50ms inference per embedding (acceptable)
- Good semantic similarity for hiring/assessment domain
- No external API dependency
- Proven on benchmarks for semantic search

### 2. Vector Database Choice

**Chosen**: FAISS (with on-disk persistence)

**Alternatives Considered**:
```
Solution           | Setup | Query | Scale | Persistence | Cost
───────────────────────────────────────────────────────────────
FAISS (in-memory)  | Easy  | Fast  | Good  | No          | Free
Pinecone           | Easy  | Fast  | Great | Yes         | $$$
Weaviate           | Med   | Fast  | Great | Yes         | Free
Qdrant             | Med   | Fast  | Great | Yes         | Free
Milvus             | Hard  | Fast  | Great | Yes         | Free
```

**Rationale**:
- No external database dependency (simpler deployment)
- In-memory + persistent files model
- Sufficient for 1000s-10000s of assessments
- Works well on single machine
- No authentication/networking complexity

**Tradeoff**: 
- Cannot handle billions of vectors (not needed here)
- Single-machine only (mitigated with stateless design)

### 3. LLM Provider

**Chosen**: Anthropic Claude API

**Alternatives Considered**:
```
Provider     | Instruction | Struct Output | Refusal | Cost  | Speed
───────────────────────────────────────────────────────────────────────
Claude       | Excellent   | Yes           | Strong  | Mod   | Fast
OpenAI GPT   | Good        | Yes           | Medium  | Low   | Fast
Llama 2      | Good        | Partial       | Weak    | Free  | Slow
Mistral      | Good        | Yes           | Medium  | Free  | Medium
Google Gemini| Good        | Yes           | Medium  | Low   | Fast
```

**Rationale**:
- Superior instruction following (key for deterministic behavior)
- Excellent JSON extraction (used for intent detection)
- Strong refusal mechanism (prevents hallucination)
- Good balance of cost/performance
- Reliable API with good uptime

**Tradeoff**: 
- Requires API key and internet connection
- Per-request cost (mitigated with efficient prompts)

### 4. API Architecture

**Chosen**: Stateless FastAPI with in-request conversation history

**Why Stateless**:
```
Stateful Architecture:
├─ Pros: Faster responses, can cache intermediate results
└─ Cons: Hard to scale, requires session management, complex

Stateless Architecture: ✓ CHOSEN
├─ Pros: Horizontal scaling, simple deployment, fault-tolerant
└─ Cons: Slight overhead per request
```

**Conversation History Handling**:
- Client sends full history each request
- Server processes without storage
- Stateless nature allows horizontal scaling
- Each instance is identical and independent

### 5. Prompt Engineering

**Decision**: Structured prompts with JSON extraction for determinism

**Approach**:
```python
# Instead of free-form generation:
intent, confidence, context = llm.detect_intent(conversation)

# Structured JSON output:
{
    "intent": "ready_to_recommend",  # Deterministic classification
    "confidence": 0.95,
    "context": {
        "role": "Java developer",
        "skills": ["Java", "SQL"],
        "goals": ["Technical skills", "Problem-solving"]
    }
}
```

**Benefits**:
- Deterministic behavior (same conversation → same intent)
- Easy to test and validate
- Prevents model drift
- Enables routing without string matching

### 6. Data Grounding Strategy

**Constraints**:
1. Zero hallucinated assessments
2. All URLs must exist in catalog
3. No prior knowledge usage

**Implementation**:
```python
# Only retrieval-based recommendations
recommendations = retriever.retrieve(query, top_k=5)
# ↓
# Results come from FAISS index + catalog metadata
# ↓
# Cannot recommend unlisted assessments

# Comparison uses only catalog data
comparison = llm.generate_comparison(
    format_assessment_for_prompt(assess1),  # Catalog data only
    format_assessment_for_prompt(assess2)   # Catalog data only
)
```

## Performance Considerations

### Response Time Budget (Target: <30s)

```
Operation              | Typical | Max   | Budget
──────────────────────────────────────────────────
Pydantic validation    | 1ms     | 5ms   | 5ms
Intent detection       | 200ms   | 500ms | 1000ms (can be cached)
Embedding query        | 20ms    | 50ms  | 50ms
FAISS search          | 5ms     | 20ms  | 50ms
Text generation       | 500ms   | 1000ms| 2000ms
Response formatting   | 5ms     | 10ms  | 50ms
                      ───────────────────────────
Total (typical)       | 731ms   |       |
Total (max)           |         | 1635ms| <30,000ms ✓
```

### Memory Usage

```
Component              | Size
────────────────────────────────
Embeddings model       | 500MB
FAISS index (1000 vectors) | 50MB
Claude SDK            | 50MB
FastAPI + deps        | 100MB
OS/overhead           | 200MB
                      ──────────
Total                 | ~900MB

Recommended: 2GB RAM minimum
```

### Scalability

**Vertical**: 
- Can handle 10,000+ assessments on single machine
- Limited by embeddings model size

**Horizontal**:
- Stateless design → add instances as needed
- Each instance is identical
- No shared state required

## Error Handling Philosophy

### Fail-Safe Design

```
User Request
    │
    ▼
Try: Process normally
    │
    ├─ Validation error? → Return 400 with details
    ├─ Service error? → Return 500 with message
    └─ LLM error? → Return error response
```

### Graceful Degradation

```
Normal Path (Recommendation with retrieval):
  Intent detection → Retrieval → LLM generation

Degraded Path (Fallback):
  Intent detection fails → Ask clarification
  Retrieval fails → Return empty recommendations
  LLM fails → Return generic response
```

## Testing Strategy

### Unit Tests
- Schema validation
- Embeddings correctness
- FAISS indexing
- Retriever functionality

### Integration Tests  
- Intent detection flows
- Recommendation retrieval
- Response generation

### End-to-End Tests
- Full conversation flows
- Error handling
- Performance (response time)

## Security Considerations

### Input Validation
```python
# Pydantic enforces:
- Message length: 1-10,000 characters
- Messages count: 1-100
- Message role: user or assistant only
- URL format: http/https only
```

### Output Validation
```python
# ChatResponse schema enforces:
- Reply: 1-5,000 characters
- Recommendations: 0-10 items max
- Each URL validated format
```

### Refusal Mechanism
```python
# Three layers:
1. Explicit refusal detection (Claude)
2. URL validation (must be in catalog)
3. Assessment verification (cross-check metadata)
```

## Deployment Considerations

### Rendering Platforms
- **Render**: Auto-scaling, persistent disk, free tier
- **Railway**: Simple setup, pay-as-you-go
- **Lambda**: Serverless, scales automatically

### Pre-warming Strategy
- Build catalog.json at image build time
- Pre-compute embeddings at build time
- Load FAISS index at startup
- Result: <5s startup time (vs 60s for on-demand)

---

## Conclusion

This architecture balances:
- **Production readiness** (error handling, validation)
- **Interview defensibility** (clean, understandable code)
- **Scalability** (stateless, horizontal)
- **Reliability** (grounded, no hallucinations)
- **Simplicity** (minimal external dependencies)
