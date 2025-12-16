# GitHub Wiki Setup Guide

This guide explains how to set up the GitHub wiki using the documentation files in the `docs/` directory.

## Wiki Structure

The documentation is organized as follows:

```
Home
├── Installation
├── Quick-Start
├── Basic-Usage
├── Configuration
├── Interactive-Mode
├── Streaming
├── File-References
├── Session-Management
├── Model-Factory
├── MCP-Integration
├── Message-History
├── Command-Registry
├── Architecture
├── Development-Phases
├── Adding-Providers
├── Contributing
├── Command-Reference
├── Configuration-Reference
└── API-Reference
```

## Setup Steps

### 1. Enable Wiki

1. Go to your GitHub repository
2. Click on "Settings"
3. Scroll to "Features" section
4. Enable "Wikis"

### 2. Create Pages

For each markdown file in `docs/`, create a corresponding wiki page:

| File | Wiki Page Name |
|------|----------------|
| `WIKI_HOME.md` | Home |
| `Installation.md` | Installation |
| `Quick-Start.md` | Quick-Start |
| `Architecture.md` | Architecture |
| `Development-Phases.md` | Development-Phases |
| `Command-Reference.md` | Command-Reference |

### 3. Add Sidebar

Create a `_Sidebar.md` file in the wiki with:

```markdown
## Getting Started
- [[Home|Home]]
- [[Installation|Installation]]
- [[Quick-Start|Quick-Start]]

## User Guides
- [[Command-Reference|Command Reference]]
- [[Configuration|Configuration]]

## Development
- [[Architecture|Architecture]]
- [[Development-Phases|Development Phases]]
- [[Contributing|Contributing]]
```

### 4. Add Footer

Create a `_Footer.md` file:

```markdown
---

**Agent CLI** - A custom LLM CLI with local and external agent support

[GitHub Repository](https://github.com/yourusername/agent-cli) | [Issues](https://github.com/yourusername/agent-cli/issues)
```

## Content Files

All documentation files are ready in `docs/`:

- ✅ `WIKI_HOME.md` - Main landing page
- ✅ `Installation.md` - Installation instructions
- ✅ `Quick-Start.md` - Quick start guide
- ✅ `Architecture.md` - System architecture
- ✅ `Development-Phases.md` - Development history
- ✅ `Command-Reference.md` - Complete command reference
- ✅ `PROJECT_SUMMARY.md` - Project completion summary

## Additional Pages to Create

You may want to create these additional pages:

- **Basic-Usage.md** - Detailed usage examples
- **Configuration.md** - Configuration guide (use CONFIG_GUIDE.md content)
- **Interactive-Mode.md** - Interactive mode guide
- **Streaming.md** - Streaming feature guide
- **File-References.md** - File reference syntax
- **Session-Management.md** - Session management guide
- **Model-Factory.md** - Model factory documentation
- **MCP-Integration.md** - MCP integration guide
- **Message-History.md** - History management guide
- **Adding-Providers.md** - Guide for adding new providers
- **Contributing.md** - Contribution guidelines

## Tips

1. **Use relative links**: Wiki pages can link to each other using `[[Page-Name]]`
2. **Keep it updated**: Update wiki when adding new features
3. **Add examples**: Include code examples in guides
4. **Cross-reference**: Link related pages together

## Quick Copy-Paste

To quickly set up the wiki, you can:

1. Clone the wiki repository:
   ```bash
   git clone https://github.com/yourusername/agent-cli.wiki.git
   ```

2. Copy files from `docs/` to wiki repo:
   ```bash
   cp docs/*.md agent-cli.wiki/
   ```

3. Rename files to match wiki page names
4. Commit and push:
   ```bash
   cd agent-cli.wiki
   git add .
   git commit -m "Add documentation"
   git push
   ```

