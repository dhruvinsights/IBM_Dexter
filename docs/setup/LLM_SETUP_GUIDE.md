# LLM Setup Guide for IBM Dexter

This guide covers setting up and configuring Large Language Models (LLMs) for IBM Dexter AI Code Reviewer.

## Table of Contents

1. [Quick Start (Ollama + Llama 3)](#quick-start-ollama--llama-3)
2. [IBM Watsonx Setup](#ibm-watsonx-setup)
3. [OpenAI Setup](#openai-setup)
4. [Anthropic Claude Setup](#anthropic-claude-setup)
5. [Cohere Setup](#cohere-setup)
6. [Configuration Reference](#configuration-reference)
7. [Testing Your Setup](#testing-your-setup)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## Quick Start (Ollama + Llama 3)

**Recommended for local development and testing.**

### Why Ollama + Llama 3?

- ✅ **Free and Open Source**: No API costs
- ✅ **Privacy**: Runs completely locally
- ✅ **Fast**: No network latency
- ✅ **Powerful**: Llama 3 is highly capable
- ✅ **Easy Setup**: Simple installation process

### Installation Steps

#### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/download)

**Verify Installation:**
```bash
ollama --version
```

#### 2. Pull Llama 3 Model

```bash
# Pull the default Llama 3 model (8B parameters)
ollama pull llama3

# Or pull the larger model for better performance (70B parameters)
ollama pull llama3:70b
```

#### 3. Test Ollama

```bash
# Start interactive chat
ollama run llama3

# Test with a simple prompt
ollama run llama3 "Explain what code review is in one sentence"
```

#### 4. Configure Dexter

Create or update `backend/.env`:

```bash
# Use Ollama as the LLM provider
DEXTER_LLM_PROVIDER=ollama

# Ollama configuration (defaults work for standard installation)
DEXTER_OLLAMA_BASE_URL=http://localhost:11434
DEXTER_OLLAMA_MODEL=llama3
```

#### 5. Start Dexter

```bash
cd backend
uvicorn main:app --reload
```

**That's it!** Dexter is now using Ollama + Llama 3 for AI-powered code reviews.

### Ollama Model Options

| Model | Size | Use Case |
|-------|------|----------|
| `llama3` | 8B | Default, fast, good quality |
| `llama3:70b` | 70B | Best quality, slower |
| `codellama` | 7B-34B | Specialized for code |
| `mistral` | 7B | Fast alternative |
| `mixtral` | 8x7B | High quality, efficient |

To switch models:
```bash
ollama pull codellama
```

Update `.env`:
```bash
DEXTER_OLLAMA_MODEL=codellama
```

---

## IBM Watsonx Setup

**Recommended for enterprise deployments.**

### Prerequisites

- IBM Cloud account
- Watsonx.ai service instance
- API key and project ID

### Setup Steps

#### 1. Create IBM Cloud Account

Visit [cloud.ibm.com](https://cloud.ibm.com/) and sign up.

#### 2. Create Watsonx.ai Instance

1. Navigate to **Catalog** → **AI / Machine Learning**
2. Select **watsonx.ai**
3. Choose your plan (Lite/Standard/Enterprise)
4. Click **Create**

#### 3. Get API Credentials

1. Go to **Manage** → **Access (IAM)**
2. Click **API keys** → **Create**
3. Copy your API key (save it securely!)

#### 4. Get Project ID

1. Open your Watsonx.ai instance
2. Navigate to **Projects**
3. Create or select a project
4. Copy the **Project ID** from project settings

#### 5. Configure Dexter

Update `backend/.env`:

```bash
# Use Watsonx as the LLM provider
DEXTER_LLM_PROVIDER=watsonx

# Watsonx configuration
DEXTER_WATSONX_API_KEY=your_api_key_here
DEXTER_WATSONX_PROJECT_ID=your_project_id_here
DEXTER_WATSONX_URL=https://us-south.ml.cloud.ibm.com
DEXTER_WATSONX_MODEL=ibm/granite-13b-chat-v2
```

#### 6. Test Connection

```bash
cd backend
python -c "from app.services.llm_service import get_llm_service; print(get_llm_service().get_provider_info())"
```

### Available Watsonx Models

| Model | Description | Best For |
|-------|-------------|----------|
| `ibm/granite-13b-chat-v2` | IBM's enterprise model | General purpose |
| `ibm/granite-20b-code` | Code-specialized | Code analysis |
| `meta-llama/llama-3-70b-instruct` | Llama 3 on Watsonx | High quality |
| `mistralai/mixtral-8x7b-instruct` | Mixtral | Balanced performance |

---

## OpenAI Setup

**Recommended for quick prototyping with GPT models.**

### Setup Steps

#### 1. Get API Key

1. Visit [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create new secret key**
5. Copy and save your key

#### 2. Configure Dexter

Update `backend/.env`:

```bash
# Use OpenAI as the LLM provider
DEXTER_LLM_PROVIDER=openai

# OpenAI configuration
DEXTER_OPENAI_API_KEY=sk-...your_key_here
DEXTER_OPENAI_MODEL=gpt-4o-mini
```

### Available OpenAI Models

| Model | Cost | Best For |
|-------|------|----------|
| `gpt-4o-mini` | Low | Fast, cost-effective |
| `gpt-4o` | Medium | Balanced quality/cost |
| `gpt-4-turbo` | High | Best quality |
| `gpt-3.5-turbo` | Lowest | Simple tasks |

---

## Anthropic Claude Setup

**Recommended for advanced reasoning and long context.**

### Setup Steps

#### 1. Get API Key

1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Create a new key
5. Copy and save your key

#### 2. Configure Dexter

Update `backend/.env`:

```bash
# Use Anthropic as the LLM provider
DEXTER_LLM_PROVIDER=anthropic

# Anthropic configuration
DEXTER_ANTHROPIC_API_KEY=sk-ant-...your_key_here
DEXTER_ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Available Claude Models

| Model | Context | Best For |
|-------|---------|----------|
| `claude-3-opus-20240229` | 200K | Highest quality |
| `claude-3-sonnet-20240229` | 200K | Balanced |
| `claude-3-haiku-20240307` | 200K | Fast, cost-effective |

---

## Cohere Setup

**Recommended for enterprise with RAG capabilities.**

### Setup Steps

#### 1. Get API Key

1. Visit [dashboard.cohere.com](https://dashboard.cohere.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Create a new key
5. Copy and save your key

#### 2. Configure Dexter

Update `backend/.env`:

```bash
# Use Cohere as the LLM provider
DEXTER_LLM_PROVIDER=cohere

# Cohere configuration
DEXTER_COHERE_API_KEY=your_key_here
DEXTER_COHERE_MODEL=command-r-plus
```

---

## Configuration Reference

### Environment Variables

All configuration uses the `DEXTER_` prefix:

```bash
# Primary provider selection
DEXTER_LLM_PROVIDER=ollama  # ollama, watsonx, openai, anthropic, cohere

# Generation settings (apply to all providers)
DEXTER_LLM_TEMPERATURE=0.7      # 0.0-1.0, higher = more creative
DEXTER_LLM_MAX_TOKENS=2000      # Maximum response length
DEXTER_LLM_TIMEOUT=60           # Request timeout in seconds
```

### Provider Priority

Dexter uses automatic fallback in this order:

1. **Configured Provider** (from `DEXTER_LLM_PROVIDER`)
2. **Ollama** (if available locally)
3. **Watsonx** (if API key configured)
4. **OpenAI** (if API key configured)
5. **Anthropic** (if API key configured)
6. **Cohere** (if API key configured)

---

## Testing Your Setup

### 1. Check Available Providers

```bash
cd backend
python -c "
from app.services.llm_factory import get_available_providers
import json
print(json.dumps(get_available_providers(), indent=2))
"
```

### 2. Test LLM Generation

```bash
python -c "
import asyncio
from app.services.llm_service import get_llm_service

async def test():
    llm = get_llm_service()
    response = await llm.generate('Explain code review in one sentence')
    print(f'Provider: {llm.provider_name}')
    print(f'Response: {response}')

asyncio.run(test())
"
```

### 3. Test Agent Integration

```bash
python -c "
from app.agents.security_agent import SecurityAgent

agent = SecurityAgent()
print(f'Agent: {agent.agent_name}')
print(f'LLM Provider: {agent.provider}')
print(agent.get_llm_info())
"
```

---

## Troubleshooting

### Ollama Issues

**Problem: "Connection refused" error**

```bash
# Check if Ollama is running
ollama list

# Start Ollama service (if not running)
ollama serve

# Check port availability
lsof -i :11434
```

**Problem: Model not found**

```bash
# List installed models
ollama list

# Pull the required model
ollama pull llama3
```

**Problem: Slow performance**

```bash
# Use smaller model
ollama pull llama3:8b

# Or use faster model
ollama pull mistral
```

### Watsonx Issues

**Problem: Authentication failed**

- Verify API key is correct
- Check project ID matches your Watsonx project
- Ensure API key has proper permissions

**Problem: Model not available**

- Check model name spelling
- Verify model is available in your region
- Try alternative model: `ibm/granite-13b-chat-v2`

### OpenAI Issues

**Problem: Rate limit exceeded**

- Reduce request frequency
- Upgrade to higher tier plan
- Use `gpt-3.5-turbo` for lower costs

**Problem: Invalid API key**

- Regenerate key from OpenAI dashboard
- Check for extra spaces in `.env` file
- Ensure key starts with `sk-`

### General Issues

**Problem: No providers available**

```bash
# Check configuration
cat backend/.env | grep LLM

# Verify at least one provider is configured
# For local testing, install Ollama
```

**Problem: Import errors**

```bash
# Install dependencies
cd backend
pip install -r requirements.txt
```

---

## Advanced Configuration

### Multiple Providers

Configure multiple providers for redundancy:

```bash
# Primary provider
DEXTER_LLM_PROVIDER=ollama

# Backup providers (configured with API keys)
DEXTER_WATSONX_API_KEY=your_key
DEXTER_OPENAI_API_KEY=your_key
```

Dexter will automatically fall back if primary fails.

### Custom Model Parameters

Override defaults per request:

```python
from app.services.llm_service import get_llm_service

llm = get_llm_service()
response = await llm.generate(
    prompt="Analyze this code",
    temperature=0.3,  # More focused
    max_tokens=1000   # Shorter response
)
```

### Switching Providers at Runtime

```python
from app.services.llm_service import get_llm_service

llm = get_llm_service()

# Switch to different provider
llm.switch_provider("watsonx")

# Generate with new provider
response = await llm.generate("Your prompt")
```

### Provider-Specific Settings

#### Ollama Advanced

```bash
# Use custom Ollama server
DEXTER_OLLAMA_BASE_URL=http://remote-server:11434

# Use specific model version
DEXTER_OLLAMA_MODEL=llama3:70b-instruct-q4_0
```

#### Watsonx Advanced

```bash
# Use different region
DEXTER_WATSONX_URL=https://eu-gb.ml.cloud.ibm.com

# Use specific model version
DEXTER_WATSONX_MODEL=meta-llama/llama-3-70b-instruct
```

---

## Performance Optimization

### Local Development

**Best Setup:**
- Provider: Ollama
- Model: `llama3` or `mistral`
- Temperature: 0.7
- Max Tokens: 1500

### Production (Cost-Optimized)

**Best Setup:**
- Provider: Watsonx or OpenAI
- Model: `granite-13b-chat-v2` or `gpt-4o-mini`
- Temperature: 0.5
- Max Tokens: 2000

### Production (Quality-Optimized)

**Best Setup:**
- Provider: Watsonx or Anthropic
- Model: `llama-3-70b-instruct` or `claude-3-opus`
- Temperature: 0.7
- Max Tokens: 3000

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate API keys** regularly
4. **Use separate keys** for dev/staging/production
5. **Monitor API usage** to detect anomalies
6. **Set spending limits** on paid providers
7. **Use Ollama** for sensitive code (stays local)

---

## Cost Estimation

### Ollama (Local)
- **Cost:** $0 (free)
- **Hardware:** 8GB+ RAM recommended
- **Best for:** Development, testing, privacy-sensitive

### Watsonx
- **Cost:** Pay-per-use or subscription
- **Pricing:** ~$0.001-0.01 per 1K tokens
- **Best for:** Enterprise, compliance-required

### OpenAI
- **GPT-4o-mini:** ~$0.15 per 1M input tokens
- **GPT-4o:** ~$5 per 1M input tokens
- **Best for:** Prototyping, high quality

### Anthropic
- **Claude 3 Haiku:** ~$0.25 per 1M input tokens
- **Claude 3 Sonnet:** ~$3 per 1M input tokens
- **Best for:** Long context, reasoning

---

## Next Steps

1. ✅ Choose and configure your LLM provider
2. ✅ Test the setup using the commands above
3. ✅ Run a code review to see it in action
4. ✅ Adjust temperature/tokens for your needs
5. ✅ Set up monitoring and alerts

For more help, see:
- [Main README](../../README.md)
- [Architecture Documentation](../architecture/)
- [API Documentation](../api/)

---

**Made with Bob** 🤖