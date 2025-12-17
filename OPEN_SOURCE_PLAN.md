# Open Source Release Plan (v1.0)

This document outlines the roadmap for preparing agent-cli for its initial open-source release.

## 📊 Current Status

**Core Development**: ✅ Complete (Phases 1-11)
- Foundation & CLI structure
- Multi-provider support (Ollama, OpenAI, Anthropic, Google)
- Interactive mode with streaming
- Command registry system
- Configuration management
- Session management
- Model factory pattern
- MCP integration
- Smart message history
- Specialized agents & themes

**What's Missing for Open Source**:
- No automated testing
- Legacy packaging (setup.py vs pyproject.toml)
- No CI/CD pipeline
- Limited documentation for contributors
- Outdated model metadata
- No community guidelines

## 🎯 Release Goals

1. **Production Ready**: Comprehensive testing, type safety, linting
2. **Easy to Contribute**: Clear guidelines, modern tooling
3. **Well Documented**: Complete wiki, troubleshooting, examples
4. **Discoverable**: Published to PyPI, GitHub topics
5. **Secure**: API key management, security policy
6. **Feature Rich**: Export, logging, context tracking, multiple providers

## 📋 Phases Overview

### Must Have (Before v1.0)
- ✅ Phase 12: Testing Infrastructure
- ✅ Phase 13: Modern Packaging
- ✅ Phase 14: Code Quality & Type Safety
- ✅ Phase 15: Update Model Metadata
- ✅ Phase 20: Documentation & Community Files
- ✅ Phase 22: Final Release Preparation

### Should Have (v1.0 or v1.1)
- 🔄 Phase 16: Export & Logging Features
- 🔄 Phase 17: Context Management Enhancements
- 🔄 Phase 19: Security Enhancements

### Nice to Have (v1.1+)
- ⏭️ Phase 18: Additional Providers (xAI, Groq, Mistral)
- ⏭️ Phase 21: Advanced CLI Features (piping, templates, cost tracking)

---

## Phase 12: Testing Infrastructure

**Goal**: Establish comprehensive testing with CI/CD

**Priority**: 🔴 Critical

**Estimated Time**: 2-3 days

### Tasks
- [ ] Create `tests/` directory structure
  - [ ] `tests/__init__.py`
  - [ ] `tests/unit/` for unit tests
  - [ ] `tests/integration/` for integration tests
  - [ ] `tests/fixtures/` for test data
- [ ] Add pytest dependencies
- [ ] Write unit tests:
  - [ ] `test_config.py` - configuration loading, priority, XDG
  - [ ] `test_command_registry.py` - command registration, help generation
  - [ ] `test_model_factory.py` - model validation, metadata
  - [ ] `test_session_manager.py` - session persistence, cleanup
  - [ ] `test_history_manager.py` - compaction, limits
- [ ] Write integration tests:
  - [ ] `test_agents.py` - mocked provider interactions
- [ ] GitHub Actions CI:
  - [ ] `.github/workflows/test.yml` - run tests on PR/push
  - [ ] `.github/workflows/release.yml` - publish to PyPI
- [ ] Test coverage reporting (aim for >80%)

### Success Criteria
- All tests pass
- Coverage >80%
- CI runs automatically on PRs

---

## Phase 13: Modern Packaging

**Goal**: Migrate to pyproject.toml and prepare for PyPI

**Priority**: 🔴 Critical

**Estimated Time**: 1-2 days

### Tasks
- [ ] Create `pyproject.toml`
  - [ ] [build-system] with setuptools
  - [ ] [project] metadata (name, version, description, authors, license)
  - [ ] [project.dependencies] from requirements.txt
  - [ ] [project.optional-dependencies] for dev tools
  - [ ] [project.urls] (homepage, issues, source, docs)
  - [ ] [project.scripts] for CLI entry point
  - [ ] [tool.pytest.ini_options] for pytest config
  - [ ] [tool.ruff] for linting config
  - [ ] [tool.mypy] for type checking
  - [ ] [tool.black] for formatting
- [ ] Create `.python-version` (3.11 or 3.12 for uv)
- [ ] Update README with new installation: `pip install agent-cli`
- [ ] Add PyPI classifiers (Development Status, Intended Audience, etc.)
- [ ] Add keywords for discoverability
- [ ] Remove `setup.py` after validation
- [ ] Test local build: `python -m build`
- [ ] Test installation from wheel

### Success Criteria
- Build succeeds: `python -m build`
- Installation works from built wheel
- All metadata correct
- Entry point `agent-cli` works

---

## Phase 14: Code Quality & Type Safety

**Goal**: Add type hints, linting, formatting

**Priority**: 🔴 Critical

**Estimated Time**: 3-4 days

### Tasks
- [ ] Add type hints to all modules:
  - [ ] `cli.py` - main entry point
  - [ ] `config.py` - config management
  - [ ] `agents/` - all agent implementations
  - [ ] `command_registry.py` - decorator and registry
  - [ ] `interactive_commands.py` - all commands
  - [ ] `model_factory.py` - factory methods
  - [ ] `session_manager.py` - session handling
  - [ ] `history_manager.py` - history management
  - [ ] `ui.py` - UI components
- [ ] Add docstrings (Google style) to all public functions
- [ ] Create `Makefile` with targets:
  - [ ] `make test` - run pytest
  - [ ] `make lint` - run ruff
  - [ ] `make format` - run black
  - [ ] `make type-check` - run mypy
  - [ ] `make all` - run all checks
- [ ] Configure pre-commit:
  - [ ] `.pre-commit-config.yaml`
  - [ ] Add black, ruff, mypy hooks
- [ ] Run black formatter on entire codebase
- [ ] Fix all ruff linting issues
- [ ] Fix all mypy type errors

### Success Criteria
- `make lint` passes with no errors
- `make type-check` passes with no errors
- All functions have type hints and docstrings

---

## Phase 15: Update Model Metadata

**Goal**: Update models.json with latest models

**Priority**: 🟡 High

**Estimated Time**: 1 day

### Tasks
- [ ] OpenAI models:
  - [ ] Add `gpt-4o` (128K context)
  - [ ] Add `gpt-4o-mini` (128K context)
  - [ ] Add `o1-preview` (128K context)
  - [ ] Add `o1-mini` (128K context)
  - [ ] Remove deprecated models
- [ ] Anthropic models:
  - [ ] Add `claude-3-5-sonnet-20241022` (200K context)
  - [ ] Add `claude-3-5-haiku-20241022` (200K context)
  - [ ] Update aliases (sonnet, haiku, opus)
- [ ] Google models:
  - [ ] Add `gemini-2.0-flash-exp` (1M context)
  - [ ] Add `gemini-1.5-pro-002` (2M context)
- [ ] Ollama models:
  - [ ] Add `qwen2.5:latest`
  - [ ] Add `llama3.1:latest`
  - [ ] Add `llama3.2:latest`
  - [ ] Add `deepseek-r1:latest`
  - [ ] Add `phi4:latest`
- [ ] Optional: Add cost_per_million_tokens for pricing estimates

### Success Criteria
- All current production models included
- Context lengths accurate
- Models validate correctly in ModelFactory

---

## Phase 16: Export & Logging Features

**Goal**: Add conversation export and logging

**Priority**: 🟢 Medium

**Estimated Time**: 2 days

### Tasks
- [ ] Create `agent_cli/export_manager.py`:
  - [ ] `export_to_markdown()` - format as markdown
  - [ ] `export_to_json()` - full conversation data
  - [ ] Handle file naming and paths
- [ ] Add `/export` command:
  - [ ] `/export markdown <filename>` - export to markdown
  - [ ] `/export json <filename>` - export to JSON
  - [ ] `/export` - prompt for format and filename
- [ ] Add `--log` flag to CLI
- [ ] Add LOG_DIR config option
- [ ] Create automatic logging:
  - [ ] Timestamp-based filenames
  - [ ] Save to LOG_DIR on exit
- [ ] Add `/log` command to show log status

### Success Criteria
- Export to markdown works
- Export to JSON works
- Auto-logging saves conversations

---

## Phase 17: Context Management Enhancements

**Goal**: Track context usage and warn on limits

**Priority**: 🟢 Medium

**Estimated Time**: 2 days

### Tasks
- [ ] Create `agent_cli/context_tracker.py`:
  - [ ] Calculate token counts (approximation or tiktoken)
  - [ ] Track usage vs model limits
  - [ ] Generate warnings at thresholds
- [ ] Add `/context` command:
  - [ ] Show current token count
  - [ ] Show model context limit
  - [ ] Show percentage used
- [ ] Add context warnings:
  - [ ] Warning at 80% usage
  - [ ] Warning at 90% usage
  - [ ] Critical warning at 95% usage
- [ ] Update `/history` to show token counts
- [ ] Add CONTEXT_WARNING_THRESHOLD config

### Success Criteria
- Token counting accurate (±5%)
- Warnings display at thresholds
- `/context` command shows usage

---

## Phase 18: Additional Providers

**Goal**: Add xAI, Groq, Mistral AI support

**Priority**: 🔵 Low (v1.1+)

**Estimated Time**: 3-4 days

### Tasks
- [ ] xAI (Grok):
  - [ ] Create `agent_cli/agents/xai_agent.py`
  - [ ] Add models to `models.json`
  - [ ] Update factory
  - [ ] Add to CLI choices
- [ ] Groq:
  - [ ] Create `agent_cli/agents/groq_agent.py`
  - [ ] Add models (llama3, mixtral, etc.)
  - [ ] Update factory
- [ ] Mistral AI:
  - [ ] Create `agent_cli/agents/mistral_agent.py`
  - [ ] Add models
  - [ ] Update factory
- [ ] Update `.env.example` with new API keys
- [ ] Update documentation

### Success Criteria
- All 3 providers working
- Models listed correctly
- Documentation updated

---

## Phase 19: Security Enhancements

**Goal**: Improve API key security

**Priority**: 🟢 Medium

**Estimated Time**: 2 days

### Tasks
- [ ] Add keyring support:
  - [ ] Add keyring library (optional dependency)
  - [ ] Create keyring wrapper in config.py
  - [ ] Add `/keyring set <provider>` command
  - [ ] Add `/keyring get <provider>` command
  - [ ] Add `/keyring clear <provider>` command
  - [ ] Add `--use-keyring` CLI flag
- [ ] Add privacy features:
  - [ ] Add `--no-history` flag
  - [ ] Mask API keys in `/config` display
  - [ ] Enhanced security warning for `/set` command
- [ ] Create SECURITY.md:
  - [ ] Security policy
  - [ ] Reporting vulnerabilities
  - [ ] Best practices

### Success Criteria
- Keyring stores/retrieves API keys
- `--no-history` disables history
- SECURITY.md published

---

## Phase 20: Documentation & Community Files

**Goal**: Complete documentation and community guidelines

**Priority**: 🔴 Critical

**Estimated Time**: 2-3 days

### Tasks
- [ ] Create CONTRIBUTING.md:
  - [ ] Development setup
  - [ ] Code style guidelines
  - [ ] Testing requirements
  - [ ] PR process
  - [ ] Code review expectations
- [ ] Create CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
- [ ] Update README.md:
  - [ ] Add badges (build, coverage, PyPI, license)
  - [ ] Add demo GIF/video
  - [ ] Add "Why Agent CLI?" comparison section
  - [ ] Add troubleshooting quick tips
  - [ ] Update installation for PyPI
  - [ ] Add contributor section
- [ ] Create docs/TROUBLESHOOTING.md:
  - [ ] Common issues and solutions
  - [ ] Provider-specific issues
  - [ ] Installation problems
- [ ] Create docs/USE_CASES.md:
  - [ ] Example workflows
  - [ ] Use case scenarios
  - [ ] Advanced examples
- [ ] Update wiki docs:
  - [ ] Update WIKI_HOME.md
  - [ ] Update all feature docs
  - [ ] Add new feature pages
- [ ] Create GitHub templates:
  - [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
  - [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
  - [ ] `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] Update setup.py author info

### Success Criteria
- All community files present
- README is comprehensive and engaging
- GitHub templates work correctly

---

## Phase 21: Advanced CLI Features

**Goal**: Add piping, templates, cost tracking

**Priority**: 🔵 Low (v1.1+)

**Estimated Time**: 3-4 days

### Tasks
- [ ] Add stdin piping support:
  - [ ] Detect stdin data
  - [ ] Use stdin as prompt
  - [ ] Example: `cat file.py | agent-cli --provider ollama`
- [ ] Add syntax highlighting:
  - [ ] Add pygments dependency
  - [ ] Detect code blocks in responses
  - [ ] Apply syntax highlighting
- [ ] Create template system:
  - [ ] `agent_cli/template_manager.py`
  - [ ] `/template save <name>` command
  - [ ] `/template load <name>` command
  - [ ] `/template list` command
  - [ ] Store in `~/.agent-cli/templates/`
- [ ] Create cost tracking:
  - [ ] `agent_cli/cost_tracker.py`
  - [ ] Track tokens per request
  - [ ] Calculate costs (from pricing data)
  - [ ] `/cost` command to show totals
- [ ] Add `/fork` command to branch conversations

### Success Criteria
- Piping works: `cat file.py | agent-cli`
- Code syntax highlighting works
- Templates save and load
- Cost tracking accurate

---

## Phase 22: Final Release Preparation

**Goal**: Prepare for v1.0 release

**Priority**: 🔴 Critical

**Estimated Time**: 1-2 days

### Tasks
- [ ] Run full test suite, verify all pass
- [ ] Run `make lint`, fix any issues
- [ ] Run `make type-check`, fix any issues
- [ ] Update CHANGELOG.md:
  - [ ] Document all changes since initial commit
  - [ ] Organize by category (features, fixes, docs)
  - [ ] Add migration notes if needed
- [ ] Update version to 1.0.0 in pyproject.toml
- [ ] Build distribution:
  - [ ] `python -m build`
  - [ ] Verify wheel and sdist
- [ ] Test installation from wheel
- [ ] Publish to test.pypi.org first
- [ ] Test install from test.pypi.org
- [ ] Publish to pypi.org
- [ ] Create GitHub release:
  - [ ] Tag as v1.0.0
  - [ ] Add release notes
  - [ ] Attach built artifacts
- [ ] Post-release setup:
  - [ ] Enable GitHub Discussions
  - [ ] Add GitHub topics/tags
  - [ ] Create announcement post draft
  - [ ] Share on relevant communities

### Success Criteria
- Published to PyPI successfully
- GitHub release created
- Installation via `pip install agent-cli` works
- All documentation updated

---

## 📈 Timeline Summary

| Phase | Priority | Estimated Time | Category |
|-------|----------|---------------|----------|
| 12 | Critical | 2-3 days | Must Have |
| 13 | Critical | 1-2 days | Must Have |
| 14 | Critical | 3-4 days | Must Have |
| 15 | High | 1 day | Must Have |
| 20 | Critical | 2-3 days | Must Have |
| 22 | Critical | 1-2 days | Must Have |
| **Subtotal** | | **10-15 days** | **Must Have** |
| 16 | Medium | 2 days | Should Have |
| 17 | Medium | 2 days | Should Have |
| 19 | Medium | 2 days | Should Have |
| **Subtotal** | | **6 days** | **Should Have** |
| 18 | Low | 3-4 days | Nice to Have |
| 21 | Low | 3-4 days | Nice to Have |
| **Subtotal** | | **6-8 days** | **Nice to Have** |
| **TOTAL** | | **22-29 days** | **All Phases** |

---

## 🎯 Release Strategy

### v1.0 Minimum (Must Have)
Focus: Production-ready, well-tested, properly packaged, documented
- Phases 12, 13, 14, 15, 20, 22
- Estimated: 10-15 days

### v1.0 Full (Must Have + Should Have)
Focus: Feature-complete with export, context management, security
- Add Phases 16, 17, 19
- Estimated: 16-21 days

### v1.1 (Nice to Have)
Focus: Extended provider support, advanced features
- Add Phases 18, 21
- Estimated: Additional 6-8 days

---

## 📊 Success Metrics

### Technical
- ✅ >80% test coverage
- ✅ All type checks pass
- ✅ All linting passes
- ✅ CI/CD pipeline functional
- ✅ Published to PyPI

### Community
- ✅ Complete README with examples
- ✅ CONTRIBUTING.md in place
- ✅ CODE_OF_CONDUCT.md in place
- ✅ Issue/PR templates created
- ✅ Wiki documentation complete

### Features
- ✅ At least 4 providers (Ollama, OpenAI, Anthropic, Google)
- ✅ Export functionality
- ✅ Context management
- ✅ Security enhancements
- ✅ Up-to-date model metadata

---

## 🚀 Next Steps

1. Start with Phase 12 (Testing Infrastructure)
2. Move to Phase 13 (Modern Packaging)
3. Continue through must-have phases
4. Evaluate should-have phases based on time
5. Plan v1.1 for nice-to-have features

**Let's build something amazing! 🎉**
