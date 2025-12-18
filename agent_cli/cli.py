"""Main CLI entry point - refactored for better encapsulation."""

import sys
from importlib.metadata import version
from pathlib import Path
from typing import Optional

import click

# Import interactive commands to register them
import agent_cli.commands  # noqa: F401
from agent_cli.agents import AgentFactory
from agent_cli.command_registry import handle_command
from agent_cli.commands.constants import (
    CONTEXT_KEY_AGENT,
    CONTEXT_KEY_CONFIG,
    CONTEXT_KEY_HISTORY,
    CONTEXT_KEY_MODEL,
    CONTEXT_KEY_PROVIDER,
    CONTEXT_KEY_STREAM,
    CONTEXT_KEY_SYSTEM_PROMPT,
)
from agent_cli.config import Config
from agent_cli.history_manager import add_to_history
from agent_cli.model_factory import ModelFactory
from agent_cli.session_manager import (
    get_session_state,
    save_session_state,
    update_session_state,
)
from agent_cli.ui import UI
from agent_cli.utils import process_file_references

# Constants
DUMMY_MODEL_NAME = "dummy"
EXIT_COMMANDS = ["exit", "quit"]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def build_command_context(
    agent, provider: str, model: str, stream: bool, history: list, config: Config, system_prompt
) -> dict:
    """Build context dictionary for command handlers."""
    return {
        CONTEXT_KEY_AGENT: agent,
        CONTEXT_KEY_PROVIDER: provider,
        CONTEXT_KEY_MODEL: model,
        CONTEXT_KEY_STREAM: stream,
        CONTEXT_KEY_HISTORY: history,
        CONTEXT_KEY_CONFIG: config,
        CONTEXT_KEY_SYSTEM_PROMPT: system_prompt,
    }


def create_agent_with_fallback(provider: str, model: str, config, system_prompt: str = None, ui=None):
    """Create agent with fallback provider support.

    Args:
        provider: Primary provider name
        model: Model name
        config: Configuration object
        system_prompt: Optional system prompt
        ui: Optional UI instance for displaying messages

    Returns:
        Agent instance (either from primary or fallback provider)

    Raises:
        Exception: If both primary and fallback providers fail
    """
    from agent_cli.agents.factory import AgentFactory

    # Try primary provider
    try:
        agent = AgentFactory.create(provider, model, config, system_prompt=system_prompt)
        return agent
    except Exception as primary_error:
        # Check if fallback provider is configured
        fallback_provider = config.fallback_provider

        if fallback_provider and fallback_provider != provider:
            if ui:
                ui.print_warning(
                    f"Primary provider '{provider}' failed: {str(primary_error)}"
                )
                ui.print_info(f"Attempting fallback to '{fallback_provider}'...")

            try:
                # Get default model for fallback provider
                fallback_model = _get_default_model_for_provider(fallback_provider, config)
                agent = AgentFactory.create(
                    fallback_provider, fallback_model, config, system_prompt=system_prompt
                )

                if ui:
                    ui.print_success(
                        f"✓ Using fallback provider: {fallback_provider} with model {fallback_model}"
                    )

                return agent
            except Exception as fallback_error:
                if ui:
                    ui.print_error(
                        f"Fallback provider '{fallback_provider}' also failed: {str(fallback_error)}"
                    )
                raise fallback_error
        else:
            # No fallback configured, re-raise primary error
            raise primary_error


def _get_default_model_for_provider(provider: str, config) -> str:
    """Get default model for a given provider."""
    provider = provider.lower()
    if provider == "ollama":
        return config.default_ollama_model
    elif provider == "openai":
        return config.default_openai_model
    elif provider == "anthropic":
        return config.default_anthropic_model
    elif provider == "google":
        return config.default_google_model
    else:
        return ""


def should_recreate_agent(
    old_provider: str,
    new_provider: str,
    old_model: str,
    new_model: str,
    old_prompt,
    new_prompt,
) -> bool:
    """Determine if agent needs recreation based on parameter changes."""
    return old_provider != new_provider or old_model != new_model or old_prompt != new_prompt


def setup_initial_provider_and_model(
    provider: Optional[str],
    model: Optional[str],
    config: Config,
    session_state: dict,
) -> tuple[str, str]:
    """Setup initial provider and model from CLI args, onboarding, or session state."""

    from dotenv import load_dotenv
    from rich.console import Console

    from agent_cli.interactive_onboarding import maybe_run_onboarding

    # Check if first-run onboarding is needed
    onboarding_provider = maybe_run_onboarding(Console())

    if onboarding_provider:
        # Reload .env file to pick up new variables
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)
        config = Config()  # Reload config

        # Get default model for onboarded provider
        if onboarding_provider == "ollama":
            onboarded_model = config.default_ollama_model
        elif onboarding_provider == "openai":
            onboarded_model = config.default_openai_model
        elif onboarding_provider == "anthropic":
            onboarded_model = config.default_anthropic_model
        elif onboarding_provider == "google":
            onboarded_model = config.default_google_model
        else:
            onboarded_model = config.default_ollama_model

        # CLI args override onboarding
        current_provider = provider or onboarding_provider
        current_model = model or onboarded_model
    else:
        # No onboarding, use session state or defaults
        current_provider = provider or session_state.get("provider") or "ollama"
        current_model = model or session_state.get("model") or config.default_ollama_model

    return current_provider, current_model


def load_and_setup_theme(config: Config, ui_instance: UI):
    """Load saved theme from config and apply it."""
    saved_theme = config.get_value("THEME")
    if saved_theme and saved_theme in ui_instance.theme_manager.get_available_themes():
        ui_instance.theme_manager.set_theme(saved_theme)


def populate_model_autocomplete(agent, ui_instance: UI):
    """Try to populate model list for autocomplete."""
    try:
        models = agent.list_models()
        if models:
            ui_instance.interactive_session.update_completion_models(models)
    except Exception:
        pass  # Fail silently for autocomplete loading


def handle_chat_response(
    agent,
    prompt: str,
    history: list,
    stream: bool,
    current_model: str,
    ui_instance: UI,
) -> str:
    """Handle chat response with streaming or non-streaming mode."""
    if stream:
        # Using a simple header for stream start
        ui_instance.console.print(f"\n[bold green]{current_model}[/bold green]:", end=" ")

        response_parts = []

        # Create a spinner while waiting for the first token
        with ui_instance.create_spinner(f"Activating {current_model}..."):
            stream_gen = agent.stream(prompt, history)
            try:
                first_token = next(stream_gen)
            except StopIteration:
                first_token = None

        # Start printing
        if first_token:
            ui_instance.print_stream_chunk(first_token)
            response_parts.append(first_token)

        for token in stream_gen:
            ui_instance.print_stream_chunk(token)
            response_parts.append(token)

        ui_instance.console.print("\n")
        return "".join(response_parts)
    else:
        with ui_instance.create_spinner("Thinking..."):
            response = agent.chat(prompt, history)
        ui_instance.print_agent_response(response, current_model)
        return response


def update_context_from_command(
    context: dict,
    current_provider: str,
    current_model: str,
    current_stream: bool,
    current_system_prompt,
) -> tuple[str, str, bool, any]:
    """Extract updated values from command context."""
    new_provider = context.get(CONTEXT_KEY_PROVIDER, current_provider)
    new_model = context.get(CONTEXT_KEY_MODEL, current_model)
    new_stream = context.get(CONTEXT_KEY_STREAM, current_stream)
    new_system_prompt = context.get(CONTEXT_KEY_SYSTEM_PROMPT, current_system_prompt)

    return new_provider, new_model, new_stream, new_system_prompt


# ============================================================================
# INTERACTIVE MODE
# ============================================================================


def run_interactive_mode(
    initial_provider: str,
    initial_model: str,
    initial_stream: bool,
    config: Config,
    ui_instance: UI,
):
    """Run the interactive chat loop."""
    current_provider = initial_provider
    current_model = initial_model
    current_stream = initial_stream
    current_system_prompt = None
    history: list[dict[str, str]] = []

    def create_agent():
        """Create agent with current settings, with fallback support."""
        return create_agent_with_fallback(
            current_provider,
            current_model,
            config,
            system_prompt=current_system_prompt,
            ui=ui_instance,
        )

    # Show welcome and info
    ui_instance.print_welcome()
    if current_stream:
        ui_instance.print_info("Streaming mode enabled.")

    agent = create_agent()

    # Load Ollama model if using ollama provider
    if current_provider == "ollama":
        from agent_cli.ollama_manager import get_ollama_manager

        get_ollama_manager().load_model(current_model)

    # Initialize interactive session status
    ui_instance.interactive_session.update_status(current_provider, current_model)

    # Load theme
    load_and_setup_theme(config, ui_instance)

    # Populate autocomplete
    populate_model_autocomplete(agent, ui_instance)

    # Main interactive loop
    while True:
        try:
            # Get user input
            user_input = ui_instance.interactive_session.prompt()

            # Handle exit
            if user_input.lower() in EXIT_COMMANDS:
                break

            # Handle empty input
            if not user_input.strip():
                continue

            # Handle commands starting with /
            if user_input.startswith("/"):
                command_context = build_command_context(
                    agent,
                    current_provider,
                    current_model,
                    current_stream,
                    history,
                    config,
                    current_system_prompt,
                )

                # Handle command via registry
                handled = handle_command(user_input, command_context)

                if handled:
                    # Extract updated values
                    (
                        new_provider,
                        new_model,
                        new_stream,
                        new_system_prompt,
                    ) = update_context_from_command(
                        command_context,
                        current_provider,
                        current_model,
                        current_stream,
                        current_system_prompt,
                    )

                    # Save to session if changed
                    if (
                        new_provider != current_provider
                        or new_model != current_model
                        or new_stream != current_stream
                    ):
                        update_session_state(
                            provider=new_provider,
                            model=new_model,
                            stream=new_stream,
                        )

                    # Check if agent needs recreation
                    agent_from_context = command_context.get(CONTEXT_KEY_AGENT)
                    if agent_from_context and agent_from_context != agent:
                        agent = agent_from_context
                    elif should_recreate_agent(
                        current_provider,
                        new_provider,
                        current_model,
                        new_model,
                        current_system_prompt,
                        new_system_prompt,
                    ):
                        # Update current values first
                        current_provider = new_provider
                        current_model = new_model
                        current_system_prompt = new_system_prompt
                        agent = create_agent()

                    # Update all current values
                    current_provider = new_provider
                    current_model = new_model
                    current_stream = new_stream
                    current_system_prompt = new_system_prompt

                    # Update status bar
                    ui_instance.interactive_session.update_status(current_provider, current_model)
                else:
                    ui_instance.print_error(
                        f"Unknown command: {user_input}. Type /help for available commands."
                    )
                continue

            # Process file references (@filename)
            processed_prompt, file_refs = process_file_references(user_input, ui_instance)

            # Update connection status
            ui_instance.interactive_session.update_status(
                current_provider, current_model, connected=True
            )

            # Get and handle response
            response = handle_chat_response(
                agent,
                processed_prompt,
                history,
                current_stream,
                current_model,
                ui_instance,
            )

            # Update conversation history
            history = add_to_history(history, "user", user_input)
            history = add_to_history(history, "assistant", response)

        except KeyboardInterrupt:
            # Cleanup Ollama if used
            if current_provider == "ollama":
                from agent_cli.ollama_manager import get_ollama_manager

                get_ollama_manager().cleanup()
            ui_instance.print_info("\nExiting...")
            break
        except Exception as e:
            ui_instance.interactive_session.update_status(
                current_provider, current_model, connected=False
            )
            ui_instance.print_error(f"{e}")


# ============================================================================
# NON-INTERACTIVE MODE
# ============================================================================


def run_non_interactive_mode(
    provider: str,
    model: str,
    prompt: str,
    stream: bool,
    config: Config,
    ui_instance: UI,
):
    """Run a single non-interactive prompt."""
    if not prompt:
        ui_instance.print_error("Prompt is required in non-interactive mode.")
        ui_instance.print_info("Run without --non-interactive for interactive mode or provide a prompt.")
        return

    # Process file references
    processed_prompt, file_refs = process_file_references(prompt, ui_instance)
    if file_refs:
        ui_instance.print_info(f"Including {len(file_refs)} file(s) in prompt...")

    try:
        agent = AgentFactory.create(provider, model, config)
        history: list[dict[str, str]] = []

        if stream:
            # Stream to stdout for piping
            for token in agent.stream(processed_prompt, history):
                sys.stdout.write(token)
                sys.stdout.flush()
            sys.stdout.write("\n")
        else:
            # Simple print for piping
            response = agent.chat(processed_prompt, history)
            print(response)
    except Exception as e:
        ui_instance.print_error(f"{e}")
        sys.exit(1)


# ============================================================================
# CLICK COMMANDS
# ============================================================================


@click.group()
@click.version_option(version=version("agent-cli"))
def cli():
    """Agent CLI - A custom LLM CLI with local and external agent support."""
    pass


@cli.command()
@click.option(
    "--provider",
    "-p",
    required=False,
    type=click.Choice(["ollama", "openai", "anthropic", "google"], case_sensitive=False),
    help="Provider to use. If not specified, uses last session provider.",
)
@click.option(
    "--model",
    "-m",
    required=False,
    help="Model name to use. If not specified, uses last session model.",
)
@click.option("--non-interactive", is_flag=True, help="Run in non-interactive mode (single prompt)")
@click.option("--stream", "-s", is_flag=True, help="Stream the response token by token")
@click.argument("prompt", required=False)
def chat(provider, model, non_interactive, stream, prompt):
    """Chat with an LLM agent."""
    config = Config()
    ui_instance = UI()
    session_state = get_session_state()
    interactive_mode = not non_interactive

    if interactive_mode:
        # Interactive mode
        current_provider, current_model = setup_initial_provider_and_model(
            provider, model, config, session_state
        )
        current_stream = stream if stream else session_state.get("stream", False)

        # Validate model
        if not ModelFactory.validate_model(current_provider, current_model):
            ui_instance.print_warning(
                f"Model '{current_model}' not found in metadata for provider '{current_provider}'."
            )
            ui_instance.print_info("Proceeding anyway, but some features may not work optimally.")

        # Save initial state
        save_session_state(
            {
                "provider": current_provider,
                "model": current_model,
                "stream": current_stream,
            }
        )

        run_interactive_mode(
            current_provider,
            current_model,
            current_stream,
            config,
            ui_instance,
        )
    else:
        # Non-interactive mode
        if not provider or not model:
            ui_instance.print_error("--provider and --model are required in non-interactive mode.")
            if session_state:
                ui_instance.print_info(
                    f"Last session used: {session_state.get('provider')} / {session_state.get('model')}"
                )
                ui_instance.print_info(
                    "Run without --non-interactive to continue with last session, or specify --provider and --model."
                )
            sys.exit(1)

        run_non_interactive_mode(
            provider,
            model,
            prompt,
            stream,
            config,
            ui_instance,
        )


@cli.command()
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["ollama", "openai", "anthropic", "google"], case_sensitive=False),
    help="Filter by provider",
)
@click.option("--detailed", "-d", is_flag=True, help="Show detailed model information")
def list_models(provider, detailed):
    """List available models for each provider."""
    config = Config()
    ui_instance = UI()

    # Get models from ModelFactory
    all_models = ModelFactory.get_available_models(provider)

    if not all_models:
        ui_instance.print_info("No models found.")
        return

    for prov, models in sorted(all_models.items()):
        provider_display = prov.capitalize()

        if prov == "ollama":
            provider_display = "Ollama (Local)"
            try:
                agent = AgentFactory.create("ollama", DUMMY_MODEL_NAME, config)
                actual_models = agent.list_models()
                if actual_models:
                    rows = [[model, "Local", ""] for model in actual_models]
                    ui_instance.print_table(provider_display, ["Model", "Context", "Max Tokens"], rows)
                    continue
            except Exception:
                pass

        # Build rows for table
        table_rows = []
        for model_name in sorted(models.keys()):
            metadata = ModelFactory.get_model_metadata(prov, model_name)
            if detailed and metadata:
                table_rows.append(
                    [
                        model_name,
                        f"{metadata.context_length:,}" if metadata else "-",
                        f"{metadata.max_tokens:,}" if metadata else "-",
                    ]
                )
            else:
                table_rows.append([model_name, "-", "-"])

        ui_instance.print_table(provider_display, ["Model", "Context", "Max Tokens"], table_rows)


@cli.command()
def config():
    """Show current configuration."""
    config = Config()
    ui_instance = UI()
    rows = [
        ["Ollama URL", config.ollama_base_url],
        ["OpenAI API Key", "Set" if config.openai_api_key else "Not set"],
        ["Anthropic API Key", "Set" if config.anthropic_api_key else "Not set"],
        ["Google API Key", "Set" if config.google_api_key else "Not set"],
    ]
    ui_instance.print_table("Configuration", ["Setting", "Value"], rows)


@cli.group()
def mcp():
    """Manage MCP (Model Context Protocol) servers."""
    pass


@mcp.command("list")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed server information")
def mcp_list(detailed):
    """List configured MCP servers."""
    config = Config()
    ui_instance = UI()
    servers = config.get_mcp_servers()

    if not servers:
        ui_instance.print_info("No MCP servers configured.")
        ui_instance.print_info("To add a server, use: agent-cli mcp add <name> <command> [args...]")
        return

    rows = []
    for name, server_config in sorted(servers.items()):
        cmd = server_config.get("command", "N/A")
        args = " ".join(server_config.get("args", []))
        env_count = len(server_config.get("env", {}))
        rows.append([name, f"{cmd} {args}", str(env_count)])

    ui_instance.print_table("MCP Servers", ["Name", "Command", "Env Vars"], rows)


@mcp.command("add")
@click.argument("name")
@click.argument("command")
@click.argument("args", nargs=-1)
@click.option("--env", "-e", multiple=True, help="Environment variables in KEY=VALUE format")
@click.option("--validate", is_flag=True, help="Validate server configuration after adding")
def mcp_add(name, command, args, env, validate):
    """Add or update an MCP server configuration."""
    config = Config()
    ui_instance = UI()

    # Parse environment variables
    env_dict = {}
    for env_var in env:
        if "=" in env_var:
            key, value = env_var.split("=", 1)
            env_dict[key] = value
        else:
            ui_instance.print_warning(f"Invalid environment variable format '{env_var}'. Use KEY=VALUE")

    try:
        config.add_mcp_server(
            name, command, list(args) if args else None, env_dict if env_dict else None
        )
        ui_instance.print_success(f"MCP server '{name}' added successfully.")

        if validate:
            import shutil

            cmd_name = command.split()[0] if command else command
            if shutil.which(cmd_name):
                ui_instance.print_success(f"Command '{cmd_name}' found in PATH")
            else:
                ui_instance.print_warning(f"Command '{cmd_name}' not found in PATH")
                ui_instance.print_info("Make sure the command is available when the MCP server runs.")
    except Exception as e:
        ui_instance.print_error(f"Error adding MCP server: {e}")
        sys.exit(1)


@mcp.command("remove")
@click.argument("name")
@click.option("--force", "-f", is_flag=True, help="Don't prompt for confirmation")
def mcp_remove(name, force):
    """Remove an MCP server configuration."""
    config = Config()
    ui_instance = UI()
    servers = config.get_mcp_servers()

    if name not in servers:
        ui_instance.print_error(f"MCP server '{name}' not found.")
        sys.exit(1)

    if not force and not click.confirm(f"Remove MCP server '{name}'?"):
        ui_instance.print_info("Cancelled.")
        return

    if config.remove_mcp_server(name):
        ui_instance.print_success(f"MCP server '{name}' removed successfully.")
    else:
        ui_instance.print_error(f"Error removing MCP server '{name}'.")
        sys.exit(1)


@mcp.command("show")
@click.argument("name")
def mcp_show(name):
    """Show detailed information about an MCP server."""
    config = Config()
    ui_instance = UI()
    servers = config.get_mcp_servers()

    if name not in servers:
        ui_instance.print_error(f"MCP server '{name}' not found.")
        sys.exit(1)

    server_config = servers[name]
    ui_instance.print_info(f"MCP Server: {name}")

    content = f"**Command:** `{server_config.get('command', 'N/A')}`\n\n"
    if server_config.get("args"):
        content += f"**Arguments:** `{' '.join(server_config['args'])}`\n\n"

    if server_config.get("env"):
        content += "**Environment Variables:**\n"
        for key, value in server_config["env"].items():
            display_value = value if len(value) < 50 else value[:30] + "..." + value[-10:]
            content += f"- {key}={display_value}\n"

    ui_instance.print_markdown(content)


@cli.command()
@click.argument("provider", type=click.Choice(["openai", "anthropic", "google", "ollama"]))
def setup(provider: str):
    """Interactive setup for a provider - configure API keys and settings."""
    from rich.console import Console

    from agent_cli.onboarding import ProviderOnboarding

    console = Console()
    ProviderOnboarding.quick_setup(provider, console)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
