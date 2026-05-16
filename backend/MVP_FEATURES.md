# IBM Dexter MVP - PR Review Bot

## 🎯 MVP Goal
A GitHub bot that automatically reviews pull requests using AI, providing:
- Code quality suggestions
- Company knowledge context
- Architecture compliance checks
- Security recommendations

## ✅ MVP Features (Phase 1)

### 1. GitHub Integration
- ✅ Webhook listener for PR events
- ✅ Automatic PR comment posting
- ✅ Dexter bot identity with logo
- ✅ GitHub App authentication

### 2. AI Code Review
- ✅ Ollama + Llama 3 integration
- ✅ Code analysis and suggestions
- ✅ Severity levels (Critical, High, Medium, Low)
- ✅ Inline code comments

### 3. Company Knowledge (RAG)
- ✅ Vector database (IBM Db2 via `langchain-db2`)
- ✅ Company docs ingestion
- ✅ Architecture patterns retrieval
- ✅ Context-aware suggestions

### 4. Architecture Review
- ✅ Pattern matching
- ✅ Best practices validation
- ✅ Dependency analysis
- ✅ API contract checks

### 5. Bot Branding
- ✅ Dexter logo in PR comments
- ✅ Consistent formatting
- ✅ Professional tone
- ✅ IBM branding

## 🚫 NOT in MVP (Future Phases)

### Phase 2 (Later)
- ❌ Dashboard UI (use GitHub for now)
- ❌ Multiple LLM providers (Ollama only for MVP)
- ❌ GitLab support (GitHub only for MVP)
- ❌ Advanced analytics
- ❌ Team management
- ❌ Custom rules engine

### Phase 3 (Future)
- ❌ IDE integration
- ❌ Slack/Teams notifications
- ❌ Auto-fix suggestions
- ❌ Performance benchmarking
- ❌ Multi-language support

## 📦 MVP Tech Stack

### Backend (Minimal)
- FastAPI (API server)
- Ollama + Llama 3 (AI)
- IBM Db2 vector store (via `langchain-db2`)
- PyGithub (GitHub API)
- SQLite (application database)

### No Frontend Needed for MVP
- Use GitHub UI for viewing reviews
- Bot posts comments directly on PRs
- No separate dashboard needed initially

## 🚀 MVP Workflow

1. Developer creates PR on GitHub
2. GitHub webhook triggers Dexter
3. Dexter analyzes code with AI
4. Dexter retrieves company knowledge
5. Dexter posts review comment with logo
6. Developer sees Dexter's suggestions in PR

## 📝 MVP Requirements File

Create `backend/requirements-mvp.txt` with only essentials:
- fastapi
- uvicorn
- ollama
- langchain-db2 (IBM Db2 vector store)
- ibm-db / ibm-db-sa (Db2 drivers)
- PyGithub
- langchain-core
- python-dotenv
- pydantic
- email-validator

## 🎨 Dexter Bot Identity

### GitHub Bot Setup
1. Create GitHub App
2. Upload dexter.png as app avatar
3. Set bot name: "Dexter AI Reviewer"
4. Set description: "IBM's AI-powered code review assistant"

### PR Comment Format
```markdown
![Dexter](https://your-url/dexter.png)

## 🤖 Dexter AI Review

### Summary
[AI-generated summary]

### Findings

#### 🔴 Critical Issues (0)
[None found]

#### 🟡 Suggestions (3)
1. **Line 45**: Consider using async/await for better performance
2. **Line 67**: This pattern doesn't match our architecture guidelines
3. **Line 89**: Add error handling for edge cases

### Company Knowledge
Based on our architecture docs, this change aligns with our microservices pattern.

---
*Powered by IBM Watsonx & Ollama | [Learn More](link)*
```

## 🎯 MVP Success Criteria

✅ Bot successfully comments on PRs
✅ AI provides relevant code suggestions
✅ Company knowledge is incorporated
✅ Dexter logo appears in comments
✅ Setup takes < 10 minutes
✅ Works with Ollama locally

## 📋 MVP Setup Steps

1. Install minimal dependencies
2. Configure GitHub webhook
3. Add company docs to vector DB
4. Upload Dexter logo
5. Test on sample PR
6. Deploy (optional - can run locally)

## 🔧 Technical Implementation

### Core Components

#### 1. Webhook Handler (`app/api/v1/endpoints/webhooks.py`)
- Receives GitHub PR events
- Validates webhook signatures
- Triggers review process

#### 2. GitHub Service (`app/services/github_service.py`)
- Fetches PR details
- Posts review comments
- Manages GitHub API interactions

#### 3. AI Service (`app/services/ai_service.py`)
- Integrates with Ollama
- Generates code review suggestions
- Formats review output

#### 4. RAG Pipeline (`app/rag/`)
- IBM Db2 vector store (via `langchain-db2`)
- Document ingestion
- Context retrieval for reviews

#### 5. Review Orchestration
- Coordinates all services
- Combines AI + RAG insights
- Formats final review comment

## 📊 MVP Metrics

Track these metrics to measure success:
- Number of PRs reviewed
- Average review time
- Suggestion acceptance rate
- False positive rate
- User satisfaction

## 🚀 Next Steps After MVP

1. Gather user feedback
2. Improve AI prompts based on feedback
3. Add more company knowledge
4. Optimize performance
5. Plan Phase 2 features

## 📚 Documentation

- `MVP_SETUP.md` - Quick setup guide
- `requirements-mvp.txt` - Minimal dependencies
- `README.md` - Full documentation
- `TESTING.md` - Testing guide

## 🤝 Contributing

For MVP, focus on:
1. Core review functionality
2. GitHub integration stability
3. AI prompt optimization
4. Documentation improvements

Avoid scope creep - save advanced features for Phase 2!