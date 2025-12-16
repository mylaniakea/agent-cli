#!/bin/bash
# Script to set up GitHub wiki from docs/ directory
# Usage: ./setup_wiki.sh <github-username> <repo-name>

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <github-username> <repo-name>"
    echo "Example: $0 matthew agent-cli"
    exit 1
fi

USERNAME=$1
REPO=$2
WIKI_REPO="${REPO}.wiki"

echo "Setting up GitHub wiki for ${USERNAME}/${REPO}"
echo "=========================================="

# Clone wiki repository
echo "Cloning wiki repository..."
if [ -d "$WIKI_REPO" ]; then
    echo "Wiki directory exists, updating..."
    cd "$WIKI_REPO"
    git pull
    cd ..
else
    git clone "https://github.com/${USERNAME}/${WIKI_REPO}.git"
fi

# Copy documentation files
echo "Copying documentation files..."
cp docs/WIKI_HOME.md "$WIKI_REPO/Home.md"
cp docs/Installation.md "$WIKI_REPO/Installation.md"
cp docs/Quick-Start.md "$WIKI_REPO/Quick-Start.md"
cp docs/Architecture.md "$WIKI_REPO/Architecture.md"
cp docs/Development-Phases.md "$WIKI_REPO/Development-Phases.md"
cp docs/Command-Reference.md "$WIKI_REPO/Command-Reference.md"
cp docs/PROJECT_SUMMARY.md "$WIKI_REPO/Project-Summary.md"

# Create sidebar
echo "Creating sidebar..."
cat > "$WIKI_REPO/_Sidebar.md" << 'EOF'
## Getting Started
- [[Home|Home]]
- [[Installation|Installation]]
- [[Quick-Start|Quick Start]]

## User Guides
- [[Command-Reference|Command Reference]]

## Development
- [[Architecture|Architecture]]
- [[Development-Phases|Development Phases]]
- [[Project-Summary|Project Summary]]
EOF

# Create footer
echo "Creating footer..."
cat > "$WIKI_REPO/_Footer.md" << EOF
---

**Agent CLI** - A custom LLM CLI with local and external agent support

[GitHub Repository](https://github.com/${USERNAME}/${REPO}) | [Issues](https://github.com/${USERNAME}/${REPO}/issues)
EOF

# Commit and push
echo "Committing and pushing wiki..."
cd "$WIKI_REPO"
git add .
git commit -m "Add comprehensive documentation from docs/" || echo "No changes to commit"
git push origin master

echo ""
echo "✅ Wiki setup complete!"
echo "View your wiki at: https://github.com/${USERNAME}/${REPO}/wiki"

