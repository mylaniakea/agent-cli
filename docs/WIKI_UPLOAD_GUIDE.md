# GitHub Wiki Upload Guide

This guide helps you upload the documentation to your GitHub wiki.

## Quick Method: Clone Wiki Repository

GitHub wikis are stored in a separate git repository. Here's how to upload:

### Step 1: Clone the Wiki Repository

```bash
# Replace YOUR_USERNAME and YOUR_REPO with your actual values
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.wiki.git
cd YOUR_REPO.wiki
```

### Step 2: Copy Documentation Files

```bash
# From the agent-cli project root
cp ../agent-cli/docs/WIKI_HOME.md Home.md
cp ../agent-cli/docs/Installation.md Installation.md
cp ../agent-cli/docs/Quick-Start.md Quick-Start.md
cp ../agent-cli/docs/Architecture.md Architecture.md
cp ../agent-cli/docs/Development-Phases.md Development-Phases.md
cp ../agent-cli/docs/Command-Reference.md Command-Reference.md
```

### Step 3: Create Sidebar

Create `_Sidebar.md`:

```markdown
## Getting Started
- [[Home|Home]]
- [[Installation|Installation]]
- [[Quick-Start|Quick Start]]

## User Guides
- [[Command-Reference|Command Reference]]

## Development
- [[Architecture|Architecture]]
- [[Development-Phases|Development Phases]]
```

### Step 4: Create Footer (Optional)

Create `_Footer.md`:

```markdown
---

**Agent CLI** - A custom LLM CLI with local and external agent support

[GitHub Repository](https://github.com/YOUR_USERNAME/YOUR_REPO) | [Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)
```

### Step 5: Commit and Push

```bash
git add .
git commit -m "Add comprehensive documentation"
git push origin master
```

## Alternative: Manual Upload via GitHub Web Interface

1. Go to your repository on GitHub
2. Click on the "Wiki" tab
3. Click "New Page" for each documentation file
4. Copy content from `docs/` files
5. Save each page

## File Mapping

| Source File | Wiki Page Name |
|-------------|----------------|
| `docs/WIKI_HOME.md` | `Home.md` |
| `docs/Installation.md` | `Installation.md` |
| `docs/Quick-Start.md` | `Quick-Start.md` |
| `docs/Architecture.md` | `Architecture.md` |
| `docs/Development-Phases.md` | `Development-Phases.md` |
| `docs/Command-Reference.md` | `Command-Reference.md` |
| `docs/PROJECT_SUMMARY.md` | `Project-Summary.md` (optional) |

## Notes

- Wiki pages use `.md` extension
- Links between pages use `[[Page-Name]]` syntax
- The `_Sidebar.md` and `_Footer.md` files are special and automatically used by GitHub
- All documentation is ready in the `docs/` directory

