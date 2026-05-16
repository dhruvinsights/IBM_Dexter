#!/usr/bin/env python3
"""Test all critical imports for IBM Dexter"""

import sys

def test_imports():
    """Test that all required packages can be imported"""
    
    tests = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("aiosqlite", "aiosqlite"),  # CRITICAL - async SQLite
        ("greenlet", "greenlet"),  # CRITICAL - SQLAlchemy async
        ("pydantic", "Pydantic"),
        ("email_validator", "email-validator"),  # CRITICAL - pydantic EmailStr
        ("langchain", "LangChain"),
        ("langchain_core", "LangChain Core"),
        ("langchain_community", "LangChain Community"),
        ("ollama", "Ollama"),
        ("langchain_db2", "LangChain Db2 (IBM Db2 vector store)"),
        ("ibm_db", "ibm-db (IBM Db2 CLI driver)"),
        ("github", "PyGithub"),
        ("gitlab", "python-gitlab"),
        ("jose", "python-jose"),
        ("passlib", "passlib"),
        ("httpx", "httpx"),
        ("aiohttp", "aiohttp"),
        ("dotenv", "python-dotenv"),
        ("alembic", "Alembic"),
        ("multipart", "python-multipart"),
    ]
    
    print("=" * 70)
    print("IBM DEXTER - DEPENDENCY CHECK")
    print("=" * 70)
    print()
    
    failed = []
    passed = 0
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name:30s} OK")
            passed += 1
        except ImportError as e:
            print(f"❌ {name:30s} FAILED: {e}")
            failed.append((name, str(e)))
    
    print()
    print("=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} packages imported successfully")
    print("=" * 70)
    
    if failed:
        print()
        print("❌ FAILED IMPORTS:")
        for name, error in failed:
            print(f"   • {name}: {error}")
        print()
        print("🔧 FIX: Run the following command:")
        print("   pip install -r requirements.txt")
        print()
        print("   Or use the quick fix script:")
        print("   ./fix_deps.sh")
        print()
        return 1
    else:
        print()
        print("✅ All dependencies installed correctly!")
        print()
        print("🚀 You can now start the server:")
        print("   ./start.sh")
        print()
        return 0

if __name__ == "__main__":
    sys.exit(test_imports())

# Made with Bob
