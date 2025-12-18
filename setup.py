"""Setup file for agent-cli.

Note: This file is deprecated in favor of pyproject.toml.
Modern Python packaging uses pyproject.toml exclusively.
This file is kept for backward compatibility.
"""

from setuptools import find_packages, setup

setup(
    name="agent-cli",
    version="1.1.0",
    description="A custom LLM CLI with local and external agent support",
    author="Matthew",
    author_email="matthew@mylaniakea.com",
    packages=find_packages(),
    install_requires=[
        "anthropic",
        "click>=8.0.0",
        "google-generativeai",
        "openai",
        "prompt_toolkit>=3.0.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "agent-cli=agent_cli.cli:main",
        ],
    },
    python_requires=">=3.9",
)
