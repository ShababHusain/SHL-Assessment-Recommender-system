# Quick Start Guide

Get the SHL Assessment Recommender running in 5 minutes.

## Prerequisites

- Python 3.11+
- pip/venv
- Anthropic API key (free at https://console.anthropic.com)
- ~2GB disk space

## Installation (5 minutes)

### 1. Clone & Setup

```bash
# Create project directory
mkdir shl-recommender && cd shl-recommender

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all files from outputs directory
# (Copy all .py files and requirements.txt from outputs/)
pip install -r requirements.txt
```

### 2. Get API Key

```bash
# Get free API key
# Go to https://console.anthropic.com/keys
# Copy your API key

# Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-your-key-here
PORT=8000
EOF
```

### 3. Build Data

```bash
# Create catalog (sample SHL data)
python build_catalog.py

# Build embeddings and FAISS index
# (First run takes 2-3 minutes as it downloads embeddings model)
python build_embeddings.py
```

### 4. Start Server

```bash
# Start FastAPI server
python -m uvicorn main:app --reload

# Should see:
# INFO: Uvicorn running on http://0.0.0.0:8000
# INFO: Press CTRL+C to quit
```

## First Test (1 minute)

In a new terminal:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"ok"}

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "I need a Java skills assessment"}]}'

# Should return recommendations!
```

## Usage Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000"

# Simple request
response = requests.post(f"{BASE_URL}/chat", json={
    "messages": [
        {"role": "user", "content": "Hiring Python developers"}
    ]
})

result = response.json()
print(result["reply"])
for rec in result["recommendations"]:
    print(f"- {rec['name']}: {rec['url']}")
```

### Multi-Turn Conversation

```python
# Start conversation
messages = []

# Turn 1
messages.append({"role": "user", "content": "Need an assessment"})
resp1 = requests.post(f"{BASE_URL}/chat", json={"messages": messages}).json()
messages.append({"role": "assistant", "content": resp1["reply"]})
print(f"Agent: {resp1['reply']}")

# Turn 2  
messages.append({"role": "user", "content": "Java developer for backend"})
resp2 = requests.post(f"{BASE_URL}/chat", json={"messages": messages}).json()
messages.append({"role": "assistant", "content": resp2["reply"]})
print(f"Agent: {resp2['reply']}")
for rec in resp2["recommendations"]:
    print(f"  - {rec['name']}")

# Turn 3
messages.append({"role": "user", "content": "Also add personality tests"})
resp3 = requests.post(f"{BASE_URL}/chat", json={"messages": messages}).json()
print(f"Agent: {resp3['reply']}")
for rec in resp3["recommendations"]:
    print(f"  - {rec['name']}")
```

## Project Structure

```
shl-recommender/
├── main.py                 # FastAPI app
├── schemas.py              # Pydantic models
├── embeddings.py           # Embeddings manager
├── faiss_index.py          # FAISS index manager
├── rag_retriever.py        # RAG retriever
├── llm_service.py          # Claude API service
├── agent.py                # Conversational agent
├── prompt_templates.py     # LLM prompts
│
├── build_catalog.py        # Build assessment catalog
├── build_embeddings.py     # Build embeddings & indices
│
├── data/
│   ├── catalog.json        # SHL assessments
│   ├── faiss.index         # Embeddings index
│   └── metadata.json       # Assessment metadata
│
├── tests/
│   └── test_recommender.py # Test suite
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables
├── Dockerfile              # Docker image
│
├── README.md               # Main documentation
├── ARCHITECTURE.md         # Design & architecture
├── DEPLOYMENT.md           # Deployment guide
└── API_EXAMPLES.md         # API request examples
```

## Common Issues & Fixes

### Issue: "ModuleNotFoundError: anthropic"
```bash
# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"
```bash
# Check .env file exists and has correct key
cat .env

# Or set environment variable
export ANTHROPIC_API_KEY=sk-your-key
```

### Issue: "Index files not found"
```bash
# Run embedding pipeline
python build_catalog.py
python build_embeddings.py
```

### Issue: "Connection refused" on localhost:8000
```bash
# Make sure server is running
# In new terminal, check server is started:
curl http://localhost:8000/health
```

### Issue: Slow first request
```bash
# First request downloads embeddings model (~400MB)
# This takes 30-60 seconds
# Subsequent requests are fast (<1 second)
```

## Next Steps

### Understand the System
1. Read [README.md](README.md) for overview
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design
3. Check [API_EXAMPLES.md](API_EXAMPLES.md) for usage

### Test the System  
```bash
# Run tests
pytest test_recommender.py -v

# Manual API testing
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hiring a data scientist"}]}'
```

### Customize
- Add more assessments to `data/catalog.json`
- Rebuild embeddings: `python build_embeddings.py`
- Modify prompts in `prompt_templates.py`

### Deploy
Follow [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Render.com (easiest)
- Railway
- AWS Lambda
- Docker

## API Quick Reference

### GET /health
Check if service is running.

```bash
curl http://localhost:8000/health
```

### POST /chat
Main endpoint for recommendations.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Your question here"
      }
    ]
  }'
```

**Response Schema**:
```json
{
  "reply": "Natural language response",
  "recommendations": [
    {
      "name": "Assessment Name",
      "url": "https://example.com",
      "test_type": "Assessment Type"
    }
  ],
  "end_of_conversation": false
}
```

## Example Conversation

```
User: "I'm hiring"
Agent: "What role are you hiring for?"

User: "Java backend engineer"
Agent: "Great! Here are assessments..."
Recommendations: [Java Programming, Verify G+, ...]

User: "Also add personality tests"  
Agent: "Updated recommendations..."
Recommendations: [Java Programming, Verify G+, OPQ32r+]

User: "Compare OPQ32i vs OPQ32r+"
Agent: "OPQ32r+ is the newer version with..."
Recommendations: []
```

## Troubleshooting Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] requirements.txt installed
- [ ] .env file has ANTHROPIC_API_KEY
- [ ] catalog.json exists in data/
- [ ] faiss.index exists in data/
- [ ] Server starts without errors
- [ ] Health endpoint returns {"status": "ok"}
- [ ] Chat endpoint returns valid response

## Performance Tips

1. **Pre-warm the model**: First request is slower (model loading)
2. **Batch requests**: Process multiple queries to amortize overhead
3. **Monitor memory**: System uses ~900MB RAM
4. **Check API quota**: Anthropic API calls cost tokens

## File Dependencies

```
main.py
├── schemas.py
├── agent.py
│   ├── rag_retriever.py
│   │   ├── embeddings.py
│   │   ├── faiss_index.py
│   │   └── data/catalog.json
│   ├── llm_service.py
│   └── prompt_templates.py
└── data/
    ├── catalog.json (created by build_catalog.py)
    ├── faiss.index (created by build_embeddings.py)
    └── metadata.json (created by build_embeddings.py)
```

All files must be in correct locations for system to work.

## Getting Help

1. **Check logs**: Look at terminal output for error messages
2. **Read docs**:
   - README.md - Overview
   - ARCHITECTURE.md - System design
   - API_EXAMPLES.md - API usage
   - DEPLOYMENT.md - Production setup
3. **Review code**: All code is well-documented with docstrings
4. **Test individually**: Test each component (embeddings, retriever, etc.)

## Next: Production Deployment

When ready to deploy:

```bash
# Docker deployment
docker build -t shl-recommender .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-... shl-recommender

# Render.com deployment
# Push to GitHub → Render auto-deploys

# Railway deployment  
# Connect repo → Railway auto-configures and deploys

# See DEPLOYMENT.md for full instructions
```

---

**You now have a production-ready conversational assessment recommender system! 🚀**

Questions? Check the documentation files or review the code comments.
