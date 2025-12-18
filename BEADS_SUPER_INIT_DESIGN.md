# Beads Auto-Integration for Super Init 🔗

## Overview

**Beads** is a conversation summarization system that maintains long-term project context. Let's embed it deeply into the super init to create a **persistent, intelligent project memory**.

---

## Current State

### Internal BeadsManager (`beads.py`)
- ✅ Conversation summarization
- ✅ Automatic compaction (15→20 messages)
- ✅ Summary storage

### External Beads CLI (`/beads` command)
- ✅ Integration with `bd` tool
- ✅ Status and context checking
- ✅ Auto-install via Homebrew

### Config Support
```yaml
# .agent.yml
beads:
  enabled: true
  max_messages: 20
  summary_threshold: 15
```

---

## 🚀 Super Init + Beads Integration

### 1. **Auto-Detection & Setup** 🔍

During `/init`, automatically:

```
╭────────────────────────────────────────────╮
│ 🚀 Project Initialization Wizard          │
╰────────────────────────────────────────────╯

Checking for Beads CLI...
  ✓ Beads CLI detected: v1.2.3
  ✓ Project context available: Yes

[1] 🔗 Use existing Beads project context
[2] 📝 Create new Beads project
[3] ⊘  Skip Beads integration

Select option: █
```

**If Beads not installed:**
```
⚠️  Beads CLI not found

Beads provides:
  • Persistent project context across sessions
  • Automatic conversation summarization
  • Git-aware context management
  • Team-shared project knowledge

Install Beads?
(*) Yes, install via Homebrew
( ) Yes, manual install
( ) No, skip for now
```

---

### 2. **Smart Beads Configuration** 🧠

Configure based on project characteristics:

```python
def configure_beads_for_project(project_analysis):
    """Auto-configure beads settings based on project."""

    config = {
        "enabled": True,
        "cli_integration": detect_beads_cli(),
    }

    # Adjust based on project size
    if project_analysis.loc > 10000:  # Large project
        config["max_messages"] = 30
        config["summary_threshold"] = 20
        config["auto_summarize"] = True
        config["include_file_context"] = True
    elif project_analysis.loc > 1000:  # Medium project
        config["max_messages"] = 20
        config["summary_threshold"] = 15
        config["auto_summarize"] = True
    else:  # Small project
        config["max_messages"] = 15
        config["summary_threshold"] = 10
        config["auto_summarize"] = False

    # Adjust based on team size
    if project_analysis.is_team_project:
        config["team_sync"] = True
        config["shared_context"] = True
        config["context_file"] = ".beads/team-context.md"

    # Adjust based on activity
    if project_analysis.recent_commits > 50:  # Active project
        config["auto_update_context"] = True
        config["git_integration"] = True
        config["sync_frequency"] = "daily"

    return config
```

**Example Configuration:**
```yaml
# .agent.yml (Large, active project)
beads:
  # Internal summarization
  enabled: true
  max_messages: 30
  summary_threshold: 20
  auto_summarize: true

  # External CLI integration
  cli_integration: true
  auto_update_context: true

  # Git integration
  git_integration: true
  include_commits: 20
  include_diff: true

  # Team features
  team_sync: true
  shared_context: true
  context_file: .beads/team-context.md

  # Context files
  watch_files:
    - "README.md"
    - "ARCHITECTURE.md"
    - "docs/**/*.md"

  # Smart features
  auto_categorize: true  # Tag conversations by type
  search_enabled: true   # Search old contexts
  export_summaries: true # Export to markdown
```

---

### 3. **Project Context Initialization** 📚

Auto-generate initial project context using Beads:

```
Initializing Beads project context...

📊 Analyzing project...
  ✓ Files scanned: 234
  ✓ Code structure analyzed
  ✓ Dependencies mapped
  ✓ Git history processed (50 commits)

📝 Generating project knowledge base...
  ✓ Architecture summary
  ✓ Key components identified
  ✓ Common patterns extracted
  ✓ Coding conventions detected

💾 Storing in .beads/project-context.md

Project Context Summary:
  • Type: Python FastAPI application
  • Purpose: REST API for user management
  • Key Files: 15 core modules
  • Tech Stack: FastAPI, SQLAlchemy, PostgreSQL
  • Patterns: Repository pattern, dependency injection
  • Testing: pytest with 85% coverage
```

**Generated `.beads/project-context.md`:**
```markdown
# Project Context: MyApp API

## Overview
FastAPI-based REST API for user management and authentication.

## Architecture
- **API Layer**: FastAPI routes in `app/routes/`
- **Business Logic**: Services in `app/services/`
- **Data Layer**: SQLAlchemy models in `app/models/`
- **Database**: PostgreSQL with Alembic migrations

## Key Components

### Authentication System
- JWT-based authentication
- Refresh token rotation
- OAuth2 integration (Google, GitHub)
- Located in: `app/auth/`

### User Management
- CRUD operations for users
- Role-based access control (RBAC)
- User profiles and preferences
- Located in: `app/users/`

### Database
- PostgreSQL 14
- Connection pooling via SQLAlchemy
- Migrations in `alembic/versions/`

## Coding Conventions
- Async/await for all I/O operations
- Type hints on all functions
- Pydantic models for validation
- Services use dependency injection
- Tests follow AAA pattern

## Recent Work (Last 10 commits)
1. Added OAuth2 support
2. Implemented user profile endpoints
3. Enhanced error handling
4. Added rate limiting
5. Improved test coverage
... (auto-updated from git)

## Open Issues
- [ ] Implement password reset flow
- [ ] Add email verification
- [ ] Optimize database queries

---
Auto-generated by Beads on 2025-12-17
Last updated: Every commit via git hook
```

---

### 4. **Conversation Memory Architecture** 💭

**Multi-Layer Context System:**

```
┌─────────────────────────────────────────┐
│      Current Conversation (Live)        │
│   [Last 20 messages - Full detail]     │
└─────────────────────────────────────────┘
              ↓ Auto-summarize
┌─────────────────────────────────────────┐
│     Session Summaries (Today)           │
│   [5-10 summaries from today's work]   │
└─────────────────────────────────────────┘
              ↓ Daily digest
┌─────────────────────────────────────────┐
│     Weekly Digests (Recent)             │
│   [Summaries of this week's progress]  │
└─────────────────────────────────────────┘
              ↓ Weekly rollup
┌─────────────────────────────────────────┐
│     Project Knowledge Base              │
│   [Long-term facts, decisions, patterns]│
└─────────────────────────────────────────┘
```

**How It Works:**

```python
class BeadsSuperManager:
    """Enhanced Beads with multi-layer context."""

    def __init__(self, project_config):
        self.current_session = []      # Live conversation
        self.session_summaries = []    # Today's summaries
        self.weekly_digests = []       # This week
        self.knowledge_base = ProjectKnowledgeBase()

    async def add_message(self, message):
        """Add message and manage context layers."""
        self.current_session.append(message)

        # Trigger summarization if needed
        if len(self.current_session) > self.threshold:
            summary = await self.summarize_session()
            self.session_summaries.append(summary)
            self.current_session = self.current_session[-10:]  # Keep recent

        # Daily digest
        if self.should_create_daily_digest():
            digest = await self.create_daily_digest()
            self.weekly_digests.append(digest)
            self.session_summaries.clear()

        # Update knowledge base
        if self.message_contains_decision(message):
            await self.knowledge_base.add_decision(message)

    def get_context_for_prompt(self, query: str) -> str:
        """Get relevant context for a query."""
        context_parts = []

        # Always include project knowledge base
        context_parts.append(self.knowledge_base.summary())

        # Add relevant weekly digests (semantic search)
        relevant_digests = self.search_digests(query, limit=2)
        context_parts.extend(relevant_digests)

        # Add today's summaries
        context_parts.extend(self.session_summaries[-3:])

        # Add current conversation
        context_parts.append(self.format_current_session())

        return "\n\n".join(context_parts)
```

---

### 5. **Git-Aware Context Updates** 🔀

Automatically update context on git events:

**Git Hooks Integration:**
```bash
# .git/hooks/post-commit (auto-installed by init)
#!/bin/bash
# Update Beads context after commit

bd update-context --commit "$1"
agent-cli beads sync
```

**What Gets Updated:**
```yaml
# On every commit:
- Recent work summary (last 5 commits)
- Changed files context
- New TODOs/FIXMEs added
- Tests added/modified

# On PR/merge:
- Feature summary
- Architecture changes
- New dependencies
- Breaking changes

# Daily:
- Progress summary
- Open issues
- Team activity
```

---

### 6. **Team Context Syncing** 👥

Share project context across team:

```yaml
# .agent.yml
beads:
  team_sync:
    enabled: true

    # Shared context files (committed to git)
    shared_files:
      - .beads/project-knowledge.md   # Core facts
      - .beads/architecture.md        # System design
      - .beads/conventions.md         # Team standards

    # Personal context (gitignored)
    personal_files:
      - .beads/personal-notes.md      # Your notes
      - .beads/work-log.md            # Your log

    # Auto-merge strategy
    merge_strategy: "append"          # or "override" | "manual"

    # Conflict resolution
    on_conflict: "prompt"             # or "use-remote" | "use-local"
```

**Sync Flow:**
```
1. Pull latest changes
   ↓
2. Detect .beads/ changes
   ↓
3. Merge team knowledge
   ↓
4. Update local context
   ↓
5. Notify user of updates

"📥 Team context updated:
  • Architecture.md: New microservices section
  • Conventions.md: Added error handling standards
  • 3 new decisions documented"
```

---

### 7. **Smart Context Retrieval** 🔎

Semantic search through Beads context:

```python
class BeadsSearch:
    """Search through beads summaries and context."""

    def semantic_search(self, query: str, limit: int = 5):
        """Find relevant context using embeddings."""

        # Create query embedding
        query_embedding = self.embed(query)

        # Search through:
        # 1. Session summaries
        # 2. Weekly digests
        # 3. Knowledge base entries
        # 4. Git commit messages
        # 5. File contents

        results = []
        for source in self.all_sources():
            similarity = cosine_similarity(query_embedding, source.embedding)
            if similarity > 0.7:
                results.append((source, similarity))

        # Return top results
        return sorted(results, key=lambda x: x[1], reverse=True)[:limit]
```

**Usage:**
```
User: "How did we implement authentication?"

Agent context retrieval:
  🔍 Searching beads context...

  Found relevant entries:
    1. Session 2024-12-15: "Implemented JWT auth" (95% match)
    2. Weekly digest: "Auth system design" (88% match)
    3. Commit d4f3a1b: "Add OAuth2 support" (82% match)

  Loading context...

Agent: "Based on our previous work, the authentication system uses..."
```

---

### 8. **Auto-Categorization & Tagging** 🏷️

Automatically organize conversations:

```yaml
# Auto-detected categories
categories:
  - bug-fixing       # Fixing issues
  - feature-dev      # New features
  - refactoring      # Code improvements
  - documentation    # Writing docs
  - debugging        # Troubleshooting
  - architecture     # System design
  - testing          # Writing tests
  - research         # Exploring solutions

# Auto-tagging
tags:
  - authentication   # Auth-related
  - database        # DB queries/models
  - api             # API endpoints
  - performance     # Optimization
  - security        # Security concerns
```

**Example:**
```markdown
# Session 2024-12-17 14:30
**Category:** feature-dev
**Tags:** authentication, security, api
**Duration:** 45 minutes

## Summary
Implemented password reset flow with email verification.

## Key Decisions
1. Use JWT tokens for reset links (expire in 1 hour)
2. Rate limit to 3 requests per hour per user
3. Send email via SendGrid

## Files Modified
- app/auth/password_reset.py (new)
- app/routes/auth.py (+25 lines)
- tests/test_password_reset.py (new)

## Next Steps
- Add email templates
- Test edge cases
- Update API docs
```

---

### 9. **Intelligent Init Questions** 💬

Beads-aware init wizard:

```
╭────────────────────────────────────────────╮
│ 🚀 Project Initialization Wizard          │
╰────────────────────────────────────────────╯

Configure Beads Context Management:

How often do you work on this project?
(*) Daily (Active development)
( ) Weekly (Maintenance mode)
( ) Occasionally (Side project)

This affects:
  • Auto-summarization frequency
  • Context retention period
  • Sync settings

─────────────────────────────────────────────

Is this a team project?
(*) Yes, I work with others
( ) No, solo project

If Yes:
  ✓ Enable team context syncing
  ✓ Share knowledge base
  ✓ Create shared conventions file

─────────────────────────────────────────────

What should Beads track?
[*] Conversation history (Summaries)
[*] Git commits (Recent work)
[*] File changes (Context updates)
[*] Decisions made (Knowledge base)
[ ] Code patterns (Extract common patterns)
[*] TODOs and issues (Action items)

─────────────────────────────────────────────

Context retention:
(*) Keep last 30 days (Recommended)
( ) Keep last 90 days (Long-term projects)
( ) Keep everything (Searchable archive)

This affects storage and search speed.

─────────────────────────────────────────────

✨ Beads Configuration Complete!

Settings:
  • Auto-summarize: After 20 messages
  • Git integration: Enabled
  • Team sync: Enabled
  • Context retention: 30 days
  • Smart search: Enabled

Creating initial project context...
  ✓ Analyzed 234 files
  ✓ Processed 50 commits
  ✓ Generated knowledge base
  ✓ Created team context file

📝 Stored in .beads/
```

---

### 10. **Beads CLI Integration** 🔗

Deep integration with external Beads tool:

```yaml
# .agent.yml
beads:
  cli_integration: true
  cli_path: /usr/local/bin/bd

  # Auto-commands
  auto_commands:
    on_init: "bd init ."
    on_commit: "bd update-context"
    on_session_start: "bd status"
    on_session_end: "bd save-summary"

  # Sync settings
  sync:
    auto: true
    frequency: "on_commit"  # or "hourly" | "daily"
    remote: "origin/beads"  # Git branch for context
```

**Commands Available:**
```bash
# During init
bd init .                    # Initialize beads for project
bd analyze                   # Analyze project structure
bd generate-context          # Create initial context

# During development
bd status                    # Show current context
bd summary                   # Show today's summary
bd search "authentication"   # Search context
bd update                    # Refresh from git

# Session management
bd start-session             # Begin new session
bd end-session              # Save and summarize
bd export                    # Export to markdown

# Team features
bd sync                      # Sync team context
bd share                     # Share current context
bd diff                      # Show context changes
```

---

## Implementation Plan

### Phase 1: Basic Integration ✅
```python
# In handle_init()
def init_with_beads(project_config):
    # 1. Detect Beads CLI
    beads_available = detect_beads_cli()

    # 2. Prompt for installation if missing
    if not beads_available:
        if prompt_install_beads():
            install_beads()

    # 3. Configure based on project
    beads_config = configure_beads(project_analysis)

    # 4. Initialize Beads project
    if beads_available:
        subprocess.run(["bd", "init", "."])
        subprocess.run(["bd", "analyze"])

    # 5. Generate initial context
    create_project_context(project_config)

    # 6. Add to config
    project_config["beads"] = beads_config
```

### Phase 2: Smart Configuration 🧠
- Project analysis-based settings
- Auto-detect team vs solo
- Smart defaults by project type
- Context file selection

### Phase 3: Deep Integration 🔗
- Git hooks for auto-updates
- Session management
- Multi-layer context
- Semantic search

### Phase 4: Team Features 👥
- Shared context files
- Auto-merge
- Conflict resolution
- Team dashboard

---

## Configuration Examples

### Solo Developer, Small Project
```yaml
beads:
  enabled: true
  max_messages: 15
  summary_threshold: 10
  cli_integration: false  # Not needed for small projects
  auto_summarize: false   # Manual control
```

### Team, Large Active Project
```yaml
beads:
  enabled: true
  max_messages: 30
  summary_threshold: 20

  cli_integration: true
  auto_update_context: true

  git_integration: true
  include_commits: 20

  team_sync:
    enabled: true
    shared_context: .beads/team-context.md
    auto_merge: true

  search:
    enabled: true
    semantic: true
    index_files: true

  retention:
    days: 90
    archive: true
```

### Documentation/Writing Project
```yaml
beads:
  enabled: true
  max_messages: 25
  summary_threshold: 15

  # Focus on content, not code
  watch_files:
    - "docs/**/*.md"
    - "*.md"

  categories:
    - writing
    - editing
    - research

  export:
    format: markdown
    auto_export: true
    output: docs/writing-log.md
```

---

## User Experience

### First Time Init
```
$ agent chat
$ /init

╭────────────────────────────────────────────╮
│ 🚀 Project Initialization Wizard          │
╰────────────────────────────────────────────╯

🔍 Checking for Beads CLI...
  ⚠️  Beads CLI not found

Beads provides persistent project memory!
  • Never lose context across sessions
  • Automatic conversation summaries
  • Team-shared knowledge base

Install Beads? (Recommended)
(*) Yes, install now (1 minute)
( ) No, skip Beads features

Installing Beads...
  ✓ Downloaded bd CLI
  ✓ Installed to /usr/local/bin/bd
  ✓ Verified installation

Initializing Beads for your project...
  ✓ Created .beads/ directory
  ✓ Analyzed project structure
  ✓ Generated initial context
  ✓ Configured git hooks

🎉 Beads is ready!

Next time you start a conversation, I'll have full context
about your project, recent work, and team decisions!
```

### Subsequent Sessions
```
$ agent chat

📚 Loading project context...
  ✓ Project: MyApp API (FastAPI)
  ✓ Recent work: 5 commits today
  ✓ Active context: Authentication system
  ✓ Team updates: 2 new decisions

You ➜ let's continue working on the password reset

[Agent has full context from:
 - Last session summaries
 - Recent git commits
 - Team knowledge base
 - Related code files]

Agent: I see we started implementing password reset yesterday.
       Based on your last session, you were working on email
       verification. Let's continue with...
```

---

## Benefits Summary

### For Individual Developers
- ✅ Never lose context between sessions
- ✅ Automatic conversation summaries
- ✅ Git-aware context updates
- ✅ Searchable conversation history
- ✅ Smart project memory

### For Teams
- ✅ Shared project knowledge base
- ✅ Synchronized context across team
- ✅ Documented decisions and patterns
- ✅ Onboarding new team members
- ✅ Consistent coding standards

### For Projects
- ✅ Long-term project memory
- ✅ Architecture documentation
- ✅ Pattern extraction
- ✅ Progress tracking
- ✅ Knowledge accumulation

---

This design makes Beads an **invisible, intelligent layer** that ensures you never lose project context, whether you're working solo or with a team! 🚀

What aspects would you like to prioritize for the first implementation?
