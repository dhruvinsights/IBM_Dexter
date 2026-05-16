# IBM Dexter AI Code Reviewer 🤖

> An intelligent, multi-agent AI-powered code review system with RAG capabilities, built with IBM Carbon Design System and Next.js 14.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![IBM Carbon](https://img.shields.io/badge/IBM-Carbon-blue)](https://carbondesignsystem.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)

## 🌟 Overview

IBM Dexter is an advanced AI code reviewer that leverages multiple specialized AI agents to provide comprehensive, context-aware code analysis. Using Retrieval-Augmented Generation (RAG) and IBM's Carbon Design System, it delivers professional-grade code reviews with actionable insights.

### Key Features

- 🤖 **Multi-Agent AI System**: Specialized agents for security, performance, style, and best practices
- 🔍 **RAG Pipeline**: Context-aware reviews using semantic search and vector embeddings
- 📊 **IBM Carbon UI**: Professional, accessible interface following IBM design standards
- 📄 **PDF Reports**: Generate comprehensive review reports with visualizations
- ⚡ **Real-time Streaming**: Live feedback as agents analyze your code
- 🔒 **Enterprise-Ready**: Built with security and scalability in mind

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.9+ (for skill auto-loader)
- API keys for LLM providers (OpenAI, Anthropic, etc.)
- Vector database (Pinecone, Chroma, or similar)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ibm-dexter-ai-code-reviewer.git
cd ibm-dexter-ai-code-reviewer

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API keys

# Run development server
npm run dev
```

Visit `http://localhost:3000` to see the application.

---

## 🧠 LLM Configuration

IBM Dexter supports multiple LLM providers with automatic fallback. **Ollama + Llama 3 is recommended for local testing.**

### Quick Start (Ollama + Llama 3)

**Best for local development - Free, fast, and private!**

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull Llama 3 model
ollama pull llama3

# 3. Configure Dexter (backend/.env)
DEXTER_LLM_PROVIDER=ollama
DEXTER_OLLAMA_BASE_URL=http://localhost:11434
DEXTER_OLLAMA_MODEL=llama3

# 4. Start Dexter
cd backend
uvicorn main:app --reload
```

**That's it!** Dexter will use Ollama for AI-powered code reviews.

### IBM Watsonx Setup

**Recommended for enterprise deployments.**

```bash
# 1. Get credentials from IBM Cloud
# Visit: https://cloud.ibm.com/

# 2. Configure Dexter (backend/.env)
DEXTER_LLM_PROVIDER=watsonx
DEXTER_WATSONX_API_KEY=your_api_key_here
DEXTER_WATSONX_PROJECT_ID=your_project_id_here
DEXTER_WATSONX_URL=https://us-south.ml.cloud.ibm.com
DEXTER_WATSONX_MODEL=ibm/granite-13b-chat-v2
```

### Custom LLM (OpenAI, Anthropic, etc.)

**Add any LLM with API keys.**

```bash
# OpenAI
DEXTER_LLM_PROVIDER=openai
DEXTER_OPENAI_API_KEY=sk-...

# Anthropic Claude
DEXTER_LLM_PROVIDER=anthropic
DEXTER_ANTHROPIC_API_KEY=sk-ant-...

# Cohere
DEXTER_LLM_PROVIDER=cohere
DEXTER_COHERE_API_KEY=...
```

### Supported Providers

| Provider | Cost | Best For | Setup Time |
|----------|------|----------|------------|
| **Ollama** | Free | Local testing, privacy | 2 minutes |
| **Watsonx** | Pay-per-use | Enterprise, compliance | 5 minutes |
| **OpenAI** | Pay-per-use | Quick prototyping | 2 minutes |
| **Anthropic** | Pay-per-use | Long context, reasoning | 2 minutes |
| **Cohere** | Pay-per-use | Enterprise RAG | 2 minutes |

### Automatic Fallback

Dexter automatically falls back to available providers:
1. Configured provider (from `DEXTER_LLM_PROVIDER`)
2. Ollama (if running locally)
3. Watsonx (if API key configured)
4. OpenAI, Anthropic, Cohere (if API keys configured)

📖 **Full Setup Guide**: [docs/setup/LLM_SETUP_GUIDE.md](docs/setup/LLM_SETUP_GUIDE.md)

---

### Using BOB AI Skill Auto-Loader

```bash
# List all available skills
python .bob/config/auto-loader.py list

# Analyze a prompt to see recommended skills
python .bob/config/auto-loader.py analyze "I need to add PDF generation"

# Load skills for a specific task
python .bob/config/auto-loader.py load "implement RAG pipeline with vector search"

# View usage statistics
python .bob/config/auto-loader.py stats
```

---

## 📁 Project Structure

```
IBM Dexter_AI_Code_Reviewer/
├── .bob/                          # BOB AI configuration
│   └── config/
│       ├── skill-loader.json      # Skill mapping and triggers
│       └── auto-loader.py         # Intelligent skill loader
├── docs/                          # Documentation
│   ├── architecture/              # Architecture documents
│   │   └── IBM_DEXTER_ARCHITECTURE_PLAN.md
│   └── planning/                  # Planning documents
│       ├── IBM_DEXTER_PROJECT_SUMMARY.md
│       ├── ibm_dexter_bob_ai_project_context.md
│       └── ONE_DAY_SPRINT_PLAN.md
├── skills/                        # BOB AI Skills
│   ├── core/                      # Core functionality skills
│   │   ├── ibm-dexter-pdf-documentation.skill
│   │   ├── ibm-carbon-design-integration.skill
│   │   ├── ibm-dexter-multi-agent-ai.skill
│   │   └── ibm-dexter-rag-pipeline.skill
│   ├── integration/               # Integration skills
│   │   └── ibm-dexter-bob-integration.skill
│   └── testing/                   # Testing skills
│       └── ibm-dexter-testing-coverage.skill
├── src/                           # Source code (to be created)
│   ├── app/                       # Next.js 14 app directory
│   ├── components/                # React components
│   ├── lib/                       # Utility libraries
│   └── agents/                    # AI agent implementations
└── README.md                      # This file
```

### Folder Descriptions

- **`.bob/`**: BOB AI assistant configuration and skill auto-loader
- **`docs/`**: All project documentation, architecture plans, and sprint plans
- **`skills/`**: Modular BOB AI skills for different functionalities
  - `core/`: Essential features (PDF, Carbon Design, Multi-Agent AI, RAG)
  - `integration/`: Integration-specific skills
  - `testing/`: Testing and quality assurance skills
- **`src/`**: Application source code (Next.js 14 app)

---

## 🤖 BOB AI Skill Auto-Loader

The skill auto-loader intelligently loads relevant BOB AI skills based on your prompts and context.

### How It Works

1. **Prompt Analysis**: Analyzes your input for keywords and patterns
2. **Skill Matching**: Maps keywords to relevant skills using regex triggers
3. **Auto-Loading**: Automatically loads matched skills into BOB AI context
4. **Usage Tracking**: Logs skill usage for analytics and optimization

### Configuration

Edit `.bob/config/skill-loader.json` to customize:

```json
{
  "auto_load": true,
  "skill_directories": ["skills/core", "skills/integration", "skills/testing"],
  "prompt_triggers": {
    "pdf|report|documentation": ["pdf_generation"],
    "ui|design|carbon|frontend": ["carbon_design"],
    "test|coverage|quality": ["testing_coverage"],
    "agent|ai|llm|review": ["multi_agent_ai"],
    "rag|retrieval|search|context": ["rag_pipeline"],
    "bob|integration|api": ["bob_integration"]
  }
}
```

### Skill Descriptions

| Skill | Purpose | Trigger Keywords |
|-------|---------|------------------|
| `pdf_generation` | Generate PDF reports | pdf, report, documentation |
| `carbon_design` | IBM Carbon Design integration | ui, design, carbon, frontend |
| `testing_coverage` | Testing and QA | test, coverage, quality |
| `multi_agent_ai` | Multi-agent AI system | agent, ai, llm, review |
| `rag_pipeline` | RAG implementation | rag, retrieval, search, context |
| `bob_integration` | BOB AI integration | bob, integration, api |

---

## 📅 1-Day Development Timeline

We've created an aggressive but achievable 1-day sprint plan to build the MVP. See [ONE_DAY_SPRINT_PLAN.md](docs/planning/ONE_DAY_SPRINT_PLAN.md) for details.

### Sprint Highlights

- **Hour 1-2**: Foundation, setup, and UI components
- **Hour 3-4**: Multi-agent AI and RAG pipeline
- **Hour 5-6**: API integration and testing
- **Hour 7-8**: PDF generation and final polish

### Success Criteria

- ✅ Working code review system
- ✅ Multi-agent AI operational
- ✅ RAG pipeline functional
- ✅ Professional UI with IBM Carbon
- ✅ PDF report generation
- ✅ 80%+ test coverage

---

## 🏗️ Architecture

### Multi-Agent AI System

```
User Input → Orchestrator Agent
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Security    Performance   Style
 Agent        Agent       Agent
    ↓           ↓           ↓
    └───────────┼───────────┘
                ↓
         Aggregator Agent
                ↓
         Review Results
```

### RAG Pipeline

```
Code Input → Embedding → Vector DB
                            ↓
User Query → Semantic Search → Context Retrieval
                                      ↓
                              Enhanced AI Review
```

For detailed architecture, see [IBM_DEXTER_ARCHITECTURE_PLAN.md](docs/architecture/IBM_DEXTER_ARCHITECTURE_PLAN.md).

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: IBM Carbon Design System
- **Language**: TypeScript
- **Styling**: Carbon Components + Tailwind CSS

### Backend
- **Runtime**: Node.js
- **API**: Next.js API Routes
- **AI Framework**: LangChain / LangGraph
- **Vector DB**: Pinecone / Chroma

### AI/ML
- **LLMs**: Ollama (Llama 3), IBM Watsonx, OpenAI, Anthropic, Cohere
- **Primary**: Ollama + Llama 3 (local, free)
- **Enterprise**: IBM Watsonx (Granite models)
- **Embeddings**: OpenAI text-embedding-3
- **Orchestration**: LangGraph for multi-agent coordination
- **Framework**: LangChain with custom provider support

### DevOps
- **Version Control**: Git
- **CI/CD**: GitHub Actions
- **Testing**: Jest, React Testing Library, Playwright
- **Deployment**: Vercel / AWS

---

## 📖 Documentation

- [Architecture Plan](docs/architecture/IBM_DEXTER_ARCHITECTURE_PLAN.md)
- [Project Summary](docs/planning/IBM_DEXTER_PROJECT_SUMMARY.md)
- [BOB AI Context](docs/planning/ibm_dexter_bob_ai_project_context.md)
- [1-Day Sprint Plan](docs/planning/ONE_DAY_SPRINT_PLAN.md)

---

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run linting
npm run lint
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

1. Use BOB AI skill auto-loader for context-aware assistance
2. Follow IBM Carbon Design guidelines
3. Write tests for new features
4. Update documentation
5. Ensure all tests pass before submitting PR

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IBM Carbon Design System** for the excellent UI components
- **LangChain** for the AI orchestration framework
- **OpenAI & Anthropic** for powerful LLM APIs
- **BOB AI** for intelligent development assistance

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/ibm-dexter-ai-code-reviewer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/ibm-dexter-ai-code-reviewer/discussions)
- **Email**: support@your-org.com

---

## 🗺️ Roadmap

### Phase 1 (Current - MVP)
- [x] Project structure and setup
- [ ] Multi-agent AI system
- [ ] RAG pipeline
- [ ] IBM Carbon UI
- [ ] PDF report generation

### Phase 2 (Next Sprint)
- [ ] User authentication
- [ ] Code history tracking
- [ ] Advanced analytics
- [ ] Multi-language support

### Phase 3 (Future)
- [ ] Team collaboration features
- [ ] Custom agent training
- [ ] Integration with GitHub/GitLab
- [ ] Enterprise SSO

---

**Built with ❤️ using BOB AI and IBM Carbon Design System**

*Last Updated: 2026-05-15*