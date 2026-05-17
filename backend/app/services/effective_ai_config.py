"""Resolved AI configuration for APIs and Settings UI (env + runtime Ollama overrides)."""

from __future__ import annotations

from typing import Any, Dict

from app.core.config import Settings
from app.core.runtime_config import RuntimeConfig


def effective_llm_model(settings: Settings, rc: RuntimeConfig) -> str:
    """Model id for the configured LLM provider."""
    p = (settings.llm_provider or "").lower()
    if p == "ollama":
        return rc.ollama_model() or settings.ollama_model
    if p == "watsonx":
        return settings.watsonx_model
    if p == "openai":
        return settings.openai_model
    if p == "anthropic":
        return settings.anthropic_model
    if p == "cohere":
        return settings.cohere_model
    return settings.watsonx_model


def embedding_runtime_summary(settings: Settings, rc: RuntimeConfig) -> Dict[str, Any]:
    """Embedding provider + model + vector size for RAG / knowledge base."""
    prov = (settings.embedding_provider or "openai").lower()
    if prov == "openai":
        return {
            "provider": "openai",
            "model": settings.openai_embedding_model,
            "dimension": settings.embedding_dimension,
            "api_key_configured": bool((settings.openai_api_key or "").strip()),
        }
    return {
        "provider": "ollama",
        "model": settings.ollama_embedding_model,
        "base_url": rc.ollama_base_url(),
        "dimension": settings.embedding_dimension,
        "api_key_configured": None,
    }


def hosted_deployment_hints(settings: Settings) -> Dict[str, Any]:
    """Notices for cloud deployments (localhost Ollama not reachable from the server)."""
    show = settings.app_env in ("staging", "production")
    if settings.force_hosted_ollama_notice:
        show = True
    return {
        "hosted_ollama_notice_visible": show,
        "hosted_ollama_notice": (
            "This Dexter instance is not running on your laptop. A browser or hosted server cannot use "
            "Ollama at http://localhost:11434 on your machine. "
            "Configure IBM watsonx (default), OpenAI, or another cloud provider via environment variables, "
            "or set Ollama to a **reachable** URL (private server, VPN, or tunnel). "
            "Ollama stays supported for local and future desktop packaging."
        ),
        "desktop_app_teaser": (
            "A Dexter desktop app is planned so you can run reviews with on-device models—better privacy "
            "and predictable cost. This web build will keep cloud providers as the main path."
        ),
    }


def llm_runtime_summary(settings: Settings, rc: RuntimeConfig) -> Dict[str, Any]:
    """Single object for Settings “Chat / LLM” panel."""
    p = (settings.llm_provider or "").lower()
    return {
        "provider": settings.llm_provider,
        "effective_model": effective_llm_model(settings, rc),
        "ollama_base_url": rc.ollama_base_url() if p == "ollama" else None,
        "watsonx_model": settings.watsonx_model if p == "watsonx" else None,
        "watsonx_url": settings.watsonx_url if p == "watsonx" else None,
        "watsonx_configured": bool((settings.watsonx_api_key or "").strip() and (settings.watsonx_project_id or "").strip()),
        "openai_model": settings.openai_model if p == "openai" else None,
        "openai_configured": bool((settings.openai_api_key or "").strip()),
        "configuration_source": "environment",
        "note": "Change DEXTER_LLM_PROVIDER and provider-specific variables in backend .env, then restart the API.",
    }
