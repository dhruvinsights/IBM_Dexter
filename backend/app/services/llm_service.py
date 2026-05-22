"""Flexible LLM service with support for multiple providers."""

import logging
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:  # pragma: no cover - legacy fallback
    from langchain_community.llms import Ollama  # type: ignore

from app.core.config import get_settings
from app.core.runtime_config import get_runtime_config

logger = logging.getLogger(__name__)
settings = get_settings()


def _ollama_base_url() -> str:
    return get_runtime_config().ollama_base_url()


def _ollama_model() -> str:
    return get_runtime_config().ollama_model()


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self):
        self.provider_name = self.__class__.__name__
        self.llm: Optional[LLM] = None
    
    @abstractmethod
    def initialize(self) -> LLM:
        """Initialize and return the LLM instance."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass
    
    def get_llm(self) -> LLM:
        """Get or initialize the LLM instance."""
        if self.llm is None:
            self.llm = self.initialize()
        return self.llm


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider for local models."""
    
    def initialize(self) -> LLM:
        """Initialize Ollama (see DEXTER_OLLAMA_MODEL / DEXTER_OLLAMA_NUM_CTX)."""
        try:
            logger.info(
                "Initializing Ollama model=%s num_ctx=%s base_url=%s",
                _ollama_model(),
                settings.ollama_num_ctx,
                _ollama_base_url(),
            )
            return Ollama(
                base_url=_ollama_base_url(),
                model=_ollama_model(),
                temperature=settings.llm_temperature,
                num_predict=settings.llm_max_tokens,
                num_ctx=settings.ollama_num_ctx,
                keep_alive=settings.ollama_keep_alive,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            import httpx
            response = httpx.get(f"{_ollama_base_url()}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False


class WatsonxProvider(BaseLLMProvider):
    """IBM Watsonx LLM provider."""
    
    def initialize(self) -> LLM:
        """Initialize IBM Watsonx."""
        try:
            from ibm_watsonx_ai.foundation_models import Model
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
            
            logger.info(f"Initializing Watsonx with model: {settings.watsonx_model}")
            
            credentials = {
                "url": settings.watsonx_url,
                "apikey": settings.watsonx_api_key
            }
            
            parameters = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.TEMPERATURE: settings.llm_temperature,
                GenParams.MAX_NEW_TOKENS: settings.llm_max_tokens,
            }
            
            model = Model(
                model_id=settings.watsonx_model,
                params=parameters,
                credentials=credentials,
                project_id=settings.watsonx_project_id
            )
            
            return WatsonxLLMWrapper(model)
        except Exception as e:
            logger.error(f"Failed to initialize Watsonx: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Watsonx is configured."""
        return bool(settings.watsonx_api_key and settings.watsonx_project_id)


class WatsonxLLMWrapper(LLM):
    """Wrapper to make Watsonx compatible with LangChain."""
    
    model: Any
    
    @property
    def _llm_type(self) -> str:
        return "watsonx"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Watsonx model."""
        try:
            response = self.model.generate_text(prompt=prompt)
            return response
        except Exception as e:
            logger.error(f"Watsonx generation error: {e}")
            raise


class OpenAIChatHTTPLLM(LLM):
    """OpenAI chat/completions via HTTPS (avoids legacy langchain-openai / SDK version skew)."""

    api_key: str = ""
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096
    request_timeout: int = 120

    @property
    def _llm_type(self) -> str:
        return "openai-chat-http"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        import httpx

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        body: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": min(self.max_tokens, 16384),
        }
        with httpx.Client(timeout=self.request_timeout) as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        content = msg.get("content")
        return (content or "").strip()


class OpenAIProvider(BaseLLMProvider):
    """OpenAI chat models (Completions API v1/chat/completions)."""

    def initialize(self) -> LLM:
        """Initialize OpenAI."""
        logger.info("Initializing OpenAI chat model: %s", settings.openai_model)
        return OpenAIChatHTTPLLM(
            api_key=(settings.openai_api_key or "").strip(),
            model_name=settings.openai_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            request_timeout=settings.llm_timeout,
        )

    def is_available(self) -> bool:
        """API key present."""
        return bool((settings.openai_api_key or "").strip())


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""
    
    def initialize(self) -> LLM:
        """Initialize Anthropic."""
        try:
            from langchain_community.llms import Anthropic
            
            logger.info(f"Initializing Anthropic with model: {settings.anthropic_model}")
            return Anthropic(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model,
                temperature=settings.llm_temperature,
                max_tokens_to_sample=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Anthropic is configured."""
        return bool(settings.anthropic_api_key)


class CohereProvider(BaseLLMProvider):
    """Cohere LLM provider."""
    
    def initialize(self) -> LLM:
        """Initialize Cohere."""
        try:
            from langchain_community.llms import Cohere
            
            logger.info(f"Initializing Cohere with model: {settings.cohere_model}")
            return Cohere(
                cohere_api_key=settings.cohere_api_key,
                model=settings.cohere_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Cohere: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Cohere is configured."""
        return bool(settings.cohere_api_key)


class LLMService:
    """Main LLM service with provider management and fallback."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.provider_name = settings.llm_provider
        self.providers: Dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(),
            "watsonx": WatsonxProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "cohere": CohereProvider(),
        }
        self.llm: Optional[LLM] = None
        self.fallback_order = ["watsonx", "openai", "anthropic", "cohere", "ollama"]
        
        # Initialize primary provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the configured LLM provider."""
        try:
            provider = self.providers.get(self.provider_name)
            if not provider:
                raise ValueError(f"Unknown provider: {self.provider_name}")
            
            if not provider.is_available():
                logger.warning(f"Provider {self.provider_name} not available, trying fallback")
                self._try_fallback()
                return
            
            self.llm = provider.get_llm()
            logger.info(f"Successfully initialized LLM provider: {self.provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize provider {self.provider_name}: {e}")
            self._try_fallback()
    
    def _try_fallback(self):
        """Try fallback providers in order."""
        for provider_name in self.fallback_order:
            if provider_name == self.provider_name:
                continue  # Skip the failed primary provider
            
            try:
                provider = self.providers[provider_name]
                if provider.is_available():
                    self.llm = provider.get_llm()
                    self.provider_name = provider_name
                    logger.info(f"Fallback to provider: {provider_name}")
                    return
            except Exception as e:
                logger.warning(f"Fallback provider {provider_name} failed: {e}")
                continue
        
        raise RuntimeError("No available LLM providers found")
    
    async def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate response from LLM with fallback support.
        
        Args:
            prompt: The input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Generated text response
        """
        if not self.llm:
            raise RuntimeError("No LLM provider initialized")
        
        try:
            logger.debug(f"Generating with provider: {self.provider_name}")
            response = await self.llm.ainvoke(prompt)
            if isinstance(response, str):
                return response
            return getattr(response, "content", str(response))
        except Exception as e:
            logger.error(f"Generation failed with {self.provider_name}: {e}")

            original_provider = self.provider_name
            try:
                self._try_fallback()
                if self.provider_name != original_provider:
                    logger.info(f"Retrying with fallback provider: {self.provider_name}")
                    response = await self.llm.ainvoke(prompt)
                    if isinstance(response, str):
                        return response
                    return getattr(response, "content", str(response))
            except Exception as fallback_error:
                logger.error(f"Fallback generation also failed: {fallback_error}")
                raise

            raise
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        return {
            "provider": self.provider_name,
            "available_providers": self.get_available_providers(),
            "settings": {
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens,
                "timeout": settings.llm_timeout,
            }
        }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers based on configuration."""
        available = []
        for name, provider in self.providers.items():
            if provider.is_available():
                available.append(name)
        return available
    
    def switch_provider(self, provider_name: str):
        """Switch to a different provider."""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider = self.providers[provider_name]
        if not provider.is_available():
            raise ValueError(f"Provider {provider_name} is not available")
        
        self.provider_name = provider_name
        self.llm = provider.get_llm()
        logger.info(f"Switched to provider: {provider_name}")
    
    def is_server_side_provider(self, provider: str) -> bool:
        """
        Check if provider requires backend/server-side processing.
        
        Args:
            provider: Provider name (ollama, openai, watsonx, anthropic)
        
        Returns:
            True if provider requires backend API calls, False if client-side (Ollama)
        """
        # Ollama can be called directly from frontend (client-side)
        # All other providers require backend API calls (server-side)
        return provider.lower() != "ollama"
    
    def validate_provider_access(self, provider: str, user_tier: str = "free") -> bool:
        """
        Validate if user has access to the specified provider.
        
        Args:
            provider: Provider name
            user_tier: User's subscription tier (free, paid, enterprise)
        
        Returns:
            True if user can access the provider
        """
        provider = provider.lower()
        
        # Ollama is always allowed (free tier)
        if provider == "ollama":
            return True
        
        # Cloud providers require paid tier
        if provider in ["openai", "watsonx", "anthropic", "cohere"]:
            return user_tier in ["paid", "enterprise"]
        
        # Unknown provider
        return False
    
    def get_provider_tier(self, provider: str) -> str:
        """
        Get the tier requirement for a provider.
        
        Args:
            provider: Provider name
        
        Returns:
            Tier requirement (free, paid, enterprise)
        """
        provider = provider.lower()
        
        if provider == "ollama":
            return "free"
        elif provider in ["openai", "anthropic", "cohere"]:
            return "paid"
        elif provider == "watsonx":
            return "enterprise"
        else:
            return "unknown"

    def refresh_ollama_configuration(self) -> None:
        """Drop cached Ollama client and re-bind if Ollama is the active provider."""
        ollama_provider = self.providers.get("ollama")
        if ollama_provider is not None:
            ollama_provider.llm = None
        if self.provider_name != "ollama" or ollama_provider is None:
            return
        try:
            self.llm = ollama_provider.get_llm()
            logger.info("Reloaded Ollama LLM after settings change")
        except Exception as exc:
            logger.error("Failed to reload Ollama after settings change: %s", exc)
            self._try_fallback()


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


# Made with Bob