"""Interactive onboarding flow during app startup."""

from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.markdown import Markdown
from agent_cli.onboarding import ProviderOnboarding


def check_needs_onboarding() -> bool:
    """Check if any providers are configured."""
    import os

    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_google = bool(os.environ.get("GOOGLE_API_KEY"))
    has_ollama = bool(os.environ.get("OLLAMA_BASE_URL"))

    return not (has_openai or has_anthropic or has_google or has_ollama)


def run_interactive_onboarding(console: Console) -> Optional[str]:
    """Run interactive onboarding and return default provider.

    Returns the first configured provider as default, or None if cancelled.
    """
    # Welcome screen
    welcome = """
# 🚀 Welcome to Agent CLI!

It looks like this is your first time running the app.

Let's get you set up with your AI providers!

You can configure one or more providers:
- 🤖 **OpenAI** - GPT-4o, GPT-4o-mini, o1
- 🧠 **Anthropic** - Claude 3.5 Sonnet/Haiku
- ✨ **Google** - Gemini 1.5 Pro/Flash
- 🦙 **Ollama** - Run models locally (no API key)

**Multiple providers?** Configure as many as you like!
"""

    panel = Panel(
        Markdown(welcome),
        title="[bold cyan]🎉 First Run Setup[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()

    # Ask if they want to configure now
    if not Confirm.ask("Would you like to configure providers now?", default=True, console=console):
        console.print(
            "\n[yellow]No providers configured. You can run setup later with /setup <provider>[/yellow]\n"
        )
        return None

    # Provider selection with checkboxes
    console.print("\n[bold cyan]Select providers to configure:[/bold cyan]")
    console.print("[dim]Press space to select, enter when done[/dim]\n")

    # Simple multi-select using inquirer-style prompts
    providers = []

    if Confirm.ask("  🤖 OpenAI (GPT-4, o1)", default=False, console=console):
        providers.append("openai")

    if Confirm.ask("  🧠 Anthropic (Claude)", default=False, console=console):
        providers.append("anthropic")

    if Confirm.ask("  ✨ Google (Gemini)", default=False, console=console):
        providers.append("google")

    if Confirm.ask("  🦙 Ollama (Local)", default=False, console=console):
        providers.append("ollama")

    if not providers:
        console.print(
            "\n[yellow]No providers selected. You can run setup later with /setup <provider>[/yellow]\n"
        )
        return None

    # Configure each selected provider
    onboarding = ProviderOnboarding(console)
    configured = []

    for provider in providers:
        console.print(f"\n[bold]{'=' * 60}[/bold]")
        result = onboarding.run_onboarding(provider)
        if result:
            configured.append(provider)

    if configured:
        console.print(f"\n[green bold]✅ Setup complete![/green bold]")
        console.print(f"[dim]Configured providers: {', '.join(configured)}[/dim]\n")
        # Return first configured as default
        return configured[0]

    return None


def maybe_run_onboarding(console: Console) -> Optional[str]:
    """Check if onboarding is needed and run it if so.

    Returns default provider if onboarding ran, None otherwise.
    """
    if check_needs_onboarding():
        return run_interactive_onboarding(console)
    return None
