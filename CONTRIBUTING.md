# Contributing to Agent CLI

Thank you for your interest in contributing to Agent CLI! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- Git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/mpfaffenberger/agent-cli.git
cd agent-cli

# Install with development dependencies
make install
# or
uv pip install -e ".[dev]"
```

## Development Workflow

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific test file
pytest tests/unit/test_config.py

# Run tests in verbose mode
pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with ruff
make format

# Check linting
make lint

# Run type checker
make typecheck

# Run all checks (format, lint, typecheck, test)
make all
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
uv pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Code Style Guidelines

### Python Style

- Follow PEP 8 (enforced by ruff)
- Line length: 100 characters
- Use type hints for function signatures
- Write docstrings for public functions and classes

### Docstring Format

We use Google-style docstrings:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """Brief description of what the function does.

    More detailed description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (e.g., "Add", "Fix", "Update")
- Reference issues when applicable (e.g., "Fix #123")
- Add co-author line at the end if pair programming:
  ```
  Co-Authored-By: Name <email@example.com>
  ```

## Pull Request Process

1. **Fork and Branch**
   - Fork the repository
   - Create a feature branch: `git checkout -b feature/your-feature-name`

2. **Make Changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   make all  # Run all checks
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to GitHub and create a pull request
   - Fill out the PR template
   - Link related issues
   - Wait for CI checks to pass
   - Address review feedback

6. **PR Requirements**
   - All tests must pass
   - Code coverage should not decrease
   - Linting and type checking must pass
   - At least one approving review

## Adding New Features

### Adding a New Provider

1. Create agent class in `agent_cli/agents/`:
   ```python
   from agent_cli.agents.base import BaseAgent
   
   class NewProviderAgent(BaseAgent):
       def chat(self, messages, model, **kwargs):
           # Implementation
           pass
   ```

2. Register in `agent_cli/agents/factory.py`
3. Add models to `agent_cli/models.json`
4. Write tests in `tests/unit/` and `tests/integration/`
5. Update documentation

### Adding a New Command

1. Register command in `agent_cli/interactive_commands.py`:
   ```python
   @register_command(
       name="mycommand",
       description="Description of command",
       usage="/mycommand <args>",
       aliases=["mc"],
       category="utility"
   )
   def handle_mycommand(command: str, **kwargs) -> bool:
       # Implementation
       return True
   ```

2. Add tests
3. Update help text

## Testing Guidelines

### Test Organization

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Use descriptive test names: `test_function_does_specific_thing`

### Writing Tests

```python
import pytest

def test_feature_works_correctly():
    """Test that feature works as expected."""
    result = my_function(input_value)
    assert result == expected_value

def test_feature_raises_error_on_invalid_input():
    """Test that feature raises appropriate error."""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

### Mocking

Use `pytest-mock` for mocking external dependencies:

```python
def test_api_call(mocker):
    """Test API call with mocked response."""
    mock_response = mocker.Mock()
    mocker.patch('module.api_call', return_value=mock_response)
    # Test code
```

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add comments for complex logic
- Update CHANGELOG.md

### Documentation Style

- Use clear, concise language
- Include examples where helpful
- Keep documentation up-to-date with code

## Getting Help

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: matthew@mylaniakea.com

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- Git commit history
- GitHub contributors page
- Release notes (for significant contributions)

Thank you for contributing to Agent CLI! 🎉
