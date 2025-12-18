"""Interactive onboarding flow during app startup."""

from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

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

    # Provider selection with keyboard + spacebar multi-select
    from agent_cli.interactive_select import MultiSelect

    provider_options = [
        {"key": "openai", "label": "OpenAI (GPT-4, o1)", "icon": "🤖"},
        {"key": "anthropic", "label": "Anthropic (Claude)", "icon": "🧠"},
        {"key": "google", "label": "Google (Gemini)", "icon": "✨"},
        {"key": "ollama", "label": "Ollama (Local)", "icon": "🦙"},
    ]

    multi_select = MultiSelect(
        options=provider_options,
        title="Select providers to configure:",
        console=console,
    )

    providers = multi_select.show()

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
        console.print("\n[green bold]✅ Setup complete![/green bold]")
        console.print(f"[dim]Configured providers: {', '.join(configured)}[/dim]\n")

        # Select primary provider
        primary_provider = configured[0]  # Default to first
        if len(configured) > 1:
            from agent_cli.interactive_select import SingleSelect

            primary_options = [
                {"key": p, "label": _get_provider_display_name(p), "icon": _get_provider_icon(p)}
                for p in configured
            ]

            console.print()
            single_select = SingleSelect(
                options=primary_options,
                title="Select your PRIMARY provider:",
                instruction="This will be your default provider. Use ↑/↓, then ENTER",
                default_index=0,
                console=console,
            )

            selected = single_select.show()
            if selected:
                primary_provider = selected

        # Select fallback provider (optional)
        fallback_provider = None
        if len(configured) > 1:
            console.print()
            fallback_options = [
                {"key": "none", "label": "No fallback (skip)", "icon": "⊘"}
            ] + [
                {"key": p, "label": _get_provider_display_name(p), "icon": _get_provider_icon(p)}
                for p in configured
                if p != primary_provider
            ]

            single_select = SingleSelect(
                options=fallback_options,
                title="Select a FALLBACK provider (optional):",
                instruction="Used when primary provider fails. Use ↑/↓, then ENTER",
                default_index=0,
                console=console,
            )

            selected = single_select.show()
            if selected and selected != "none":
                fallback_provider = selected

        # Save primary and fallback to config
        from agent_cli.config import Config

        config = Config()
        config.set_value("PRIMARY_PROVIDER", primary_provider)

        if fallback_provider:
            config.set_value("FALLBACK_PROVIDER", fallback_provider)
            console.print(
                f"\n[green]✓[/green] Primary: {_get_provider_icon(primary_provider)} {primary_provider.title()}"
            )
            console.print(
                f"[green]✓[/green] Fallback: {_get_provider_icon(fallback_provider)} {fallback_provider.title()}\n"
            )
        else:
            console.print(
                f"\n[green]✓[/green] Primary: {_get_provider_icon(primary_provider)} {primary_provider.title()}\n"
            )

        # Return primary provider
        return primary_provider

    return None


def _get_provider_icon(provider: str) -> str:
    """Get icon for provider."""
    icons = {
        "openai": "🤖",
        "anthropic": "🧠",
        "google": "✨",
        "ollama": "🦙",
    }
    return icons.get(provider, "💬")


def _get_provider_display_name(provider: str) -> str:
    """Get display name for provider."""
    names = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "ollama": "Ollama",
    }
    return names.get(provider, provider.title())


def maybe_run_onboarding(console: Console) -> Optional[str]:
    """Check if onboarding is needed and run it if so.

    Returns default provider if onboarding ran, None otherwise.
    """
    if check_needs_onboarding():
        return run_interactive_onboarding(console)
    return None
