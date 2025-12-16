# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Methods

### Method 1: Development Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-cli.git
cd agent-cli

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Method 2: Direct Installation

```bash
# Install from source
pip install git+https://github.com/yourusername/agent-cli.git
```

### Method 3: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Verify Installation

```bash
agent-cli --version
agent-cli --help
```

## Configuration

After installation, configure your API keys and settings:

### Option 1: Environment Variables

```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
export GOOGLE_API_KEY=your_key_here
export OLLAMA_BASE_URL=http://localhost:11434
```

### Option 2: .env File

Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

### Option 3: Config File

Use the `/set` command in interactive mode or edit `~/.agent-cli/config.ini`:

```ini
[agent-cli]
OPENAI_API_KEY=your_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

See [Configuration Guide](Configuration) for details on configuration priority.

## Ollama Setup (Optional)

If using Ollama for local models:

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Start Ollama service (usually runs automatically)
4. Verify: `agent-cli --provider ollama --model llama2 "test"`

## Next Steps

- Read the [Quick Start Guide](Quick-Start)
- Check [Basic Usage](Basic-Usage) for examples
- Explore [Interactive Mode](Interactive-Mode)

