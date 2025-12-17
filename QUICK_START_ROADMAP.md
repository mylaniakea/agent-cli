# Quick Start: v1.0 Release Roadmap

This is a quick reference for getting started with the open source release preparation.

## 📋 Overview

**Goal**: Release agent-cli v1.0 as a production-ready open source project on PyPI

**Current Status**: Core development complete (Phases 1-11)

**Next Steps**: Implement Phases 12-22 for v1.0 release

## 🎯 Minimum v1.0 Release (Must Have)

**Timeline**: ~10-15 days

**Priority Order**:

1. **Phase 12: Testing Infrastructure** (2-3 days)
   - Set up pytest and test structure
   - Write unit tests for core modules
   - Add GitHub Actions CI/CD
   - Target: >80% code coverage
   - **Start here!**

2. **Phase 13: Modern Packaging** (1-2 days)
   - Create pyproject.toml
   - Migrate from setup.py
   - Prepare for PyPI publication

3. **Phase 14: Code Quality & Type Safety** (3-4 days)
   - Add type hints throughout
   - Set up ruff, black, mypy
   - Add pre-commit hooks
   - Create Makefile

4. **Phase 15: Update Model Metadata** (1 day)
   - Add latest OpenAI models (gpt-4o, o1-preview, etc.)
   - Add latest Claude models (3.5-sonnet, 3.5-haiku)
   - Add latest Gemini models (2.0-flash-exp)
   - Update Ollama models

5. **Phase 20: Documentation & Community** (2-3 days)
   - CONTRIBUTING.md
   - CODE_OF_CONDUCT.md
   - Enhanced README with badges
   - GitHub issue/PR templates

6. **Phase 22: Final Release** (1-2 days)
   - Run all checks
   - Build packages
   - Publish to PyPI
   - Create GitHub release

## 📚 Full Documentation

See **[OPEN_SOURCE_PLAN.md](OPEN_SOURCE_PLAN.md)** for:
- Complete phase details with all tasks
- "Should Have" phases for v1.0 or v1.1
- "Nice to Have" phases for v1.1+
- Success criteria for each phase
- Timeline estimates

## 🚀 Getting Started on Your Dev Server

```bash
# Clone/pull latest
cd agent-cli
git pull origin main

# Review the roadmap
less OPEN_SOURCE_PLAN.md

# Start with Phase 12: Testing Infrastructure
mkdir -p tests/{unit,integration,fixtures}
touch tests/__init__.py
```

## 🧪 Phase 12 First Steps

Create test structure:
```bash
tests/
├── __init__.py
├── unit/
│   ├── test_config.py
│   ├── test_command_registry.py
│   ├── test_model_factory.py
│   ├── test_session_manager.py
│   └── test_history_manager.py
└── integration/
    └── test_agents.py
```

Add pytest to dependencies:
```bash
# Using uv (your preference)
uv add pytest pytest-cov pytest-mock --dev

# Or using pip
pip install pytest pytest-cov pytest-mock
```

Run initial tests:
```bash
pytest tests/ -v
```

## 📦 Phase 13 Next Steps

After Phase 12, create pyproject.toml:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "agent-cli"
version = "1.0.0"
description = "A custom LLM CLI with local and external agent support"
...
```

## 🛠 Tools to Install

For full development setup:
```bash
# Core tools
uv add --dev pytest pytest-cov pytest-mock
uv add --dev black ruff mypy
uv add --dev pre-commit

# Optional for later phases
uv add --dev keyring  # Phase 19: Security
uv add --dev pygments # Phase 21: Syntax highlighting
```

## ✅ Quick Wins

Easy first contributions:
1. Add type hints to config.py
2. Write tests for command_registry.py
3. Update models.json with new models
4. Add docstrings to public functions

## 📊 Progress Tracking

Track your progress by checking off tasks in OPEN_SOURCE_PLAN.md as you complete them.

## 🤝 Questions?

- Review OPEN_SOURCE_PLAN.md for detailed task lists
- Check existing code for patterns and style
- Each phase has clear success criteria

## 🎉 Let's Ship v1.0!

The core is solid. Now let's make it production-ready for the community!
