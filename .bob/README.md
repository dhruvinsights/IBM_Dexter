# Bob AI Configuration

This directory contains Bob AI configuration and skill definitions for the IBM Dexter AI Code Reviewer project.

## 📁 Directory Structure

```
.bob/
├── config/
│   ├── skill-loader.json    # Skill auto-loading configuration
│   └── auto-loader.py        # Intelligent skill loader script
└── README.md                 # This file
```

## 🎯 Purpose

The `.bob` directory enables:
1. **Skill Auto-Loading** - Automatically load relevant skills based on prompts
2. **Context Awareness** - Intelligent skill selection based on project context
3. **Usage Tracking** - Monitor which skills are used and when
4. **Extensibility** - Easy to add new skills and trigger patterns

## 🔧 Configuration Files

### skill-loader.json

Defines:
- **Skill Directories** - Where to find skill files
- **Skill Mapping** - Map skill IDs to file paths
- **Prompt Triggers** - Keywords that trigger specific skills
- **Auto-Load Settings** - Enable/disable automatic loading

Example:
```json
{
  "version": "1.0.0",
  "auto_load": true,
  "skill_directories": ["skills/core", "skills/integration"],
  "skill_mapping": {
    "pdf_generation": "skills/core/ibm-dexter-pdf-documentation.skill"
  },
  "prompt_triggers": {
    "pdf|report|documentation": ["pdf_generation"]
  }
}
```

### auto-loader.py

Python script that:
- Analyzes user prompts
- Identifies relevant skills
- Loads skills automatically
- Tracks usage statistics
- Provides CLI interface

Usage:
```bash
# Analyze a prompt
python .bob/config/auto-loader.py analyze "generate a PDF report"

# Load skills for a prompt
python .bob/config/auto-loader.py load "create UI components"

# List all available skills
python .bob/config/auto-loader.py list

# Show usage statistics
python .bob/config/auto-loader.py stats
```

## 🎨 Custom Skills

Skills are stored in the `skills/` directory (outside `.bob/`):

```
skills/
├── core/
│   ├── ibm-dexter-multi-agent-ai.skill
│   ├── ibm-dexter-pdf-documentation.skill
│   ├── ibm-carbon-design-integration.skill
│   ├── ibm-dexter-carbon-ui.skill
│   └── ibm-dexter-pdf-export.skill
├── integration/
│   └── ibm-dexter-bob-integration.skill
└── testing/
    └── ibm-dexter-testing-coverage.skill
```

## 🚀 How It Works

### 1. Prompt Analysis
When you give Bob a prompt, the auto-loader:
1. Analyzes keywords in your prompt
2. Matches against trigger patterns
3. Identifies relevant skills
4. Loads skill content

### 2. Skill Loading
Skills are loaded when:
- Keywords match trigger patterns
- Project context suggests relevance
- Explicitly requested by user
- Auto-load is enabled

### 3. Context Enhancement
Loaded skills provide:
- Domain-specific knowledge
- Code patterns and examples
- Best practices
- Integration guidelines

## 📝 Adding New Skills

### Step 1: Create Skill File
Create a new `.skill` file in `skills/core/` or appropriate directory:

```
skills/core/my-new-skill.skill
```

### Step 2: Update Configuration
Add to `skill-loader.json`:

```json
{
  "skill_mapping": {
    "my_new_skill": "skills/core/my-new-skill.skill"
  },
  "prompt_triggers": {
    "keyword1|keyword2": ["my_new_skill"]
  }
}
```

### Step 3: Test
```bash
python .bob/config/auto-loader.py analyze "keyword1 in prompt"
```

## 🔍 Skill Trigger Patterns

Current trigger patterns:

| Pattern | Skills | Use Case |
|---------|--------|----------|
| `pdf\|report\|documentation` | pdf_generation | Generate PDF documents |
| `ui\|design\|carbon\|frontend` | carbon_design | UI development |
| `test\|coverage\|quality` | testing_coverage | Testing and QA |
| `agent\|ai\|llm\|review` | multi_agent_ai | AI/ML features |
| `rag\|retrieval\|search\|context` | rag_pipeline | RAG implementation |
| `bob\|integration\|api` | bob_integration | Bob AI integration |

## 📊 Usage Statistics

The auto-loader tracks:
- Total skill loads
- Unique skills used
- Load frequency per skill
- Currently loaded skills

View stats:
```bash
python .bob/config/auto-loader.py stats
```

## 🛠️ Maintenance

### Regular Tasks
1. **Review Usage Stats** - Identify frequently used skills
2. **Update Triggers** - Add new keywords as needed
3. **Clean Up** - Remove unused skills
4. **Document Changes** - Keep this README updated

### Best Practices
- Use descriptive skill IDs
- Keep trigger patterns specific
- Document skill purposes
- Test new skills before deployment
- Version control skill files

## 🔐 Security Notes

### Safe Practices
- ✅ Skills are read-only during loading
- ✅ No code execution from skill files
- ✅ Skills are text-based knowledge
- ✅ Configuration is version controlled

### Avoid
- ❌ Storing secrets in skills
- ❌ Executable code in skill files
- ❌ Sensitive data in configurations
- ❌ Hardcoded credentials

## 📚 Related Documentation

- **Export Guide:** `../BOB_SESSION_EXPORT_GUIDE.md`
- **Session Context:** `../BOB_SESSION_CONTEXT.md`
- **Project README:** `../README.md`
- **Skills Directory:** `../skills/`

## 🎓 Learning Resources

### Understanding Bob AI
Bob AI is an AI-assisted development tool that:
- Helps write code
- Generates documentation
- Provides best practices
- Automates repetitive tasks

### Skill System Benefits
1. **Consistency** - Reusable patterns and practices
2. **Efficiency** - Quick access to domain knowledge
3. **Quality** - Proven solutions and examples
4. **Learning** - Built-in best practices

### When to Create Skills
Create a skill when you:
- Have reusable patterns
- Need domain-specific knowledge
- Want consistent approaches
- Have complex workflows

## 🤝 Contributing

### Adding Skills
1. Create skill file with clear documentation
2. Update skill-loader.json
3. Add trigger patterns
4. Test thoroughly
5. Document in this README

### Improving Auto-Loader
1. Enhance prompt analysis
2. Add new trigger patterns
3. Improve skill recommendations
4. Add usage analytics

## 📞 Support

### Troubleshooting

**Skills not loading?**
- Check skill file paths in skill-loader.json
- Verify trigger patterns match your prompts
- Ensure auto_load is true
- Check file permissions

**Auto-loader errors?**
- Verify Python 3.9+ is installed
- Check JSON syntax in skill-loader.json
- Ensure skill files exist
- Review error messages

**Need help?**
- Review this README
- Check BOB_SESSION_EXPORT_GUIDE.md
- Examine existing skills for examples
- Test with auto-loader.py CLI

## 🎉 Success Stories

This Bob configuration has enabled:
- ✅ Rapid development of IBM Dexter features
- ✅ Consistent code patterns across the project
- ✅ Efficient documentation generation
- ✅ Quick integration of IBM ecosystem tools
- ✅ Automated testing and validation

## 🔄 Version History

### v1.0.0 (2026-05-29)
- Initial Bob configuration
- Skill auto-loader implementation
- Core skills created
- Trigger patterns defined
- Documentation completed

---

**Made with Bob AI** 🤖  
*Intelligent skill loading for efficient development*