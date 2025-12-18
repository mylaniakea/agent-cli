# /init Command - Superpower Design

## Current Implementation

The `/init` command currently:
- ✅ Creates a project config file (.agent.yml or claude.md/gpt.md/etc.)
- ✅ Sets provider, model, temperature
- ✅ Supports YAML or Markdown format
- ✅ Allows system prompts

**Usage:**
```bash
/init anthropic
/init google --format yaml
```

**Creates:**
```yaml
# .agent.yml
provider: anthropic
model: default
temperature: 0.7
system_prompt: |
  Generic instructions...
```

---

## 🚀 Superpower Features - Proposed

### 1. **Interactive Wizard Mode** 🧙

Replace simple arguments with a beautiful step-by-step wizard using our new UI components.

**Experience:**
```
╭────────────────────────────────────────────╮
│ 🚀 Project Initialization Wizard          │
╰────────────────────────────────────────────╯

Select your PRIMARY provider:
(*) 🤖 OpenAI (GPT-4, o1)
( ) 🧠 Anthropic (Claude 3.5)
( ) ✨ Google (Gemini)
( ) 🦙 Ollama (Local)

Select project type:
(*) 💻 Python Application
( ) 🌐 Web Development (React/Node)
( ) 📱 Mobile Development
( ) 📊 Data Science/ML
( ) 🎨 General/Other

Select model:
( ) claude-3-5-sonnet-20241022 (Recommended for coding)
(*) claude-3-5-haiku-20241022 (Fast, cost-effective)
( ) claude-3-opus-20240229 (Most capable)

Select configuration format:
(*) 📄 Markdown (claude.md) - Human-friendly
( ) 📋 YAML (.agent.yml) - Structured

✨ Analyzing your project...
  ✓ Detected: Python 3.11
  ✓ Found: requirements.txt, setup.py
  ✓ Framework: FastAPI

📝 Generated custom system prompt
💾 Created: claude.md

🎉 Project initialized successfully!

Next steps:
  • Edit claude.md to add project-specific instructions
  • Use /chat to start coding with project context
  • Use /fallback to add a backup provider
```

---

### 2. **Smart Project Detection** 🔍

Auto-detect project type and suggest optimal configuration.

**Detection Logic:**
```python
# Detect from files
- package.json → Node.js/TypeScript
- requirements.txt/setup.py → Python
- Cargo.toml → Rust
- go.mod → Go
- pom.xml/build.gradle → Java

# Detect framework
- next.config.js → Next.js
- nuxt.config.js → Nuxt
- manage.py → Django
- app.py + flask → Flask
- main.py + fastapi → FastAPI

# Detect purpose
- test/ directory → Include testing context
- docs/ directory → Documentation mode
- src/components/ → React/Vue
```

**Smart Suggestions:**
```
🔍 Project Analysis:

Detected: Python 3.11 + FastAPI
Framework: FastAPI (async web framework)
Estimated Size: Medium (~5K LOC)
Git Repo: Yes

📊 Recommended Configuration:

Provider: anthropic (Best for Python + architecture)
Model: claude-3-5-sonnet-20241022 (Reasoning + coding)
Temperature: 0.3 (Precise code generation)
Fallback: ollama/deepseek-coder-v2 (Local backup)

System Prompt: Generated for FastAPI development
  • Async/await patterns
  • Pydantic models
  • API best practices
  • Testing with pytest
```

---

### 3. **Template Library** 📚

Pre-built templates for common project types.

**Templates:**
```
Available Templates:

1. 🐍 Python Development
   - Web API (FastAPI, Django, Flask)
   - Data Science (Pandas, NumPy)
   - CLI Tools
   - Testing (pytest, unittest)

2. 🌐 Web Development
   - React/Next.js
   - Vue/Nuxt
   - Svelte/SvelteKit
   - Node.js Backend

3. 📱 Mobile Development
   - React Native
   - Flutter
   - SwiftUI
   - Kotlin

4. 📊 Data Science
   - ML/AI Development
   - Data Analysis
   - Jupyter Notebooks

5. 🛠️ DevOps/Infrastructure
   - Docker/K8s
   - Terraform
   - CI/CD Pipelines

6. 📝 Documentation
   - Technical Writing
   - API Docs
   - README Generation

7. 🎨 Custom
   - Blank template
   - Import from GitHub
```

**Template Example (FastAPI):**
```markdown
---
provider: anthropic
model: claude-3-5-sonnet-20241022
temperature: 0.3
context_files:
  - "**/*.py"
  - "requirements.txt"
  - "README.md"
exclude_patterns:
  - "**/test_*.py"
  - "**/__pycache__/**"
tools:
  - code_search
  - file_edit
  - terminal
---

# FastAPI Project Assistant

You are an expert FastAPI developer. When working on this project:

## Code Style
- Use async/await for all route handlers
- Type hints everywhere (Pydantic models)
- Follow PEP 8 conventions
- Descriptive variable names

## Architecture
- Follow clean architecture principles
- Separate concerns: routes, services, models
- Use dependency injection for services
- Keep routes thin, business logic in services

## Testing
- Write pytest tests for all endpoints
- Use TestClient from fastapi.testclient
- Mock external dependencies
- Aim for >80% coverage

## Security
- Validate all inputs with Pydantic
- Use proper authentication (OAuth2/JWT)
- Sanitize database queries (use ORM)
- CORS configuration for production

## Performance
- Use async database drivers
- Implement caching where appropriate
- Optimize database queries (N+1 problem)
- Use background tasks for slow operations

When generating code:
1. Always include type hints
2. Add docstrings for public functions
3. Include error handling
4. Write corresponding tests
5. Consider edge cases
```

---

### 4. **Multi-File Context Configuration** 📂

Automatically include relevant files in context.

**Configuration:**
```yaml
# .agent.yml
provider: anthropic
model: claude-3-5-sonnet-20241022

# Auto-include these files in every conversation
context_files:
  - "README.md"           # Project overview
  - "ARCHITECTURE.md"     # System design
  - "requirements.txt"    # Dependencies
  - "src/**/*.py"         # All Python source
  - "!**/test_*.py"       # Exclude tests

# Watch for changes
watch_files:
  - "package.json"        # Dependency changes
  - ".env.example"        # Environment vars

# File size limits
max_file_size: 50kb
max_total_context: 100kb

# Smart context
auto_detect_imports: true  # Include imported files
include_recent_changes: 5  # Last 5 git commits
```

---

### 5. **Advanced Provider Configuration** ⚙️

Configure multiple models, tools, and capabilities.

**Configuration:**
```yaml
# .agent.yml
providers:
  primary:
    provider: anthropic
    model: claude-3-5-sonnet-20241022
    temperature: 0.3
    max_tokens: 4096
    use_cases: ["coding", "architecture"]

  fallback:
    provider: ollama
    model: deepseek-coder-v2
    temperature: 0.3
    use_cases: ["coding", "quick-questions"]

  documentation:
    provider: openai
    model: gpt-4o
    temperature: 0.7
    use_cases: ["writing", "documentation"]

  research:
    provider: google
    model: gemini-1.5-pro
    temperature: 0.9
    use_cases: ["research", "brainstorming"]

# Auto-routing
auto_route: true
route_by:
  - intent        # Detect what user wants
  - cost          # Prefer cheaper for simple tasks
  - speed         # Use fast models for quick queries
  - capability    # Use best model for complex tasks

# Model-specific tools
tools:
  code_search:
    enabled: true
    max_results: 10

  file_operations:
    enabled: true
    allowed_paths: ["src/", "tests/"]
    forbidden_paths: [".env", "secrets/"]

  web_search:
    enabled: false

  terminal:
    enabled: true
    allowed_commands: ["git", "npm", "pytest"]
    forbidden_commands: ["rm -rf", "sudo"]
```

---

### 6. **Git Integration** 🔀

Leverage git history and branch info.

**Features:**
```yaml
# .agent.yml
git:
  enabled: true

  # Include git context
  include_branch: true        # Current branch name
  include_status: true        # Changed files
  include_recent_commits: 5   # Last 5 commits
  include_diff: true          # Uncommitted changes

  # Commit message generation
  auto_commit_messages: true
  commit_style: "conventional"  # conventional | detailed | short

  # Branch context
  branch_context:
    main: "Production code - be careful"
    dev: "Development - experimental OK"
    feature/*: "New feature development"
    fix/*: "Bug fix - focus on testing"

# System prompt gets branch context
system_prompt: |
  Current branch: {{git.branch}}
  Recent work: {{git.recent_commits}}

  Branch guidelines: {{git.branch_context}}
```

---

### 7. **Team Configuration** 👥

Shareable configs with personal overrides.

**Structure:**
```
.agent/
  ├── team.yml          # Shared team config (committed to git)
  ├── personal.yml      # Your personal overrides (gitignored)
  └── templates/        # Shared templates
      ├── python.md
      ├── react.md
      └── documentation.md
```

**team.yml (Shared):**
```yaml
# Team-wide defaults
provider: anthropic
model: claude-3-5-sonnet-20241022
temperature: 0.3

# Shared system prompt
system_prompt_file: .agent/templates/team-guidelines.md

# Code style
code_style:
  language: python
  formatter: black
  linter: ruff
  conventions: .agent/templates/conventions.md

# Review guidelines
review_focus:
  - security
  - performance
  - testing
  - documentation
```

**personal.yml (Gitignored):**
```yaml
# Override provider (maybe you prefer local)
provider: ollama
model: llama3.3

# Your API keys
api_keys:
  anthropic: ${ANTHROPIC_API_KEY}
  openai: ${OPENAI_API_KEY}

# Personal preferences
temperature: 0.5
verbose: true
```

---

### 8. **Interactive Configuration Editor** ✏️

Edit config visually within the CLI.

**Interface:**
```
╭─────────────────────────────────────╮
│ 📝 Configuration Editor             │
╰─────────────────────────────────────╯

Provider Settings:
  Primary:     🧠 anthropic / claude-3-5-sonnet
  Fallback:    🦙 ollama / deepseek-coder-v2
  Temperature: 0.3
  [Edit]

Project Context:
  Type:        Python / FastAPI
  Files:       src/**/*.py (24 files)
  Excludes:    tests/, __pycache__/
  [Edit]

System Prompt:
  Template:    FastAPI Development
  Custom:      Yes (125 lines)
  [View] [Edit]

Advanced:
  Git Integration:   ✓ Enabled
  Auto-routing:      ✓ Enabled
  Tools:             code_search, file_edit, terminal
  [Configure]

[Save] [Cancel] [Reset to Default]
```

---

### 9. **Smart Defaults & Recommendations** 🧠

AI-powered configuration suggestions.

**Analysis:**
```python
def analyze_project(path: Path) -> ProjectAnalysis:
    """Analyze project and suggest optimal config."""

    analysis = ProjectAnalysis()

    # Detect language
    analysis.languages = detect_languages(path)

    # Detect framework
    analysis.frameworks = detect_frameworks(path)

    # Analyze complexity
    analysis.loc = count_lines_of_code(path)
    analysis.complexity = "simple" | "medium" | "complex"

    # Analyze requirements
    has_tests = (path / "tests").exists()
    has_docs = (path / "docs").exists()
    has_ci = (path / ".github").exists()

    # Suggest provider
    if analysis.complexity == "complex":
        suggest_provider = "anthropic"
        suggest_model = "claude-3-5-sonnet"
    elif analysis.languages.primary == "python":
        suggest_provider = "anthropic"
        suggest_model = "claude-3-5-haiku"
    else:
        suggest_provider = "openai"
        suggest_model = "gpt-4o-mini"

    # Suggest temperature
    if "test" in str(path) or has_tests:
        suggest_temperature = 0.2  # Precise for tests
    elif has_docs:
        suggest_temperature = 0.7  # Creative for docs
    else:
        suggest_temperature = 0.3  # Balanced for code

    return analysis
```

---

### 10. **Migration & Import Tools** 📥

Import configs from other tools.

**Supported Imports:**
```
Import configuration from:

[1] Cursor .cursorrules
[2] Aider .aider.conf.yml
[3] Continue config.json
[4] GitHub Copilot settings
[5] Custom JSON/YAML
[6] Environment variables

Select source: █
```

**Import Example:**
```python
# Import from Cursor
cursor_rules = Path(".cursorrules").read_text()

# Parse and convert
agent_config = convert_cursor_to_agent(cursor_rules)

# Save
ProjectConfig.create_from_dict(agent_config)
```

---

## Implementation Plan

### Phase 1: Interactive Wizard ✅
- [ ] Use MultiSelect for provider selection
- [ ] Use SingleSelect for model/template selection
- [ ] Project type detection
- [ ] Template selection
- [ ] Smart defaults

### Phase 2: Project Analysis 🔍
- [ ] Language/framework detection
- [ ] Complexity analysis
- [ ] Git integration
- [ ] Context file suggestion

### Phase 3: Advanced Features ⚙️
- [ ] Multi-provider configuration
- [ ] Tool configuration
- [ ] Auto-routing
- [ ] Team configs

### Phase 4: Editor & Tools 🛠️
- [ ] Interactive config editor
- [ ] Migration tools
- [ ] Template library
- [ ] Validation & testing

---

## Proposed Command Structure

### Basic Usage (Wizard)
```bash
/init                    # Launch interactive wizard
/init anthropic          # Quick init with provider
/init --template python  # Use template
```

### Advanced Usage
```bash
/init --analyze          # Analyze and suggest
/init --import cursor    # Import from Cursor
/init --edit             # Edit existing config
/init --validate         # Check config validity
/init --team             # Setup team config
```

### Configuration Commands
```bash
/config init             # Alias for /init
/config edit             # Edit current config
/config show             # Show current config
/config validate         # Validate config
/config reset            # Reset to default
```

---

## Benefits

### Developer Experience
- ✅ **5x Faster Setup** - Wizard vs manual editing
- ✅ **Smart Defaults** - No need to know all options
- ✅ **Project-Aware** - Optimal config for your stack
- ✅ **Template Library** - Pre-built best practices
- ✅ **Visual Interface** - Beautiful, guided setup

### Team Collaboration
- ✅ **Shared Configs** - Consistent team settings
- ✅ **Personal Overrides** - Customize without conflicts
- ✅ **Version Control** - Git-friendly YAML/Markdown
- ✅ **Documentation** - Self-documenting configs

### Reliability
- ✅ **Multi-Provider** - Automatic failover
- ✅ **Validation** - Catch errors early
- ✅ **Migration** - Easy import from other tools
- ✅ **Testing** - Verify before deploying

---

## What's Your Idea? 💡

I'd love to hear what you had in mind! Some questions:

1. **Specific Use Case** - What project type are you working on?
2. **Pain Points** - What's currently frustrating about init?
3. **Must-Have Features** - What would make this "super powered"?
4. **Team or Solo** - Individual developer or team collaboration?
5. **Integration** - Any specific tools to integrate with?

Let me know and we can design the perfect /init experience! 🚀
