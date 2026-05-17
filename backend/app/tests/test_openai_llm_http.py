"""OpenAI chat HTTP wrapper."""

from __future__ import annotations

import httpx
import pytest
import respx
from httpx import Response

from app.services.llm_service import OpenAIChatHTTPLLM

pytestmark = pytest.mark.no_llm_stub


@respx.mock
def test_openai_chat_http_call() -> None:
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=Response(
            200,
            json={"choices": [{"message": {"content": " OK "}}]},
        )
    )
    llm = OpenAIChatHTTPLLM(
        api_key="sk-x",
        model_name="gpt-4o-mini",
        temperature=0.2,
        max_tokens=100,
        request_timeout=30,
    )
    out = llm._call("ping")
    assert out == "OK"


@respx.mock
def test_openai_chat_raises_on_http_error() -> None:
    respx.post("https://api.openai.com/v1/chat/completions").mock(return_value=Response(401, json={"error": "bad"}))
    llm = OpenAIChatHTTPLLM(api_key="sk-x", model_name="gpt-4o-mini", request_timeout=10)
    with pytest.raises(httpx.HTTPStatusError):
        llm._call("ping")
