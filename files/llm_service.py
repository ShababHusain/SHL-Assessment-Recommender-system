"""
LLM service for interacting with Google Gemini API (FREE).
Uses Google's Gemini 1.5 Flash model - completely free tier.
60 requests per minute - more than sufficient for production.
"""

import os
import json
import logging
from typing import Optional, Tuple, List, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for LLM interactions using Google Gemini API.
    FREE tier: 60 requests per minute, unlimited month.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize LLM service with Google Gemini.
        
        Args:
            api_key: API key (uses GOOGLE_API_KEY env var if not provided)
            model: Model to use (gemini-1.5-flash is free and fast)
        """
        self.api_key = api_key or os.getenv("AIzaSyDg6LU7WCLXcZYt725UcMmi0SgfblD5W5A")
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
        """
        Generate text using Google Gemini.
        
        Args:
            prompt: User message/prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            Generated text
        """
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
        """
        Generate and parse JSON output from Google Gemini.
        
        Args:
            prompt: Prompt requesting JSON
            system_prompt: System context
            max_tokens: Maximum tokens
        
        Returns:
            Parsed JSON dictionary
        """
        system = system_prompt or "You must respond with ONLY valid JSON, no other text."
        
        response_text = self.generate_text(
            prompt=prompt,
            system_prompt=system,
            max_tokens=max_tokens,
            temperature=0.3  # Lower temp for structured output
        )
        
        try:
            # Clean up response (remove markdown code blocks if present)
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

    def detect_intent(self, conversation: str) -> Tuple[str, float, Dict]:
        """
        Detect user intent from conversation.
        
        Returns:
            Tuple of (intent, confidence, context_dict)
        """
        from prompt_templates import INTENT_DETECTION_PROMPT
        
        prompt = INTENT_DETECTION_PROMPT.format(conversation=conversation)
        result = self.extract_json(prompt)
        
        return (
            result.get("intent", "clarification_needed"),
            result.get("confidence", 0.0),
            result.get("context", {})
        )

    def generate_clarification_question(
        self,
        role: Optional[str] = None,
        skills: Optional[List[str]] = None,
        goals: Optional[List[str]] = None
    ) -> str:
        """Generate clarifying question based on context."""
        from prompt_templates import CLARIFICATION_PROMPT
        
        prompt = CLARIFICATION_PROMPT.format(
            role=role or "Not mentioned",
            skills=", ".join(skills) if skills else "None mentioned",
            goals=", ".join(goals) if goals else "None mentioned"
        )
        
        return self.generate_text(prompt, temperature=0.8)

    def generate_recommendation_response(
        self,
        role: str,
        skills: Optional[List[str]] = None,
        goals: Optional[List[str]] = None,
        assessments: Optional[List[str]] = None
    ) -> str:
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

    def generate_comparison(
        self,
        assessment1: str,
        assessment2: str
    ) -> str:
        """Generate comparison of two assessments."""
        from prompt_templates import COMPARISON_PROMPT
        
        prompt = COMPARISON_PROMPT.format(
            assessment1=assessment1,
            assessment2=assessment2
        )
        
        return self.generate_text(prompt, temperature=0.5)

    def should_refuse(self, request: str) -> Tuple[bool, str]:
        """
        Determine if request should be refused.
        
        Returns:
            Tuple of (should_refuse: bool, reason: str)
        """
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
