"""Factory pattern for LLM initialization and management."""

import logging
from typing import Dict, List, Optional, Type
from enum import Enum

from app.core.config import get_settings
from app.services.llm_service import (
    BaseLLMProvider,
    OllamaProvider,
    WatsonxProvider,
    OpenAIProvider,
    AnthropicProvider,
    CohereProvider,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMProviderType(str, Enum):
    """Enumeration of supported LLM providers."""
    OLLAMA = "ollama"
    WATSONX = "watsonx"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"


class LLMFactory:
    """Factory for creating and managing LLM provider instances."""
    
    # Registry of provider classes
    _provider_registry: Dict[str, Type[BaseLLMProvider]] = {
        LLMProviderType.OLLAMA: OllamaProvider,
        LLMProviderType.WATSONX: WatsonxProvider,
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.ANTHROPIC: AnthropicProvider,
        LLMProviderType.COHERE: CohereProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_type: str) -> BaseLLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            provider_type: Type of provider to create
            
        Returns:
            Initialized provider instance
            
        Raises:
            ValueError: If provider type is unknown
        """
        provider_class = cls._provider_registry.get(provider_type)
        if not provider_class:
            raise ValueError(
                f"Unknown provider type: {provider_type}. "
                f"Available: {list(cls._provider_registry.keys())}"
            )
        
        logger.info(f"Creating provider: {provider_type}")
        return provider_class()
    
    @classmethod
    def get_available_providers(cls) -> List[Dict[str, any]]:
        """
        Get list of available providers with their configuration status.
        
        Returns:
            List of provider information dictionaries
        """
        available = []
        
        for provider_type, provider_class in cls._provider_registry.items():
            try:
                provider = provider_class()
                is_available = provider.is_available()
                
                provider_info = {
                    "type": provider_type,
                    "name": provider_class.__name__,
                    "available": is_available,
                    "configured": cls._is_configured(provider_type),
                }
                
                # Add provider-specific details
                if provider_type == LLMProviderType.OLLAMA:
                    provider_info["details"] = {
                        "base_url": settings.ollama_base_url,
                        "model": settings.ollama_model,
                    }
                elif provider_type == LLMProviderType.WATSONX:
                    provider_info["details"] = {
                        "url": settings.watsonx_url,
                        "model": settings.watsonx_model,
                        "has_api_key": bool(settings.watsonx_api_key),
                        "has_project_id": bool(settings.watsonx_project_id),
                    }
                elif provider_type == LLMProviderType.OPENAI:
                    provider_info["details"] = {
                        "model": settings.openai_model,
                        "has_api_key": bool(settings.openai_api_key),
                    }
                elif provider_type == LLMProviderType.ANTHROPIC:
                    provider_info["details"] = {
                        "model": settings.anthropic_model,
                        "has_api_key": bool(settings.anthropic_api_key),
                    }
                elif provider_type == LLMProviderType.COHERE:
                    provider_info["details"] = {
                        "model": settings.cohere_model,
                        "has_api_key": bool(settings.cohere_api_key),
                    }
                
                available.append(provider_info)
            except Exception as e:
                logger.warning(f"Error checking provider {provider_type}: {e}")
                available.append({
                    "type": provider_type,
                    "name": provider_class.__name__,
                    "available": False,
                    "configured": False,
                    "error": str(e),
                })
        
        return available
    
    @classmethod
    def _is_configured(cls, provider_type: str) -> bool:
        """
        Check if a provider is properly configured.
        
        Args:
            provider_type: Type of provider to check
            
        Returns:
            True if provider is configured
        """
        if provider_type == LLMProviderType.OLLAMA:
            return True  # Ollama is always "configured" (local)
        elif provider_type == LLMProviderType.WATSONX:
            return bool(settings.watsonx_api_key and settings.watsonx_project_id)
        elif provider_type == LLMProviderType.OPENAI:
            return bool(settings.openai_api_key)
        elif provider_type == LLMProviderType.ANTHROPIC:
            return bool(settings.anthropic_api_key)
        elif provider_type == LLMProviderType.COHERE:
            return bool(settings.cohere_api_key)
        return False
    
    @classmethod
    def get_default_provider(cls) -> str:
        """
        Get the default provider based on configuration.
        
        Returns:
            Default provider type
        """
        # Use configured provider if set
        if settings.llm_provider in cls._provider_registry:
            return settings.llm_provider
        
        # Fallback order: Ollama -> Watsonx -> OpenAI -> Anthropic -> Cohere
        fallback_order = [
            LLMProviderType.OLLAMA,
            LLMProviderType.WATSONX,
            LLMProviderType.OPENAI,
            LLMProviderType.ANTHROPIC,
            LLMProviderType.COHERE,
        ]
        
        for provider_type in fallback_order:
            if cls._is_configured(provider_type):
                try:
                    provider = cls.create_provider(provider_type)
                    if provider.is_available():
                        logger.info(f"Using default provider: {provider_type}")
                        return provider_type
                except Exception as e:
                    logger.warning(f"Provider {provider_type} not available: {e}")
                    continue
        
        # Default to Ollama even if not available (will fail gracefully)
        logger.warning("No available providers found, defaulting to Ollama")
        return LLMProviderType.OLLAMA
    
    @classmethod
    def register_provider(
        cls,
        provider_type: str,
        provider_class: Type[BaseLLMProvider]
    ):
        """
        Register a custom provider class.
        
        Args:
            provider_type: Unique identifier for the provider
            provider_class: Provider class to register
        """
        if provider_type in cls._provider_registry:
            logger.warning(f"Overwriting existing provider: {provider_type}")
        
        cls._provider_registry[provider_type] = provider_class
        logger.info(f"Registered provider: {provider_type}")
    
    @classmethod
    def get_provider_config(cls, provider_type: str) -> Dict[str, any]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider_type: Type of provider
            
        Returns:
            Provider configuration dictionary
        """
        config = {
            "provider": provider_type,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
            "timeout": settings.llm_timeout,
        }
        
        if provider_type == LLMProviderType.OLLAMA:
            config.update({
                "base_url": settings.ollama_base_url,
                "model": settings.ollama_model,
            })
        elif provider_type == LLMProviderType.WATSONX:
            config.update({
                "url": settings.watsonx_url,
                "model": settings.watsonx_model,
                "project_id": settings.watsonx_project_id,
            })
        elif provider_type == LLMProviderType.OPENAI:
            config.update({
                "model": settings.openai_model,
            })
        elif provider_type == LLMProviderType.ANTHROPIC:
            config.update({
                "model": settings.anthropic_model,
            })
        elif provider_type == LLMProviderType.COHERE:
            config.update({
                "model": settings.cohere_model,
            })
        
        return config
    
    @classmethod
    def validate_provider_config(cls, provider_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate provider configuration.
        
        Args:
            provider_type: Type of provider to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if provider_type not in cls._provider_registry:
            return False, f"Unknown provider type: {provider_type}"
        
        if not cls._is_configured(provider_type):
            return False, f"Provider {provider_type} is not configured"
        
        try:
            provider = cls.create_provider(provider_type)
            if not provider.is_available():
                return False, f"Provider {provider_type} is not available"
            
            # Try to initialize
            provider.initialize()
            return True, None
        except Exception as e:
            return False, f"Provider initialization failed: {str(e)}"


# Convenience functions
def create_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    """
    Create an LLM provider instance.
    
    Args:
        provider_type: Type of provider (defaults to configured provider)
        
    Returns:
        Initialized provider instance
    """
    if provider_type is None:
        provider_type = LLMFactory.get_default_provider()
    
    return LLMFactory.create_provider(provider_type)


def get_available_providers() -> List[Dict[str, any]]:
    """Get list of available providers."""
    return LLMFactory.get_available_providers()


def validate_provider(provider_type: str) -> tuple[bool, Optional[str]]:
    """Validate a provider configuration."""
    return LLMFactory.validate_provider_config(provider_type)


# Made with Bob