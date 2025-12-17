"""Main CLI entry point."""

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

# Import interactive commands to register them
import agent_cli.interactive_commands  # noqa: F401
from agent_cli.agents import AgentFactory
from agent_cli.command_registry import handle_command
from agent_cli.config import Config
from agent_cli.history_manager import (
    add_to_history,
)
from agent_cli.interactive_commands import (
    CONTEXT_KEY_AGENT,
    CONTEXT_KEY_CONFIG,
    CONTEXT_KEY_HISTORY,
    CONTEXT_KEY_MODEL,
    CONTEXT_KEY_PROVIDER,
    CONTEXT_KEY_STREAM,
    CONTEXT_KEY_SYSTEM_PROMPT,
)
from agent_cli.model_factory import ModelFactory
from agent_cli.session_manager import (
    get_session_state,
    save_session_state,
    update_session_state,
)
from agent_cli.ui import ui


def read_file_content(filepath: str) -> Optional[str]:
    """Read file content, handling both absolute and relative paths."""
    try:
        path = Path(filepath)
        if not path.is_absolute():
            # Try relative to current directory
            path = Path.cwd() / path
        if not path.exists():
            return None
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def process_file_references(text: str) -> Tuple[str, List[str]]:
    """Process @filename references in text and return enhanced prompt with file contents."""
    # Pattern to match @filename or @"filename with spaces"
    pattern = r'@("([^"]+)"|(\S+))'
    file_contents = []
    processed_text = text

    for match in re.finditer(pattern, text):
        filename = match.group(2) or match.group(3)
        content = read_file_content(filename)
        if content:
            file_contents.append(f"File: {filename}\n{content}")
            # Replace @filename with a reference
            processed_text = processed_text.replace(match.group(0), f"[File: {filename}]")
        else:
            ui.print_warning(f"Could not read file '{filename}'")

    # Prepend file contents to the prompt
    if file_contents:
        enhanced_prompt = "\n\n".join(file_contents) + "\n\nUser request: " + processed_text
    else:
        enhanced_prompt = processed_text

    return enhanced_prompt, file_contents


def show_interactive_help():
    """Show help for interactive commands using the registry."""
    # This is handled by the /help command now, effectively
    pass


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Agent CLI - A custom LLM CLI with local and external agent support."""
    pass


@cli.command()
@click.option(
    "--provider",
    "-p",
    required=False,
    type=click.Choice(["ollama", "openai", "anthropic", "google"], case_sensitive=False),
    help="Provider to use (ollama, openai, anthropic, google). If not specified, uses last session provider.",
)
@click.option(
    "--model",
    "-m",
    required=False,
    help="Model name to use. If not specified, uses last session model.",
)
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
@click.option("--stream", "-s", is_flag=True, help="Stream the response token by token")
@click.argument("prompt", required=False)
def chat(provider, model, interactive, stream, prompt):
    """Chat with an LLM agent."""
    config = Config()

    # Load session state
    session_state = get_session_state()

    # Use provided values, or fall back to session state (for interactive mode)
    if interactive:
        # Check if first-run onboarding is needed
        from agent_cli.interactive_onboarding import maybe_run_onboarding
        from rich.console import Console
        onboarding_provider = maybe_run_onboarding(Console())
        if onboarding_provider:
            # Use the provider from onboarding
            current_provider = onboarding_provider
            config = Config()  # Reload config to pick up new env vars
            if onboarding_provider == "ollama":
                current_model = config.default_ollama_model
            elif onboarding_provider == "openai":
                current_model = config.default_openai_model
            elif onboarding_provider == "anthropic":
                current_model = config.default_anthropic_model
            elif onboarding_provider == "google":
                current_model = config.default_google_model
        
        # In interactive mode, use session state if provider/model not specified
        current_provider = provider or session_state.get("provider") or "ollama"
        current_model = model or session_state.get("model") or config.default_ollama_model
        current_stream = stream if stream else session_state.get("stream", False)
        current_system_prompt = None  # Start with no system prompt
    else:
        # In non-interactive mode, provider and model are required
        if not provider or not model:
            ui.print_error("--provider and --model are required in non-interactive mode.")
            if session_state:
                ui.print_info(
                    f"Last session used: {session_state.get('provider')} / {session_state.get('model')}"
                )
                ui.print_info(
                    "Use --interactive to continue with last session, or specify --provider and --model."
                )
            sys.exit(1)
        current_provider = provider
        current_model = model
        current_stream = stream
        current_system_prompt = None

    # Validate model (warn if not in metadata, but don't fail)
    if not ModelFactory.validate_model(current_provider, current_model):
        ui.print_warning(
            f"Model '{current_model}' not found in metadata for provider '{current_provider}'."
        )
        ui.print_info("Proceeding anyway, but some features may not work optimally.")
        ui.print_info("Use 'agent-cli list-models' to see available models.")

    # Save initial state to session
    if interactive:
        save_session_state(
            {
                "provider": current_provider,
                "model": current_model,
                "stream": current_stream,
            }
        )

    # Conversation history for context
    history: List[Dict[str, str]] = []

    def create_agent():
        """Create agent with current provider and model."""
        return AgentFactory.create(
            current_provider, current_model, config, system_prompt=current_system_prompt
        )

    if interactive:
        ui.print_welcome()
        ui.print_info(
            f"Using [bold]{current_provider}[/bold] with model [bold]{current_model}[/bold]"
        )
        if current_stream:
            ui.print_info("Streaming mode enabled.")

        agent = create_agent()

        # Load Ollama model if using ollama provider
        if current_provider == "ollama":
            from agent_cli.ollama_manager import get_ollama_manager
            ollama_mgr = get_ollama_manager()
            ollama_mgr.load_model(current_model)

        # Initialize interactive session status
        ui.interactive_session.update_status(current_provider, current_model)

        # Load theme from config if set
        saved_theme = config.get_value("THEME")
        if saved_theme and saved_theme in ui.theme_manager.get_available_themes():
            ui.theme_manager.set_theme(saved_theme)

        # Attempt to populate model list for autocomplete
        try:
            models = agent.list_models()
            if models:
                ui.interactive_session.update_completion_models(models)
                # ui.print_info(f"Loaded {len(models)} models for autocomplete.")
        except Exception:
            pass  # Fail silently for autocomplete loading

        while True:
            try:
                # Initialize variables that might be used in exception handling or cleanup
                response_parts = []

                # Use InteractiveSession for prompt input
                user_input = ui.interactive_session.prompt()

                # Handle exit
                if user_input.lower() in ["exit", "quit"]:
                    break

                # Handle empty input
                if not user_input.strip():
                    continue

                # Handle commands starting with / using the registry
                if user_input.startswith("/"):
                    parts = user_input.split()
                    cmd = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []

                    if cmd == "/compress":
                        if not history:
                            ui.print_warning("No history to compress.")
                            continue

                        ui.print_info("Compressing conversation history...")
                        with ui.create_spinner("Summarizing context..."):
                            summary_prompt = "Summarize our conversation so far into a concise context string that captures all key information, decisions, and current state. Do not lose important details."
                            summary = agent.chat(summary_prompt, history=history)

                        # Replace history with summary
                        history = [
                            {"role": "user", "content": "Previous Context Summary: " + summary},
                            {"role": "assistant", "content": "Understood. I have the context."},
                        ]
                        ui.print_success("Context compressed!")
                        continue

                    elif cmd == "/beads":
                        bd_path = shutil.which("bd")

                        # Handle installation if missing
                        if not bd_path:
                            ui.print_warning("Beads CLI ('bd') not found.")

                            # Check for Homebrew
                            brew_path = shutil.which("brew")
                            if brew_path:
                                try:
                                    response = ui.interactive_session.session.prompt(
                                        "Install 'bd' via Homebrew? (y/n) > "
                                    )
                                    if response.lower().startswith("y"):
                                        ui.print_info("Running: brew tap steveyegge/beads")
                                        subprocess.run(
                                            [brew_path, "tap", "steveyegge/beads"], check=True
                                        )

                                        ui.print_info("Running: brew install bd")
                                        subprocess.run([brew_path, "install", "bd"], check=True)

                                        bd_path = shutil.which("bd")
                                        if bd_path:
                                            ui.print_success(
                                                f"Beads installed successfully at {bd_path}!"
                                            )
                                        else:
                                            ui.print_error(
                                                "Installation appeared to succeed but 'bd' is still not found."
                                            )
                                except subprocess.CalledProcessError as e:
                                    ui.print_error(f"Installation failed: {e}")
                                except Exception as e:
                                    ui.print_error(f"Error during installation: {e}")

                            if not bd_path:
                                ui.print_info("Please install manually:")
                                ui.print_info("  brew tap steveyegge/beads && brew install bd")
                                ui.print_info("  -or-")
                                ui.print_info(
                                    "  curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash"
                                )
                                continue

                        subcmd = args[0] if args else "status"

                        try:
                            if subcmd == "context":
                                # For now, status serves as context check
                                result = subprocess.run(
                                    [bd_path, "status"], capture_output=True, text=True, check=True
                                )
                                ui.print_panel(result.stdout, title="Beads Context", style="blue")
                            else:  # Default to status
                                result = subprocess.run(
                                    [bd_path, "status"], capture_output=True, text=True, check=True
                                )
                                ui.print_panel(result.stdout, title="Beads Status", style="blue")
                        except subprocess.CalledProcessError as e:
                            # 'bd' might return non-zero if not initialized
                            ui.print_warning(
                                f"Beads returned error (is it initialized?): {e.stderr.strip() if e.stderr else e.stdout.strip()}"
                            )
                            ui.print_info(
                                "Try running 'bd init' in the project folder matching this session."
                            )
                        except FileNotFoundError:
                            # Should not happen given check above, but safe to keep
                            ui.print_error(f"Beads CLI ('bd') not found at '{bd_path}'.")
                        except Exception as e:
                            ui.print_error(f"An unexpected error occurred while running beads: {e}")
                        continue

                    elif cmd == "/keepalive":
                        if args:
                            if hasattr(agent, "set_keep_alive"):
                                agent.set_keep_alive(args[0])
                                ui.print_success(f"Keep-alive set to {args[0]}")
                            else:
                                ui.print_warning("Keep-alive is only supported for Ollama agents.")
                        else:
                            ui.print_info(
                                f"Current keep-alive: {getattr(agent, 'keep_alive', 'N/A')}"
                            )
                            ui.print_info("Usage: /keepalive 10m (only for Ollama)")
                        continue

                    elif cmd == "/reasoning":
                        # Toggle reasoning logic (if any)
                        # For now just a placeholder toggle or info
                        ui.print_info(
                            "Reasoning display toggle: currently always enabled for raw stream."
                        )
                        continue

                    # Build context for command handlers
                    command_context = {
                        CONTEXT_KEY_AGENT: agent,
                        CONTEXT_KEY_PROVIDER: current_provider,
                        CONTEXT_KEY_MODEL: current_model,
                        CONTEXT_KEY_STREAM: current_stream,
                        CONTEXT_KEY_HISTORY: history,
                        CONTEXT_KEY_CONFIG: config,
                        CONTEXT_KEY_SYSTEM_PROMPT: current_system_prompt,
                    }

                    # Handle command via registry
                    handled = handle_command(user_input, command_context)

                    if handled:
                        # Update local variables from context (in case command changed them)
                        new_provider = command_context.get(CONTEXT_KEY_PROVIDER, current_provider)
                        new_model = command_context.get(CONTEXT_KEY_MODEL, current_model)
                        new_stream = command_context.get(CONTEXT_KEY_STREAM, current_stream)
                        new_system_prompt = command_context.get(
                            CONTEXT_KEY_SYSTEM_PROMPT, current_system_prompt
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

                        current_provider = new_provider
                        current_model = new_model
                        current_stream = new_stream
                        current_system_prompt = new_system_prompt

                        # Update agent if provider/model/system_prompt changed
                        needs_refresh = False
                        if agent != command_context.get(CONTEXT_KEY_AGENT, agent):
                            agent = command_context.get(CONTEXT_KEY_AGENT, agent)
                        elif (
                            new_model != command_context.get(CONTEXT_KEY_MODEL, current_model)
                            or new_provider
                            != command_context.get(CONTEXT_KEY_PROVIDER, current_provider)
                            or new_system_prompt
                            != command_context.get(CONTEXT_KEY_SYSTEM_PROMPT, current_system_prompt)
                        ):  # Check if these differ from what they were BEFORE command
                            # Actually check against current_ vars is redundant if we just updated them.
                            # We need to detect if command changed them.
                            # Easier: just always recreate if agent wasn't explicitly replaced but params are different from what agent has
                            # But agent doesn't expose system_prompt easily unless we modify base again.
                            # Simpler: just set needs_refresh = True if they changed in context
                            needs_refresh = True

                        if needs_refresh:
                            agent = create_agent()
                            # Re-apply properties if needed (like keep_alive)
                            # Note: new agent will have default keep_alive. Ideally we preserve it.
                            # But for now user has to re-set it if they switch models.

                        # Update status bar
                        ui.interactive_session.update_status(current_provider, current_model)
                    else:
                        ui.print_error(
                            f"Unknown command: {user_input}. Type /help for available commands."
                        )
                    continue

                # Process file references (@filename)
                processed_prompt, file_refs = process_file_references(user_input)

                # Check connection before chatting (optional optimization)
                ui.interactive_session.update_status(
                    current_provider, current_model, connected=True
                )  # Assume connected until error

                if current_stream:
                    # Using a simple header for stream start
                    ui.console.print(f"\n[bold green]{current_model}[/bold green]:", end=" ")

                    response_parts = []

                    # Create a spinner while waiting for the first token
                    with ui.create_spinner(f"Activating {current_model}..."):
                        # Get the generator
                        stream_gen = agent.stream(processed_prompt, history)
                        # Fetch first token to "break" the spinner lock
                        try:
                            first_token = next(stream_gen)
                        except StopIteration:
                            first_token = None

                    # Start printing
                    if first_token:
                        ui.print_stream_chunk(first_token)
                        response_parts.append(first_token)

                    for token in stream_gen:
                        ui.print_stream_chunk(token)
                        response_parts.append(token)
                    ui.console.print("\n")
                    response = "".join(response_parts)
                else:
                    with ui.create_spinner("Thinking..."):
                        response = agent.chat(processed_prompt, history)
                    ui.print_agent_response(response, current_model)

                # Update conversation history with automatic compaction
                history = add_to_history(history, "user", user_input)
                history = add_to_history(history, "assistant", response)

            except KeyboardInterrupt:
                # Cleanup Ollama if used
                if current_provider == "ollama":
                    from agent_cli.ollama_manager import get_ollama_manager
                    get_ollama_manager().cleanup()
                ui.print_info("\nExiting...")
                break
            except Exception as e:
                ui.interactive_session.update_status(
                    current_provider, current_model, connected=False
                )
                ui.print_error(f"{e}")
    else:
        if not prompt:
            ui.print_error("Prompt is required in non-interactive mode.")
            ui.print_info("Use --interactive for interactive mode or provide a prompt.")
            return

        # Process file references (@filename)
        processed_prompt, file_refs = process_file_references(prompt)
        if file_refs:
            ui.print_info(f"Including {len(file_refs)} file(s) in prompt...")

        try:
            agent = create_agent()
            if stream:
                for token in agent.stream(processed_prompt, history):
                    print(
                        token, end="", flush=True
                    )  # Keep raw print for pipe-ability in non-interactive? Or use ui?
                    # If non-interactive is used for scripting, raw strings are better.
                    # But the user asked for UI update. Assuming interactive usage is primary target.
                    # Let's use standard print for non-interactive to be safe for pipes,
                    # OR use ui.console.print with markup=False if we want raw.
                    # actually the 'stream' flag in CLI usually implies human consumption.
                    # If piping, usually no stream.
                    pass
                # Implementation for non-interactive stream:
                for token in agent.stream(processed_prompt, history):
                    sys.stdout.write(token)
                    sys.stdout.flush()
                sys.stdout.write("\n")
            else:
                response = agent.chat(processed_prompt, history)
                # For non-interactive, just print the response content?
                # Or styled? Let's keep it simple for pipes:
                print(response)
        except Exception as e:
            ui.print_error(f"{e}")
            sys.exit(1)


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

    # Get models from ModelFactory
    all_models = ModelFactory.get_available_models(provider)

    if not all_models:
        ui.print_info("No models found.")
        return

    for prov, models in sorted(all_models.items()):
        provider_display = prov.capitalize()

        rows = []

        if prov == "ollama":
            provider_display = "Ollama (Local)"
            try:
                agent = AgentFactory.create("ollama", "dummy", config)
                actual_models = agent.list_models()
                if actual_models:
                    for model in actual_models:
                        rows.append([model, "Local", ""])
                    ui.print_table(provider_display, ["Model", "Context", "Max Tokens"], rows)
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

        ui.print_table(provider_display, ["Model", "Context", "Max Tokens"], table_rows)


@cli.command()
def config():
    """Show current configuration."""
    config = Config()
    rows = [
        ["Ollama URL", config.ollama_base_url],
        ["OpenAI API Key", "Set" if config.openai_api_key else "Not set"],
        ["Anthropic API Key", "Set" if config.anthropic_api_key else "Not set"],
        ["Google API Key", "Set" if config.google_api_key else "Not set"],
    ]
    ui.print_table("Configuration", ["Setting", "Value"], rows)


@cli.group()
def mcp():
    """Manage MCP (Model Context Protocol) servers."""
    pass


@mcp.command("list")
@click.option("--detailed", "-d", is_flag=True, help="Show detailed server information")
def mcp_list(detailed):
    """List configured MCP servers."""
    config = Config()
    servers = config.get_mcp_servers()

    if not servers:
        ui.print_info("No MCP servers configured.")
        ui.print_info("To add a server, use: agent-cli mcp add <name> <command> [args...]")
        return

    rows = []
    for name, server_config in sorted(servers.items()):
        cmd = server_config.get("command", "N/A")
        args = " ".join(server_config.get("args", []))
        env_count = len(server_config.get("env", {}))
        rows.append([name, f"{cmd} {args}", str(env_count)])

    ui.print_table("MCP Servers", ["Name", "Command", "Env Vars"], rows)


@mcp.command("add")
@click.argument("name")
@click.argument("command")
@click.argument("args", nargs=-1)
@click.option("--env", "-e", multiple=True, help="Environment variables in KEY=VALUE format")
@click.option("--validate", is_flag=True, help="Validate server configuration after adding")
def mcp_add(name, command, args, env, validate):
    """Add or update an MCP server configuration."""
    config = Config()

    # Parse environment variables
    env_dict = {}
    for env_var in env:
        if "=" in env_var:
            key, value = env_var.split("=", 1)
            env_dict[key] = value
        else:
            ui.print_warning(f"Invalid environment variable format '{env_var}'. Use KEY=VALUE")

    try:
        config.add_mcp_server(
            name, command, list(args) if args else None, env_dict if env_dict else None
        )
        ui.print_success(f"MCP server '{name}' added successfully.")

        if validate:
            import shutil

            cmd_name = command.split()[0] if command else command
            if shutil.which(cmd_name):
                ui.print_success(f"Command '{cmd_name}' found in PATH")
            else:
                ui.print_warning(f"Command '{cmd_name}' not found in PATH")
                ui.print_info("Make sure the command is available when the MCP server runs.")
    except Exception as e:
        ui.print_error(f"Error adding MCP server: {e}")
        sys.exit(1)


@mcp.command("remove")
@click.argument("name")
@click.option("--force", "-f", is_flag=True, help="Don't prompt for confirmation")
def mcp_remove(name, force):
    """Remove an MCP server configuration."""
    config = Config()
    servers = config.get_mcp_servers()

    if name not in servers:
        ui.print_error(f"MCP server '{name}' not found.")
        sys.exit(1)

    if not force:
        # We can implement a ui.confirm if needed, or use click.confirm
        if not click.confirm(f"Remove MCP server '{name}'?"):
            ui.print_info("Cancelled.")
            return

    if config.remove_mcp_server(name):
        ui.print_success(f"MCP server '{name}' removed successfully.")
    else:
        ui.print_error(f"Error removing MCP server '{name}'.")
        sys.exit(1)


@mcp.command("show")
@click.argument("name")
def mcp_show(name):
    """Show detailed information about an MCP server."""
    config = Config()
    servers = config.get_mcp_servers()

    if name not in servers:
        ui.print_error(f"MCP server '{name}' not found.")
        sys.exit(1)

    server_config = servers[name]
    ui.print_info(f"MCP Server: {name}")  # Could use panel

    content = f"**Command:** `{server_config.get('command', 'N/A')}`\n\n"
    if server_config.get("args"):
        content += f"**Arguments:** `{' '.join(server_config['args'])}`\n\n"

    if server_config.get("env"):
        content += "**Environment Variables:**\n"
        for key, value in server_config["env"].items():
            display_value = value if len(value) < 50 else value[:30] + "..." + value[-10:]
            content += f"- {key}={display_value}\n"

    ui.print_markdown(content)


@cli.command()
@click.argument("provider", type=click.Choice(["openai", "anthropic", "google", "ollama"]))
def setup(provider: str):
    """Interactive setup for a provider - configure API keys and settings."""
    from agent_cli.onboarding import ProviderOnboarding
    from rich.console import Console
    
    console = Console()
    ProviderOnboarding.quick_setup(provider, console)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
