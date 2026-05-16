#!/usr/bin/env python3
"""
IBM Dexter Installation Test Script
Tests all critical imports and configurations
"""

import sys
from typing import Optional, Tuple


def test_import(module_name: str, package_name: Optional[str] = None) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        return True, f"✅ {package_name or module_name}"
    except ImportError as e:
        return False, f"❌ {package_name or module_name}: {str(e)}"


def main():
    print("🧪 IBM Dexter Installation Test")
    print("=" * 50)
    print()

    # Core dependencies
    print("📦 Testing Core Dependencies:")
    core_tests = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("dotenv", "python-dotenv"),
    ]

    core_results = []
    for module, name in core_tests:
        success, message = test_import(module, name)
        print(f"   {message}")
        core_results.append(success)
    print()

    # LangChain dependencies
    print("🤖 Testing LangChain:")
    langchain_tests = [
        ("langchain", "LangChain"),
        ("langchain_core", "LangChain Core"),
        ("langchain_community", "LangChain Community"),
    ]

    langchain_results = []
    for module, name in langchain_tests:
        success, message = test_import(module, name)
        print(f"   {message}")
        langchain_results.append(success)
    print()

    # LLM providers
    print("🧠 Testing LLM Providers:")
    llm_tests = [
        ("ollama", "Ollama"),
    ]

    llm_results = []
    for module, name in llm_tests:
        success, message = test_import(module, name)
        print(f"   {message}")
        llm_results.append(success)
    print()

    # Optional dependencies
    print("🔧 Testing Optional Dependencies:")
    optional_tests = [
        ("github", "PyGithub"),
        ("gitlab", "python-gitlab"),
        ("jose", "python-jose"),
        ("passlib", "passlib"),
    ]

    optional_results = []
    for module, name in optional_tests:
        success, message = test_import(module, name)
        print(f"   {message}")
        optional_results.append(success)
    print()

    # Summary
    print("=" * 50)
    print("📊 Test Summary:")
    print(f"   Core: {sum(core_results)}/{len(core_results)} passed")
    print(f"   LangChain: {sum(langchain_results)}/{len(langchain_results)} passed")
    print(f"   LLM: {sum(llm_results)}/{len(llm_results)} passed")
    print(f"   Optional: {sum(optional_results)}/{len(optional_results)} passed")
    print()

    all_results = core_results + langchain_results + llm_results + optional_results
    if all(all_results):
        print("🎉 All tests passed!")
        print("✅ Installation is complete and working")
        return 0
    else:
        print("⚠️  Some tests failed")
        print("❌ Please check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
