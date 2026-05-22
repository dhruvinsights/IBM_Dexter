# Hybrid LLM Provider System Implementation

## Overview

Successfully implemented a hybrid LLM provider system that allows users to choose between:
- **Free Tier**: Client-side Ollama (local, no backend API calls, zero hosting costs)
- **Paid Tier**: Server-side cloud providers (OpenAI, Watsonx, Anthropic)

## Architecture

### Frontend (Client-Side)

#### 1. Direct Ollama Integration
**File**: `frontend/src/services/ollamaService.js`
- Direct HTTP calls to `http://localhost:11434`
- No backend API involvement for Ollama
- Methods: `chat()`, `generate()`, `listModels()`, `checkConnection()`, `pullModel()`

#### 2. Unified LLM Service
**File**: `frontend/src/services/llmService.js`
- Routes requests to Ollama (client-side) or backend (cloud providers)
- Provider metadata and configuration
- Automatic provider detection and routing
- Methods: `chat()`, `reviewCode()`, `listModels()`, `checkConnection()`

#### 3. State Management
**File**: `frontend/src/store/useLLMStore.js`
- Zustand store for LLM settings persistence
- Provider selection, model configuration
- Connection status tracking
- Auto-check for Ollama connection (every 30 seconds)
- Usage statistics tracking

#### 4. UI Components

**Ollama Settings** (`frontend/src/components/settings/OllamaSettings.jsx`)
- Connection status indicator
- Model selection dropdown
- Test connection button
- Installation guide link
- Available models list

**Cloud Provider Settings** (`frontend/src/components/settings/CloudProviderSettings.jsx`)
- API key configuration (encrypted)
- Model selection
- Usage statistics
- Provider-specific instructions

**Ollama Status Indicator** (`frontend/src/components/ui/OllamaStatus.jsx`)
- Header status badge
- Auto-check connection
- Click to open settings
- Visual connection states (connected/disconnected/checking)

#### 5. Settings Page Integration
**File**: `frontend/src/pages/Settings/Settings.jsx`
- Added LLM Provider Selection section
- Radio button group for provider selection
- Dynamic settings based on selected provider
- Integrated with existing settings tabs

#### 6. Setup Guide
**File**: `frontend/src/pages/OllamaSetup/OllamaSetup.jsx`
- Step-by-step Ollama installation
- Platform-specific instructions (Mac/Windows/Linux)
- Model recommendations
- Troubleshooting guide
- Quick start commands

### Backend (Server-Side)

#### 1. Configuration Updates
**File**: `backend/app/core/config.py`
- Added `default_llm_provider: str = "ollama"` (default to free tier)
- Added `allow_client_ollama: bool = True` (enable frontend Ollama calls)
- Changed default from "watsonx" to "ollama" for new installations

#### 2. LLM Service Enhancements
**File**: `backend/app/services/llm_service.py`

Added three new methods to `LLMService` class:

```python
def is_server_side_provider(self, provider: str) -> bool:
    """Check if provider requires backend processing"""
    return provider.lower() != "ollama"

def validate_provider_access(self, provider: str, user_tier: str = "free") -> bool:
    """Validate user access to provider based on tier"""
    if provider == "ollama":
        return True  # Always allowed
    return user_tier in ["paid", "enterprise"]  # Cloud providers

def get_provider_tier(self, provider: str) -> str:
    """Get tier requirement for provider"""
    # Returns: "free", "paid", or "enterprise"
```

## Provider Comparison

| Provider | Tier | Location | API Key | Cost | Installation |
|----------|------|----------|---------|------|--------------|
| **Ollama** | Free | Client-side | No | $0 | Required |
| **OpenAI** | Paid | Server-side | Yes | Per usage | No |
| **Watsonx** | Enterprise | Server-side | Yes | Per usage | No |
| **Anthropic** | Paid | Server-side | Yes | Per usage | No |

## Data Flow

### Free Tier (Ollama)
```
User → Frontend → Ollama (localhost:11434) → Response
```
- No backend involvement
- Data never leaves user's machine
- Zero hosting costs

### Paid Tier (Cloud Providers)
```
User → Frontend → Backend API → Cloud Provider → Backend → Frontend → User
```
- Backend handles API keys securely
- Usage tracking and billing
- No local installation needed

## Files Created/Modified

### Frontend Files Created (8 files)
1. `frontend/src/services/ollamaService.js` - Direct Ollama API client
2. `frontend/src/services/llmService.js` - Unified LLM routing service
3. `frontend/src/store/useLLMStore.js` - State management
4. `frontend/src/components/settings/OllamaSettings.jsx` - Ollama config UI
5. `frontend/src/components/settings/OllamaSettings.scss` - Ollama styles
6. `frontend/src/components/settings/CloudProviderSettings.jsx` - Cloud config UI
7. `frontend/src/components/settings/CloudProviderSettings.scss` - Cloud styles
8. `frontend/src/components/ui/OllamaStatus.jsx` - Status indicator
9. `frontend/src/components/ui/OllamaStatus.scss` - Status styles
10. `frontend/src/pages/OllamaSetup/OllamaSetup.jsx` - Setup guide
11. `frontend/src/pages/OllamaSetup/OllamaSetup.scss` - Setup styles

### Frontend Files Modified (1 file)
1. `frontend/src/pages/Settings/Settings.jsx` - Added provider selection

### Backend Files Modified (2 files)
1. `backend/app/core/config.py` - Added hybrid mode settings
2. `backend/app/services/llm_service.py` - Added provider validation

## Configuration

### Environment Variables

```bash
# Default provider (free tier)
DEXTER_DEFAULT_LLM_PROVIDER=ollama
DEXTER_ALLOW_CLIENT_OLLAMA=true

# Ollama configuration
DEXTER_OLLAMA_BASE_URL=http://localhost:11434
DEXTER_OLLAMA_MODEL=llama2

# Cloud providers (optional)
DEXTER_OPENAI_API_KEY=sk-...
DEXTER_WATSONX_API_KEY=...
DEXTER_ANTHROPIC_API_KEY=...
```

## User Experience

### First-Time Setup (Free Tier)
1. User opens Dexter
2. Default provider is Ollama (free)
3. If Ollama not installed, see setup guide
4. Install Ollama → Pull model → Start using

### Upgrading to Paid Tier
1. Go to Settings → AI Configuration
2. Select cloud provider (OpenAI/Watsonx/Anthropic)
3. Enter API key
4. Select model
5. Start using immediately

## Testing Instructions

### Test with Local Ollama

1. **Install Ollama**:
   ```bash
   # Mac
   brew install ollama
   
   # Or download from https://ollama.ai/download
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Pull a model**:
   ```bash
   ollama pull llama2
   # or
   ollama pull codellama  # Better for code review
   ```

4. **Start Dexter Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

5. **Test Connection**:
   - Open http://localhost:3000
   - Go to Settings → AI Configuration
   - Should see "Ollama" selected by default
   - Connection status should show "Connected"
   - Model dropdown should list available models

6. **Test Code Review**:
   - Create a test pull request
   - Trigger code review
   - Should use local Ollama (check network tab - no backend API calls)

### Test Provider Switching

1. **Switch to OpenAI**:
   - Go to Settings → AI Configuration
   - Select "OpenAI (Paid)"
   - Enter API key
   - Select model (e.g., gpt-4)
   - Test connection

2. **Verify Backend Routing**:
   - Trigger code review
   - Check network tab - should call backend API
   - Backend should route to OpenAI

## Benefits

### For Users
- **Free Option**: No costs, complete privacy, works offline
- **Flexibility**: Easy switching between providers
- **No Lock-in**: Can use any provider at any time
- **Privacy**: Ollama keeps data local

### For Dexter
- **Lower Costs**: Free tier users don't consume backend resources
- **Scalability**: Ollama users scale independently
- **Revenue**: Paid tiers for cloud providers
- **Adoption**: Free tier lowers barrier to entry

## Security Considerations

1. **API Keys**: Cloud provider keys stored server-side only
2. **Local Data**: Ollama data never leaves user's machine
3. **CORS**: Frontend can only call localhost:11434 for Ollama
4. **Validation**: Backend validates provider access based on user tier

## Future Enhancements

1. **Desktop App**: Package Ollama with Electron app
2. **Model Management**: UI for pulling/deleting Ollama models
3. **Usage Analytics**: Track token usage per provider
4. **Cost Estimation**: Show estimated costs for cloud providers
5. **Hybrid Mode**: Use Ollama for embeddings, cloud for chat
6. **Model Comparison**: Side-by-side comparison of provider outputs

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check port 11434 is not blocked
- Verify model is downloaded: `ollama list`

### Cloud Provider Issues
- Verify API key is correct
- Check API key has sufficient credits
- Ensure network connectivity to provider

## Documentation Links

- Ollama: https://ollama.ai
- OpenAI: https://platform.openai.com
- IBM Watsonx: https://www.ibm.com/watsonx
- Anthropic: https://www.anthropic.com

---

**Implementation Status**: ✅ Complete
**Date**: 2026-05-22
**Version**: 1.0.0