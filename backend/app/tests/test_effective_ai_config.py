"""Unit tests for effective_ai_config helpers."""

from __future__ import annotations

import pytest

from app.core.config import get_settings
from app.core.runtime_config import RuntimeConfig
from app.services.effective_ai_config import (
    effective_llm_model,
    embedding_runtime_summary,
    hosted_deployment_hints,
    llm_runtime_summary,
)


def test_effective_llm_model_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_LLM_PROVIDER", "openai")
    monkeypatch.setenv("DEXTER_OPENAI_MODEL", "gpt-4o")
    get_settings.cache_clear()
    s = get_settings()
    rc = RuntimeConfig()
    assert effective_llm_model(s, rc) == "gpt-4o"


def test_effective_llm_model_ollama_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("DEXTER_OLLAMA_MODEL", "qwen2.5-coder:14b")
    get_settings.cache_clear()
    s = get_settings()
    rc = RuntimeConfig()
    rc.set("ollama_model", "mistral:latest")
    assert effective_llm_model(s, rc) == "mistral:latest"


def test_embedding_runtime_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("DEXTER_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.setenv("DEXTER_EMBEDDING_DIMENSION", "1536")
    monkeypatch.setenv("DEXTER_OPENAI_API_KEY", "sk-live")
    get_settings.cache_clear()
    s = get_settings()
    rc = RuntimeConfig()
    out = embedding_runtime_summary(s, rc)
    assert out["provider"] == "openai"
    assert out["model"] == "text-embedding-3-small"
    assert out["dimension"] == 1536
    assert out["api_key_configured"] is True


def test_hosted_notice_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_APP_ENV", "production")
    get_settings.cache_clear()
    s = get_settings()
    hints = hosted_deployment_hints(s)
    assert hints["hosted_ollama_notice_visible"] is True
    assert "localhost" in hints["hosted_ollama_notice"]


def test_llm_runtime_summary_watsonx(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEXTER_LLM_PROVIDER", "watsonx")
    monkeypatch.setenv("DEXTER_WATSONX_MODEL", "ibm/granite-13b-chat-v2")
    monkeypatch.setenv("DEXTER_WATSONX_API_KEY", "k")
    monkeypatch.setenv("DEXTER_WATSONX_PROJECT_ID", "p")
    get_settings.cache_clear()
    s = get_settings()
    rc = RuntimeConfig()
    snap = llm_runtime_summary(s, rc)
    assert snap["effective_model"] == "ibm/granite-13b-chat-v2"
    assert snap["watsonx_configured"] is True
