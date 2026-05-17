"""
Conversational agent orchestrator.
Combines intent detection, retrieval, LLM generation, and decision logic.
"""

import logging
from typing import List, Tuple, Optional, Dict, Any
from schemas import Message, MessageRole, ChatResponse, Recommendation
from rag_retriever import RAGRetriever
from llm_service import LLMService
from prompt_templates import (
    SYSTEM_PROMPT,
    format_conversation_for_prompt,
    format_assessment_for_prompt
)

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """
    Orchestrates multi-turn conversation for assessment recommendations.
    Handles clarification, recommendation, refinement, comparison, and refusal.
    """

    def __init__(self, retriever: RAGRetriever, llm: LLMService):
        """
        Initialize agent.
        
        Args:
            retriever: RAGRetriever instance
            llm: LLMService instance
        """
        self.retriever = retriever
        self.llm = llm

    def process_message(self, messages: List[Message]) -> ChatResponse:
        """
        Process multi-turn conversation and generate response.
        
        Args:
            messages: List of conversation messages (last is from user)
        
        Returns:
            ChatResponse with reply, recommendations, and end-of-conversation flag
        """
        try:
            # Extract user query (last message)
            user_query = messages[-1].content
            
            # Build conversation history for context
            conv_history = format_conversation_for_prompt(
                [{"role": m.role.value, "content": m.content} for m in messages]
            )
            
            # Step 1: Check for refusal (out-of-scope requests)
            should_refuse, refusal_reason = self.llm.should_refuse(user_query)
            if should_refuse:
                return self._handle_refusal(refusal_reason)
            
            # Step 2: Detect intent
            intent, confidence, context = self.llm.detect_intent(conv_history)
            logger.info(f"Detected intent: {intent} (confidence: {confidence})")
            
            # Step 3: Route based on intent
            if intent == "clarification_needed":
                return self._handle_clarification(context)
            
            elif intent == "ready_to_recommend":
                return self._handle_recommendation(context, user_query)
            
            elif intent == "refine_recommendations":
                return self._handle_refinement(context, user_query)
            
            elif intent == "compare_assessments":
                return self._handle_comparison(user_query)
            
            else:
                # Default: ask for clarification
                return self._handle_clarification(context)
        
        except Exception as e:
            logger.error(f"Agent processing error: {e}", exc_info=True)
            return ChatResponse(
                reply="I encountered an error processing your request. Please try again.",
                recommendations=[],
                end_of_conversation=False
            )

    def _handle_clarification(self, context: Dict[str, Any]) -> ChatResponse:
        """Handle clarification phase - ask follow-up questions."""
        try:
            ctx = context.get("context", {})
            role = ctx.get("role")
            skills = ctx.get("skills", [])
            goals = ctx.get("goals", [])
            
            # Generate clarification question
            question = self.llm.generate_clarification_question(role, skills, goals)
            
            return ChatResponse(
                reply=question,
                recommendations=[],
                end_of_conversation=False
            )
        
        except Exception as e:
            logger.error(f"Clarification error: {e}")
            return ChatResponse(
                reply="Could you tell me more about the role you're hiring for?",
                recommendations=[],
                end_of_conversation=False
            )

    def _handle_recommendation(
        self,
        context: Dict[str, Any],
        user_query: str
    ) -> ChatResponse:
        """Handle recommendation phase - retrieve and recommend assessments."""
        try:
            ctx = context.get("context", {})
            role = ctx.get("role", "Unknown")
            skills = ctx.get("skills", [])
            goals = ctx.get("goals", [])
            
            # Retrieve relevant assessments
            recommendations = self.retriever.retrieve(
                user_query,
                top_k=5
            )
            
            # Fall back to context-based retrieval if no results
            if not recommendations:
                recommendations = self.retriever.retrieve_for_context(
                    role=role,
                    skills=skills if skills else None,
                    assessment_goals=goals if goals else None
                )
            
            # Limit to 10 per PRD
            recommendations = recommendations[:10]
            
            if not recommendations:
                reply = f"I couldn't find specific SHL assessments matching those criteria. Could you clarify the role or specific skills you're assessing?"
            else:
                # Generate response with recommendations
                rec_text = "\n".join([
                    f"- {rec.name} ({rec.test_type})"
                    for rec in recommendations
                ])
                
                reply = self.llm.generate_recommendation_response(
                    role=role,
                    skills=skills if skills else None,
                    goals=goals if goals else None,
                    assessments=[rec_text]
                )
            
            return ChatResponse(
                reply=reply,
                recommendations=recommendations,
                end_of_conversation=False
            )
        
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            return ChatResponse(
                reply="I had trouble retrieving recommendations. Could you provide more details?",
                recommendations=[],
                end_of_conversation=False
            )

    def _handle_refinement(
        self,
        context: Dict[str, Any],
        user_query: str
    ) -> ChatResponse:
        """Handle refinement - update recommendations based on new requirements."""
        try:
            # Re-retrieve with updated query
            recommendations = self.retriever.retrieve(user_query, top_k=5)
            recommendations = recommendations[:10]
            
            reply = f"I've updated the recommendations based on your requirements. {len(recommendations)} assessments match your criteria."
            
            return ChatResponse(
                reply=reply,
                recommendations=recommendations,
                end_of_conversation=False
            )
        
        except Exception as e:
            logger.error(f"Refinement error: {e}")
            return ChatResponse(
                reply="I had trouble refining the recommendations. Could you clarify?",
                recommendations=[],
                end_of_conversation=False
            )

    def _handle_comparison(self, user_query: str) -> ChatResponse:
        """Handle assessment comparison."""
        try:
            # Extract assessment names from query
            # Simple heuristic: look for known assessment names in query
            assessment_names = self._extract_assessment_names(user_query)
            
            if len(assessment_names) < 2:
                return ChatResponse(
                    reply="Could you specify which two assessments you'd like to compare?",
                    recommendations=[],
                    end_of_conversation=False
                )
            
            # Retrieve full details
            assess1, assess2 = self.retriever.compare_assessments(assessment_names[:2])
            
            if not assess1 or not assess2:
                return ChatResponse(
                    reply="I couldn't find those assessments in the catalog.",
                    recommendations=[],
                    end_of_conversation=False
                )
            
            # Generate comparison
            comparison = self.llm.generate_comparison(
                format_assessment_for_prompt(assess1),
                format_assessment_for_prompt(assess2)
            )
            
            return ChatResponse(
                reply=comparison,
                recommendations=[],
                end_of_conversation=False
            )
        
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            return ChatResponse(
                reply="I couldn't compare those assessments. Please try again.",
                recommendations=[],
                end_of_conversation=False
            )

    def _handle_refusal(self, reason: str) -> ChatResponse:
        """Handle refusal of out-of-scope requests."""
        from prompt_templates import REFUSAL_RESPONSE, OUT_OF_SCOPE_RESPONSE
        
        if reason:
            reply = OUT_OF_SCOPE_RESPONSE.format(reason=reason)
        else:
            reply = REFUSAL_RESPONSE
        
        return ChatResponse(
            reply=reply,
            recommendations=[],
            end_of_conversation=False
        )

    def _extract_assessment_names(self, text: str) -> List[str]:
        """
        Extract assessment names from text (simple heuristic).
        Returns list of assessment names found in query.
        """
        names = []
        catalog_names = [m.get("name", "").lower() for m in self.retriever.faiss.metadata]
        
        text_lower = text.lower()
        for catalog_name in set(catalog_names):
            if catalog_name and catalog_name in text_lower:
                # Find original name
                for m in self.retriever.faiss.metadata:
                    if m.get("name", "").lower() == catalog_name:
                        names.append(m.get("name", ""))
                        break
        
        return names[:2]  # Return up to 2 names
