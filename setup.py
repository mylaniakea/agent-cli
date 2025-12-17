from setuptools import find_packages, setup

setup(
    name="agent-cli",
    version="0.1.0",
    description="A custom LLM CLI with local and external agent support",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "agent-cli=agent_cli.cli:main",
        ],
    },
    python_requires=">=3.8",
)
