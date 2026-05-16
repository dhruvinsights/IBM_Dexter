"""Base abstractions for Dexter review agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.services.llm_service import get_llm_service, LLMService

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Define the shared contract for all review agents."""

    agent_name: str = "base-agent"
    category: str = "general"

    def __init__(self):
        """Initialize the agent with LLM service."""
        self.llm_service: LLMService = get_llm_service()
        self.provider = self.llm_service.provider_name
        logger.info(f"Initialized {self.agent_name} with LLM provider: {self.provider}")

    @abstractmethod
    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """Analyze a pull request and return structured findings."""

    async def generate_llm_response(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        try:
            response = await self.llm_service.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"LLM generation failed in {self.agent_name}: {e}")
            raise

    def _build_prompt(self, context: dict[str, Any]) -> str:
        """
        Build a prompt for the LLM based on context.
        
        Args:
            context: Context dictionary with relevant information
            
        Returns:
            Formatted prompt string
        """
        # Default implementation - agents should override this
        return str(context)

    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        """
        Parse the LLM response into structured data.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed structured data
        """
        # Default implementation - agents should override this
        return {"raw_response": response}

    def format_result(
        self,
        summary: str,
        findings: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a standard result payload for all agents."""
        result_metadata = metadata or {}
        result_metadata["llm_provider"] = self.provider
        
        return {
            "agent": self.agent_name,
            "category": self.category,
            "summary": summary,
            "findings": findings,
            "metadata": result_metadata,
        }

    def get_llm_info(self) -> dict[str, Any]:
        """Get information about the current LLM configuration."""
        return self.llm_service.get_provider_info()

# Made with Bob
