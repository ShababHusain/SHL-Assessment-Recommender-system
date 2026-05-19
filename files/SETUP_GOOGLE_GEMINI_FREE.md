# 🆓 FREE SETUP - Google Gemini API (5 minutes)

## The Easiest Free Option

Google's Gemini API is **completely free** with no credit card needed.

---

## Step 1: Get Free API Key (2 minutes)

1. Go to: **https://ai.google.dev/**
2. Click **"Get API Key"** (top right)
3. Click **"Create API Key in new Google Cloud project"**
4. **Copy the key** (looks like: `AIzaSy...`)
5. **Save it somewhere safe**

✅ **That's it! No credit card needed!**

---

## Step 2: Update Your Code (3 minutes)

### File 1: Replace `llm_service.py`

Delete the old file and create new one with this code:

```python
"""
LLM service using Google Gemini API (FREE)
"""

import os
import json
import logging
from typing import Optional, Dict, Any

import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMService:
    """Service for Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize LLM service.
        
        Args:
            api_key: API key (uses GOOGLE_API_KEY env var if not provided)
            model: Model to use (gemini-1.5-flash is free and fast)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate text using Google Gemini."""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                ),
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_UNSPECIFIED",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"LLM generation error: {e}", exc_info=True)
            raise

    def extract_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generate and parse JSON output."""
        system = system_prompt or "You must respond with ONLY valid JSON, no other text."
        
        response_text = self.generate_text(
            prompt=prompt,
            system_prompt=system,
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}\nResponse: {response_text}")
            raise ValueError(f"Failed to parse JSON response: {e}")

    def detect_intent(self, conversation: str) -> tuple:
        """Detect user intent from conversation."""
        from prompt_templates import INTENT_DETECTION_PROMPT
        
        prompt = INTENT_DETECTION_PROMPT.format(conversation=conversation)
        result = self.extract_json(prompt)
        
        return (
            result.get("intent", "clarification_needed"),
            result.get("confidence", 0.0),
            result.get("context", {})
        )

    def generate_clarification_question(self, role=None, skills=None, goals=None) -> str:
        """Generate clarifying question."""
        from prompt_templates import CLARIFICATION_PROMPT
        
        prompt = CLARIFICATION_PROMPT.format(
            role=role or "Not mentioned",
            skills=", ".join(skills) if skills else "None mentioned",
            goals=", ".join(goals) if goals else "None mentioned"
        )
        
        return self.generate_text(prompt, temperature=0.8)

    def generate_recommendation_response(self, role, skills=None, goals=None, assessments=None) -> str:
        """Generate response with recommendations."""
        from prompt_templates import RECOMMENDATION_RESPONSE_PROMPT
        
        assess_text = "\n".join(assessments) if assessments else "No assessments"
        
        prompt = RECOMMENDATION_RESPONSE_PROMPT.format(
            role=role,
            skills=", ".join(skills) if skills else "Not specified",
            goals=", ".join(goals) if goals else "Not specified",
            assessments=assess_text
        )
        
        return self.generate_text(prompt, temperature=0.7)

    def generate_comparison(self, assessment1: str, assessment2: str) -> str:
        """Generate comparison of two assessments."""
        from prompt_templates import COMPARISON_PROMPT
        
        prompt = COMPARISON_PROMPT.format(
            assessment1=assessment1,
            assessment2=assessment2
        )
        
        return self.generate_text(prompt, temperature=0.5)

    def should_refuse(self, request: str) -> tuple:
        """Determine if request should be refused."""
        from prompt_templates import REFUSAL_PROMPT
        
        prompt = REFUSAL_PROMPT.format(request=request)
        result = self.extract_json(prompt)
        
        return (
            result.get("should_refuse", False),
            result.get("reason", "")
        )

    def extract_context(self, conversation: str) -> Dict[str, Any]:
        """Extract structured context from conversation."""
        from prompt_templates import CONTEXT_EXTRACTION_PROMPT
        
        prompt = CONTEXT_EXTRACTION_PROMPT.format(conversation=conversation)
        return self.extract_json(prompt)
```

### File 2: Update `requirements.txt`

Replace the old one with:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.3
google-generativeai==0.3.0
python-dotenv==1.0.0
pytest==7.4.3
beautifulsoup4==4.12.2
requests==2.31.0
```

---

## Step 3: Set Environment Variable

Create `.env` file in your project:

```bash
cat > .env << 'EOF'
GOOGLE_API_KEY=AIzaSy_YOUR_API_KEY_HERE
PORT=8000
LOG_LEVEL=info
EOF
```

Or set as environment variable:

```bash
export GOOGLE_API_KEY=AIzaSy_YOUR_API_KEY_HERE
```

---

## Step 4: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Build data
python build_catalog.py
python build_embeddings.py

# Start server
python -m uvicorn main:app --reload

# Test in another terminal
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need to hire a Java developer"}
    ]
  }'
```

✅ Should return recommendations!

---

## Step 5: Deploy to Render

### 5.1 Push to GitHub

```bash
git add .
git commit -m "Switch to Google Gemini API (free)"
git push origin main
```

### 5.2 Deploy on Render

1. Go to **https://render.com**
2. Sign up with GitHub
3. Click **"New Web Service"**
4. Select your `shl-recommender` repo
5. Set environment variables:
   - `GOOGLE_API_KEY` = Your API key
   - `PORT` = 8000
6. Create disk:
   - Name: `data`
   - Mount: `/app/data`
   - Size: `5 GB`
7. Click **"Create Web Service"**
8. Wait 5-10 minutes
9. **Copy your live URL!** 🎉

---

## 🎉 You're Done!

Your API is now live and **completely free**!

```
GET    https://shl-recommender-XXXXX.onrender.com/health
POST   https://shl-recommender-XXXXX.onrender.com/chat
```

---

## Free Tier Limits

- ✅ **No credit card required**
- ✅ **60 requests per minute** (plenty!)
- ✅ **Powerful model** (Gemini 1.5 Flash)
- ✅ **Unlimited for 12 months** (free tier)

After 12 months, very affordable pricing.

---

## Cost Comparison

| Service | Cost | Setup |
|---------|------|-------|
| **Google Gemini** | FREE (60 req/min) | 5 min |
| **Ollama Local** | FREE | 10 min |
| **Anthropic** | Paid | 5 min |

---

## If You Want Local (No Internet)

Use **Ollama** instead:

```bash
# Install from: https://ollama.ai

# Start Ollama
ollama serve

# In another terminal
ollama pull mistral

# Copy code from FREE_LLM_ALTERNATIVES.md (Option 2: Ollama)
# Update llm_service.py to use Ollama
# Run your app!
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "GOOGLE_API_KEY not found" | Set in `.env` file or environment variable |
| API limits exceeded | Free tier has 60 req/min limit, should be fine |
| "Safety violation" | Model might refuse some prompts, add safety_settings |
| Import error | Run `pip install google-generativeai` |

---

## Summary

✅ **Free forever** - No credit card  
✅ **60 requests/minute** - More than enough  
✅ **Powerful model** - Gemini 1.5 Flash  
✅ **5 minute setup** - Easy!  
✅ **Deploy anywhere** - Works with Render  

**You're ready to deploy!** 🚀
