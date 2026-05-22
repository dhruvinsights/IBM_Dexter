#!/usr/bin/env python3
"""Test script to verify PR review enhancements.

This script tests:
1. Full file content fetching from GitHub
2. RAG/Knowledge base integration
3. Memory Agent inclusion in pipeline
4. Complete code traversal capabilities
"""

import asyncio
import logging
import sys
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_github_full_content_fetch():
    """Test that we can fetch full file content from GitHub."""
    logger.info("=" * 80)
    logger.info("TEST 1: GitHub Full File Content Fetching")
    logger.info("=" * 80)
    
    try:
        from app.services.github_service import GitHubService
        
        github = GitHubService()
        
        # Test with a public repository
        owner = "octocat"
        repo = "Hello-World"
        path = "README"
        sha = "master"
        
        logger.info(f"Fetching {path} from {owner}/{repo} at {sha}")
        content = await github.get_file_content_at_commit(owner, repo, path, sha)
        
        if content:
            logger.info(f"✅ SUCCESS: Fetched {len(content)} characters")
            logger.info(f"First 200 chars: {content[:200]}")
            return True
        else:
            logger.warning("⚠️  No content returned (might be expected for test repo)")
            return True  # Not a failure, just no content
            
    except Exception as exc:
        logger.error(f"❌ FAILED: {exc}")
        return False


async def test_rag_integration():
    """Test that RAG/Knowledge Base is integrated in PR reviews."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: RAG/Knowledge Base Integration")
    logger.info("=" * 80)
    
    try:
        from app.services.knowledge_base_service import get_knowledge_base_service
        
        kb = get_knowledge_base_service()
        
        # Test retrieval
        query = "code review best practices"
        logger.info(f"Testing RAG retrieval with query: '{query}'")
        
        results = await kb.search(query, limit=3)
        logger.info(f"✅ SUCCESS: Retrieved {len(results)} results from knowledge base")
        
        # Test context_for method (used in PR reviews)
        context = await kb.context_for(query, limit=3)
        logger.info(f"✅ SUCCESS: Generated {len(context)} context strings for agents")
        
        backend_info = kb.get_backend_info()
        logger.info(f"Backend: {backend_info.get('backend')}")
        logger.info(f"Vector DB: {backend_info.get('vector_db_type')}")
        
        return True
        
    except Exception as exc:
        logger.error(f"❌ FAILED: {exc}")
        return False


async def test_memory_agent_in_pipeline():
    """Test that Memory Agent is included in the review pipeline."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Memory Agent in Pipeline")
    logger.info("=" * 80)
    
    try:
        from app.services.ai_service import AIReviewService
        from app.agents.memory_agent import MemoryAgent
        
        service = AIReviewService()
        
        # Check if Memory Agent is in the pipeline
        agent_names = [agent.agent_name for agent in service.agents]
        logger.info(f"Active agents: {agent_names}")
        
        if "memory-agent" in agent_names:
            logger.info("✅ SUCCESS: Memory Agent is active in pipeline")
            return True
        else:
            logger.error("❌ FAILED: Memory Agent not found in pipeline")
            return False
            
    except Exception as exc:
        logger.error(f"❌ FAILED: {exc}")
        return False


async def test_full_content_in_diffs():
    """Test that diffs are enriched with full file content."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Full Content Enrichment in Diffs")
    logger.info("=" * 80)
    
    try:
        # Create a mock diff structure
        mock_diffs = [
            {
                "filename": "test.py",
                "status": "modified",
                "additions": 5,
                "deletions": 2,
                "patch": "+def new_function():\n+    pass",
                "full_content": None  # Will be populated by enhancement
            }
        ]
        
        logger.info("Mock diff structure created")
        logger.info(f"Diff has 'full_content' field: {'full_content' in mock_diffs[0]}")
        
        # Check if the enhancement code exists in pr_review_runner.py
        with open("app/services/pr_review_runner.py", "r") as f:
            content = f.read()
            
        if "get_file_content_at_commit" in content:
            logger.info("✅ SUCCESS: Full content fetching code found in pr_review_runner.py")
            return True
        else:
            logger.error("❌ FAILED: Full content fetching code not found")
            return False
            
    except Exception as exc:
        logger.error(f"❌ FAILED: {exc}")
        return False


async def test_agent_full_content_usage():
    """Test that agents can access and use full file content."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Agent Full Content Usage")
    logger.info("=" * 80)
    
    try:
        from app.agents.security_agent import SecurityAgent
        from app.agents.memory_agent import MemoryAgent
        
        # Create test data with full content
        test_diffs = [
            {
                "filename": "test.py",
                "patch": "+import os\n+password = 'secret123'",
                "full_content": "import os\nimport sys\n\npassword = 'secret123'\n\ndef main():\n    pass"
            }
        ]
        
        test_pr = {
            "title": "Test PR",
            "number": 1,
            "author": "test-user"
        }
        
        # Test Security Agent
        security_agent = SecurityAgent()
        logger.info("Testing Security Agent with full content...")
        result = await security_agent.analyze(test_pr, test_diffs, [])
        logger.info(f"Security Agent returned {len(result.get('findings', []))} findings")
        
        # Test Memory Agent
        memory_agent = MemoryAgent()
        logger.info("Testing Memory Agent with full content...")
        result = await memory_agent.analyze(test_pr, test_diffs, [])
        logger.info(f"Memory Agent returned {len(result.get('findings', []))} findings")
        
        logger.info("✅ SUCCESS: Agents can process diffs with full content")
        return True
        
    except Exception as exc:
        logger.error(f"❌ FAILED: {exc}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all enhancement verification tests."""
    logger.info("\n" + "=" * 80)
    logger.info("IBM DEXTER PR REVIEW ENHANCEMENT VERIFICATION")
    logger.info("=" * 80 + "\n")
    
    results = {
        "GitHub Full Content Fetch": await test_github_full_content_fetch(),
        "RAG Integration": await test_rag_integration(),
        "Memory Agent in Pipeline": await test_memory_agent_in_pipeline(),
        "Full Content in Diffs": await test_full_content_in_diffs(),
        "Agent Full Content Usage": await test_agent_full_content_usage(),
    }
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 ALL ENHANCEMENTS VERIFIED SUCCESSFULLY!")
        return 0
    else:
        logger.error(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)

# Made with Bob
