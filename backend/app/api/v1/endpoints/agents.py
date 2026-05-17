"""Agents API: list available agents and their runtime status."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.runtime_config import get_runtime_config
from app.services.ai_service import AIReviewService

router = APIRouter()
settings = get_settings()


_AGENT_METADATA: Dict[str, Dict[str, Any]] = {
    "security-agent": {
        "display_name": "Security Agent",
        "category": "security",
        "description": "Detects hardcoded credentials, injection, auth gaps, and other AppSec issues using regex + LLM.",
        "rag_enabled": True,
    },
    "architecture-agent": {
        "display_name": "Architecture Agent",
        "category": "architecture",
        "description": "Reviews design patterns, dependency direction, and patch size for maintainability.",
        "rag_enabled": True,
    },
    "compliance-agent": {
        "display_name": "Compliance Agent",
        "category": "compliance",
        "description": "Flags auditability, policy, and standards violations.",
        "rag_enabled": True,
    },
}


@router.get("/agents")
async def list_agents() -> List[Dict[str, Any]]:
    """Return all agents registered in the AI review pipeline."""
    review_service = AIReviewService()
    out: List[Dict[str, Any]] = []
    for agent in review_service.agents:
        meta = _AGENT_METADATA.get(agent.agent_name, {})
        out.append({
            "id": agent.agent_name,
            "display_name": meta.get("display_name", agent.agent_name),
            "category": meta.get("category", agent.category),
            "description": meta.get("description", ""),
            "rag_enabled": meta.get("rag_enabled", False),
            "llm_provider": getattr(agent, "provider", "unknown"),
            "status": "active",
        })
    return out


@router.get("/agents/status")
async def agents_status() -> Dict[str, Any]:
    """Return aggregate status info for the AI Agents dashboard."""
    review_service = AIReviewService()
    rc = get_runtime_config()
    return {
        "llm_provider": settings.llm_provider,
        "llm_model": rc.ollama_model(),
        "llm_base_url": rc.ollama_base_url(),
        "agent_count": len(review_service.agents),
        "agents": [agent.agent_name for agent in review_service.agents],
    }


# Made with Bob
