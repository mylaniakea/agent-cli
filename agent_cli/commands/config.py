from pathlib import Path

from rich.prompt import Confirm

from agent_cli.command_registry import register_command
from agent_cli.commands.constants import (
    CONTEXT_KEY_AGENT,
    CONTEXT_KEY_CONFIG,
    CONTEXT_KEY_MODEL,
    CONTEXT_KEY_PROVIDER,
    CONTEXT_KEY_STREAM,
)
from agent_cli.ui import ui


@register_command(
    name="model",
    description="Switch to a different model or show current model",
    usage="/model [name]",
    aliases=["m"],
    category="config",
    detailed_help="Switch to a different model or show the current model.\n" \
    "Examples:\n" \
    "  /model          - Show current model\n" \
    "  /model mistral  - Switch to mistral model",
)
def handle_model(command: str, context: dict) -> bool:
    """Handle /model command."""
    from agent_cli.agents import AgentFactory

    parts = command.split(None, 1)
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")

    if not config:
        ui.print_error("Configuration not available.")
        return True

    if len(parts) > 1:
        # Switch model
        new_model = parts[1]
        try:
            # Try to create agent with new model to validate
            test_agent = AgentFactory.create(current_provider, new_model, config)
            context[CONTEXT_KEY_MODEL] = new_model
            context[CONTEXT_KEY_AGENT] = test_agent
            ui.print_success(f"Switched to model: {new_model}")
            # Load Ollama model if using ollama provider
            if current_provider == "ollama":
                from agent_cli.ollama_manager import get_ollama_manager

                get_ollama_manager().load_model(new_model)
        except Exception as e:
            ui.print_error(f"Error switching model: {e}")
    else:
        # Show current model
        ui.print_info(f"Current model: {current_model}")

    return True


@register_command(
    name="provider",
    description="Switch to a different provider or show current provider",
    usage="/provider [name]",
    aliases=["p"],
    category="config",
    detailed_help="Switch to a different provider or show the current provider.\n" \
    "Available providers: ollama, openai, anthropic, google\n" \
    "Examples:\n" \
    "  /provider         - Show current provider\n" \
    "  /provider openai  - Switch to OpenAI provider",
)
def handle_provider(command: str, context: dict) -> bool:
    """Handle /provider command."""
    from agent_cli.agents import AgentFactory

    parts = command.split(None, 1)
    config = context.get(CONTEXT_KEY_CONFIG)
    current_provider = context.get(CONTEXT_KEY_PROVIDER, "")
    current_model = context.get(CONTEXT_KEY_MODEL, "")

    if not config:
        ui.print_error("Configuration not available.")
        return True

    if len(parts) > 1:
        new_provider = parts[1].lower()
        if new_provider in ["ollama", "openai", "anthropic", "google"]:
            try:
                # Try to create agent with new provider to validate
                test_agent = AgentFactory.create(new_provider, current_model, config)
                context[CONTEXT_KEY_PROVIDER] = new_provider
                context[CONTEXT_KEY_AGENT] = test_agent
                ui.print_success(f"Switched to provider: {new_provider}")
                # Load Ollama model if switched to ollama
                if new_provider == "ollama":
                    from agent_cli.ollama_manager import get_ollama_manager

                    get_ollama_manager().load_model(current_model)
            except Exception as e:
                ui.print_error(f"Error switching provider: {e}")
        else:
            ui.print_error("Invalid provider. Choose from: ollama, openai, anthropic, google")
    else:
        # Show current provider
        ui.print_info(f"Current provider: {current_provider}")

    return True


@register_command(
    name="stream",
    description="Toggle streaming mode on/off",
    usage="/stream",
    aliases=["s"],
    category="config",
    detailed_help="Toggle streaming mode on or off.\n" \
    "When enabled, responses are streamed token by token.\n" \
    "When disabled, responses are returned all at once.",
)
def handle_stream(command: str, context: dict) -> bool:
    """Handle /stream command."""
    current_stream = context.get(CONTEXT_KEY_STREAM, False)
    context[CONTEXT_KEY_STREAM] = not current_stream
    ui.print_info(f"Streaming mode: {'enabled' if context[CONTEXT_KEY_STREAM] else 'disabled'}")
    return True

@register_command(
    name="set",
    description="Set a configuration value",
    usage="/set KEY=value",
    aliases=[],
    category="config",
    detailed_help="Set a configuration value for the current session and config.ini.\n" \
    "Environment variables still take precedence.\n" \
    "Examples:\n" \
    "  /set OLLAMA_BASE_URL=http://localhost:11434\n" \
    "  /set THEME=dracula",
)
def handle_set(command: str, context: dict) -> bool:
    """Handle /set command."""
    config = context.get(CONTEXT_KEY_CONFIG)
    if not config:
        ui.print_error("Configuration not available.")
        return True

    # Parse command: /set KEY=value
    parts = command.split(None, 1)
    if len(parts) < 2:
        ui.print_info("Usage: /set <key>=<value>")
        ui.print_info("Example: /set OLLAMA_BASE_URL=http://192.168.1.100:11434")
        return True

    # Parse key=value
    assignment = parts[1]
    if "=" not in assignment:
        ui.print_error("Invalid format. Use KEY=value")
        # Check for user confusion
        if "MODEL" in assignment.upper() or "PROVIDER" in assignment.upper():
            ui.print_info("Did you mean to use /model or /provider?")
        return True

    key, value = assignment.split("=", 1)
    key = key.strip()
    value = value.strip()

    # Validation helpers
    if key.upper() == "MODEL":
        ui.print_warning(
            "Setting 'MODEL' in config only changes the default. Use /model to switch immediately."
        )

    # Warn about API keys
    if "API_KEY" in key.upper():
        ui.print_warning("API keys should be set via environment variables for security.")
        if not Confirm.ask("Continue anyway?", default=False, console=ui.console):
            ui.print_info("Cancelled.")
            return True

    try:
        config.set_value(key, value)
        ui.print_success(f"Set {key} = {value}")
        ui.print_info("Note: This value is saved to config.ini and will persist.")
        ui.print_info("Environment variables take precedence over config file values.")
    except Exception as e:
        ui.print_error(f"Error setting configuration: {e}")

    return True

@register_command(
    name="init",
    description="Initialize project configuration with intelligent wizard",
    usage="/init [provider] [--quick] [--format yaml|markdown] [--analyze]",
    aliases=[],
    category="config",
)
def handle_init(command: str, **kwargs) -> bool:
    """Initialize project configuration file with intelligent wizard."""
    ui = kwargs.get("ui")

    if not ui:
        return True

    from agent_cli.interactive_select import SingleSelect
    from agent_cli.project_config import ProjectConfig
    from agent_cli.project_detector import detect_project
    from agent_cli.templates import get_template_library

    # Parse command
    parts = command.split()
    provider = None
    format_type = "markdown"  # default
    quick_mode = "--quick" in parts
    analyze = "--analyze" in parts or not any(p in parts[1:] for p in ["openai", "anthropic", "google", "ollama"])

    for i, part in enumerate(parts[1:], 1):
        if part.startswith("--format="):
            format_type = part.split("=")[1]
        elif part in ["--format", "-f"]:
            if i + 1 < len(parts):
                format_type = parts[i + 1]
        elif part not in ["--quick", "--analyze", "--format", "-f"] and not provider:
            provider = part

    # Check if config already exists
    existing = ProjectConfig.find_project_config()
    if existing:
        ui.console.print(f"\n[yellow]Warning: Project config already exists:[/yellow] {existing}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            ui.console.print("[dim]Cancelled[/dim]")
            return True

    # Show wizard header
    ui.console.print("\n╭────────────────────────────────────────────╮")
    ui.console.print("│ 🚀 Project Initialization Wizard          │")
    ui.console.print("╰────────────────────────────────────────────╯\n")

    # Analyze project if requested or no provider specified
    analysis = None
    if analyze:
        ui.console.print("[cyan]🔍 Analyzing your project...[/cyan]\n")
        try:
            analysis = detect_project(Path.cwd())
            ui.console.print(analysis.get_summary())
            ui.console.print()
        except Exception as e:
            ui.console.print(f"[yellow]Warning: Could not analyze project: {e}[/yellow]\n")

    # Get template library
    template_lib = get_template_library()

    # Provider selection
    if not provider:
        provider_options = [
            {"key": "anthropic", "label": "🧠 Anthropic (Claude 3.5)",
             "description": "Best for coding, reasoning, and complex tasks"},
            {"key": "openai", "label": "🤖 OpenAI (GPT-4o, o1)",
             "description": "Excellent all-rounder with strong performance"},
            {"key": "google", "label": "✨ Google (Gemini 1.5)",
             "description": "Fast and cost-effective with large context"},
            {"key": "ollama", "label": "🦙 Ollama (Local)",
             "description": "Privacy-focused local models"},
        ]

        # Highlight recommended provider if we have analysis
        if analysis and analysis.recommended_provider:
            for opt in provider_options:
                if opt["key"] == analysis.recommended_provider:
                    opt["label"] = opt["label"] + " [bold cyan](Recommended)[/bold cyan]"
                    # Move to front
                    provider_options.remove(opt)
                    provider_options.insert(0, opt)
                    break

        ui.console.print("[bold]Select your PRIMARY provider:[/bold]")
        selector = SingleSelect(provider_options)
        selected_provider = selector.show()

        if not selected_provider:
            ui.console.print("[dim]Cancelled[/dim]")
            return True

        provider = selected_provider

    # Template selection
    template = None
    if not quick_mode:
        # Get recommended template from analysis or provider
        recommended_template_id = None
        if analysis and analysis.recommended_template:
            recommended_template_id = analysis.recommended_template

        # Get templates for selection
        categories = template_lib.get_categories()
        template_options = []

        for template_obj in template_lib.list_templates():
            label = f"{template_obj.name}"
            if template_obj.id == recommended_template_id:
                label = f"{label} [bold cyan](Recommended)[/bold cyan]"

            template_options.append({
                "key": template_obj.id,
                "label": label,
                "description": template_obj.description
            })

        ui.console.print("\n[bold]Select a project template:[/bold]")
        selector = SingleSelect(template_options)
        selected_template_id = selector.show()

        if not selected_template_id:
            ui.console.print("[dim]Using default template[/dim]\n")
        else:
            template = template_lib.get_template(selected_template_id)

    # Format selection
    if not quick_mode:
        ui.console.print("\n[bold]Select configuration format:[/bold]")
        format_options = [
            {"key": "markdown", "label": "📄 Markdown (claude.md, gpt.md, etc.)",
             "description": "Human-friendly, easy to read and edit"},
            {"key": "yaml", "label": "📋 YAML (.agent.yml)",
             "description": "Structured, machine-readable format"},
        ]
        selector = SingleSelect(format_options)
        selected_format = selector.show()

        if selected_format:
            format_type = selected_format

    # Create config
    ui.console.print("\n[cyan]✨ Creating project configuration...[/cyan]\n")

    try:
        # Use template if selected
        if template:
            # Create config with template settings
            config_content = _create_config_from_template(
                provider=provider,
                template=template,
                format_type=format_type,
                analysis=analysis
            )

            # Determine filename
            if format_type == "yaml":
                config_path = Path.cwd() / ".agent.yml"
            else:
                config_path = Path.cwd() / f"{provider}.md"

            config_path.write_text(config_content)
        else:
            # Use default config creation
            config_path = ProjectConfig.create_project_config(
                provider.lower(),
                format=format_type
            )

        ui.print_success(f"Created project config: {config_path}")

        # Generate initial project context
        if not quick_mode and analysis:
            try:
                from agent_cli.context_manager import initialize_project_context

                ui.console.print("\n[cyan]📝 Generating project context...[/cyan]")

                context_info = {
                    "name": Path.cwd().name,
                    "primary_language": analysis.primary_language,
                    "frameworks": analysis.frameworks,
                    "complexity": analysis.complexity,
                    "total_loc": analysis.total_loc,
                    "dependency_files": analysis.dependency_files,
                    "has_tests": analysis.has_tests,
                    "has_docs": analysis.has_docs,
                    "has_ci": analysis.has_ci,
                }

                context_file = initialize_project_context(Path.cwd(), context_info)
                ui.console.print(f"  ✓ Created context file: {context_file.relative_to(Path.cwd())}")
            except Exception as e:
                ui.console.print(f"  [yellow]Warning: Could not generate context: {e}[/yellow]")

        # Offer to install git hooks
        if not quick_mode and analysis and analysis.has_git:
            try:
                ui.console.print("\n[cyan]🔗 Git hooks setup[/cyan]")
                response = input("  Install git hooks for automatic context updates? (Y/n): ").strip().lower()

                if response in ["", "y", "yes"]:
                    from agent_cli.git_hooks import install_git_hooks

                    result = install_git_hooks(Path.cwd())

                    if result["success"]:
                        if result["installed"]:
                            ui.console.print(f"  ✓ Installed hooks: {', '.join(result['installed'])}")
                        if result["skipped"]:
                            ui.console.print(f"  ⊘ Already installed: {', '.join(result['skipped'])}")
                    else:
                        ui.console.print(f"  [yellow]Warning: {result.get('error', 'Unknown error')}[/yellow]")
            except Exception as e:
                ui.console.print(f"  [yellow]Warning: Could not install git hooks: {e}[/yellow]")

        # Show next steps
        ui.console.print("\n[bold cyan]🎉 Project initialized successfully![/bold cyan]\n")
        ui.console.print("[bold]Next steps:[/bold]")
        ui.console.print(f"  • Edit [cyan]{config_path.name}[/cyan] to customize settings")
        ui.console.print("  • Use [cyan]/chat[/cyan] to start coding with project context")
        ui.console.print("  • Use [cyan]/fallback[/cyan] to add a backup provider")

        if template:
            ui.console.print(f"\n[dim]Template: {template.name}[/dim]")
            ui.console.print(f"[dim]Use cases: {', '.join(template.example_use_cases)}[/dim]")

    except Exception as e:
        ui.print_error(f"Failed to create config: {e}")

    return True


def _create_config_from_template(provider: str, template, format_type: str, analysis=None) -> str:
    """Create configuration content from a template.

    Args:
        provider: Provider name
        template: ProjectTemplate object
        format_type: 'yaml' or 'markdown'
        analysis: Optional ProjectAnalysis

    Returns:
        Configuration file content as string
    """
    if format_type == "yaml":
        # YAML format
        content = f"""# Agent CLI Project Configuration
# Auto-generated from template: {template.name}

provider: {provider}
model: {template.model}
temperature: {template.temperature}

# System prompt for this project
system_prompt: |
{chr(10).join('  ' + line for line in template.system_prompt.split(chr(10)))}

# Context files to include automatically
context_files:
"""
        for pattern in template.context_files:
            content += f'  - "{pattern}"\n'

        content += "\n# Files to exclude from context\nexclude_patterns:\n"
        for pattern in template.exclude_patterns:
            content += f'  - "{pattern}"\n'

        content += "\n# Enabled tools\ntools:\n"
        for tool in template.tools:
            content += f"  - {tool}\n"

        # Add Beads configuration if we have analysis
        if analysis:
            content += "\n# Beads context management\nbeads:\n"
            content += "  enabled: true\n"
            content += "  max_messages: 20\n"
            content += "  summary_threshold: 15\n"

    else:
        # Markdown format
        content = f"""---
provider: {provider}
model: {template.model}
temperature: {template.temperature}
context_files:
"""
        for pattern in template.context_files:
            content += f'  - "{pattern}"\n'

        content += "exclude_patterns:\n"
        for pattern in template.exclude_patterns:
            content += f'  - "{pattern}"\n'

        content += "tools:\n"
        for tool in template.tools:
            content += f"  - {tool}\n"

        content += "---\n\n"
        content += template.system_prompt

        # Add project info if we have analysis
        if analysis and analysis.primary_language:
            content += "\n\n## Project Information\n\n"
            content += f"- **Language**: {analysis.primary_language.title()}\n"
            if analysis.frameworks:
                content += f"- **Frameworks**: {', '.join(analysis.frameworks)}\n"
            content += f"- **Complexity**: {analysis.complexity.title()}\n"

    return content


@register_command(
    name="hooks",
    description="Manage git hooks for automatic context updates",
    usage="/hooks [install|uninstall|list]",
    aliases=[],
    category="config",
    detailed_help="Manage git hooks:\n" \
    "- /hooks or /hooks list - Show installed hooks\n" \
    "- /hooks install - Install git hooks\n" \
    "- /hooks uninstall - Remove git hooks",
)
def handle_hooks(command: str, **kwargs) -> bool:
    """Handle /hooks command."""
    ui = kwargs.get("ui")
    if not ui:
        return True

    from agent_cli.git_hooks import GitHooksManager

    # Parse subcommand
    parts = command.split()
    subcommand = parts[1].lower() if len(parts) > 1 else "list"

    manager = GitHooksManager(Path.cwd())

    try:
        if not manager.is_git_repo():
            ui.print_error("Not a git repository")
            return True

        if subcommand in ["list", "status"]:
            # List hooks
            result = manager.list_hooks()

            ui.console.print("\n[bold]Git Hooks Status[/bold]\n")

            if result["agent_hooks"]:
                ui.console.print("[green]✓ Agent CLI Hooks:[/green]")
                for hook in result["agent_hooks"]:
                    ui.console.print(f"  • {hook}")
            else:
                ui.console.print("[dim]No Agent CLI hooks installed[/dim]")

            if result["other_hooks"]:
                ui.console.print("\n[dim]Other Hooks:[/dim]")
                for hook in result["other_hooks"]:
                    ui.console.print(f"  • {hook}")

            ui.console.print()

        elif subcommand == "install":
            # Install hooks
            ui.console.print("[cyan]Installing git hooks...[/cyan]\n")

            result = manager.install_hooks()

            if result["success"]:
                if result["installed"]:
                    ui.console.print("[green]✓ Installed:[/green]")
                    for hook in result["installed"]:
                        ui.console.print(f"  • {hook}")

                if result["skipped"]:
                    ui.console.print("\n[dim]Already installed:[/dim]")
                    for hook in result["skipped"]:
                        ui.console.print(f"  • {hook}")

                ui.print_success("\nGit hooks installed successfully")
            else:
                ui.print_error("Failed to install git hooks")
                for error in result.get("errors", []):
                    ui.console.print(f"  [red]✗[/red] {error}")

        elif subcommand == "uninstall":
            # Uninstall hooks
            ui.console.print("[cyan]Uninstalling git hooks...[/cyan]\n")

            result = manager.uninstall_hooks()

            if result["success"]:
                if result["removed"]:
                    ui.console.print("[green]✓ Removed:[/green]")
                    for hook in result["removed"]:
                        ui.console.print(f"  • {hook}")
                else:
                    ui.console.print("[dim]No Agent CLI hooks to remove[/dim]")

                ui.print_success("\nGit hooks uninstalled successfully")
            else:
                ui.print_error("Failed to uninstall git hooks")
                for error in result.get("errors", []):
                    ui.console.print(f"  [red]✗[/red] {error}")

        else:
            ui.print_error(f"Unknown subcommand: {subcommand}")
            ui.console.print("\nUsage:")
            ui.console.print("  /hooks [list] - Show installed hooks")
            ui.console.print("  /hooks install - Install git hooks")
            ui.console.print("  /hooks uninstall - Remove git hooks")

    except Exception as e:
        ui.print_error(f"Hooks error: {e}")

    return True


@register_command(
    name="setup",
    description="Interactive setup for a provider",
    usage="/setup <provider>",
    aliases=[],
    category="config",
)
def _handle_setup(context: dict, args: str) -> bool:
    """Handle the setup command - interactive provider onboarding."""
    from rich.console import Console

    from agent_cli.onboarding import ProviderOnboarding

    args = args.strip()
    if not args:
        console = Console()
        console.print("[yellow]Usage: /setup <provider>[/yellow]")
        console.print("Available providers: openai, anthropic, google, ollama")
        return True

    provider = args.lower()
    console = Console()

    result = ProviderOnboarding(console).run_onboarding(provider)

    if result:
        console.print("\n[green bold]🎉 Setup complete![/green bold]")
        console.print(f"[dim]Use /provider {provider} to switch to this provider[/dim]\n")

    return True

@register_command(
    name="keepalive",
    description="Set or show Ollama keep-alive duration",
    usage="/keepalive [duration]",
    aliases=["ka"],
    category="config",
    detailed_help="Set or show the keep-alive duration for Ollama models.\n" \
    "Examples:\n" \
    "  /keepalive       - Show current setting\n" \
    "  /keepalive 10m   - Keep model loaded for 10 minutes\n" \
    "  /keepalive 0     - Unload immediately after response\n\n" \
    "Only works with Ollama provider.",
)
def handle_keepalive(command: str, context: dict) -> bool:
    """Handle /keepalive command."""
    agent = context.get(CONTEXT_KEY_AGENT)
    parts = command.split()

    if len(parts) > 1:
        # Set keep-alive
        duration = parts[1]
        if hasattr(agent, "set_keep_alive"):
            agent.set_keep_alive(duration)
            ui.print_success(f"Keep-alive set to {duration}")
        else:
            ui.print_warning("Keep-alive is only supported for Ollama agents.")
    else:
        # Show current keep-alive
        if hasattr(agent, "keep_alive"):
            ui.print_info(f"Current keep-alive: {agent.keep_alive}")
        else:
            ui.print_info("Keep-alive: N/A (not supported for this provider)")
        ui.print_info("Usage: /keepalive <duration> (e.g., 10m, 1h, 0)")

    return True


@register_command(
    name="reasoning",
    description="Toggle reasoning display mode",
    usage="/reasoning",
    aliases=["think"],
    category="config",
    detailed_help="Toggle reasoning display mode.\n" \
    "When enabled, shows model reasoning process (if supported by model).",
)
def handle_reasoning(command: str, context: dict) -> bool:
    """Handle /reasoning command."""
    # For now, this is a placeholder for future reasoning display toggle
    ui.print_info("Reasoning display toggle: currently always enabled for raw stream.")
    ui.print_info("This feature will be enhanced in future updates.")
    return True
