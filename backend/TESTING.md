# Testing IBM Dexter Backend

## Quick Test

Run the automated setup and test:

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

This will:
1. Clean up old installation
2. Create fresh virtual environment
3. Install minimal requirements (2-3 minutes)
4. Test all imports
5. Verify installation

## Manual Testing

### 1. Test Installation
```bash
source venv/bin/activate
python3 test_installation.py
```

### 2. Test Server Start
```bash
./start.sh
```

### 3. Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

## Expected Results

### Setup Script Output
```text
🚀 IBM Dexter Backend Setup
================================

📦 Step 1: Cleaning up old installation...
   ✅ Old venv removed

🐍 Step 2: Creating fresh virtual environment...
   ✅ Virtual environment created

⚡ Step 3: Activating virtual environment...
   ✅ Virtual environment activated

📦 Step 4: Upgrading pip...
   ✅ Pip upgraded

📥 Step 5: Installing minimal requirements...
   This should take 2-3 minutes...
   ✅ Requirements installed

⚙️  Step 6: Configuring environment...
   ✅ .env file created

🧪 Step 7: Testing installation...
   ✅ FastAPI imported
   ✅ SQLAlchemy imported
   ✅ LangChain imported
   ✅ Ollama imported
   ✅ All core imports successful

📄 Step 8: Checking application files...
   ✅ main.py found

🎉 Setup Complete!
```

### Test Script Output
```text
🧪 IBM Dexter Installation Test
==================================================

📦 Testing Core Dependencies:
   ✅ FastAPI
   ✅ Uvicorn
   ✅ SQLAlchemy
   ✅ Pydantic
   ✅ python-dotenv

🤖 Testing LangChain:
   ✅ LangChain
   ✅ LangChain Core
   ✅ LangChain Community

🧠 Testing LLM Providers:
   ✅ Ollama

🔧 Testing Optional Dependencies:
   ✅ PyGithub
   ✅ python-gitlab
   ✅ python-jose
   ✅ passlib

==================================================
📊 Test Summary:
   Core: 5/5 passed
   LangChain: 3/3 passed
   LLM: 1/1 passed
   Optional: 4/4 passed

🎉 All tests passed!
✅ Installation is complete and working
```

## Troubleshooting

### Issue: setup.sh permission denied
```bash
chmod +x setup.sh
./setup.sh
```

### Issue: Python not found
```bash
# Try python instead of python3
python -m venv venv
```

### Issue: pip install fails
```bash
# Upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Port 8000 already in use
```bash
# Use different port
python3 -m uvicorn main:app --reload --port 8001