"""Main CLI entry point."""
import click
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from agent_cli.config import Config
from agent_cli.agents import AgentFactory
from agent_cli.model_factory import ModelFactory
from agent_cli.command_registry import handle_command, generate_help_text
from agent_cli.session_manager import (
    get_session_state,
    update_session_state,
    save_session_state,
)
from agent_cli.history_manager import (
    add_to_history,
    format_history_summary,
    should_compact_history,
    compact_history,
)
# Import interactive commands to register them
import agent_cli.interactive_commands  # noqa: F401
from agent_cli.interactive_commands import (
    CONTEXT_KEY_AGENT,
    CONTEXT_KEY_PROVIDER,
    CONTEXT_KEY_MODEL,
    CONTEXT_KEY_STREAM,
    CONTEXT_KEY_HISTORY,
    CONTEXT_KEY_CONFIG,
)


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
        return path.read_text(encoding='utf-8')
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
            click.echo(f"Warning: Could not read file '{filename}'", err=True)
    
    # Prepend file contents to the prompt
    if file_contents:
        enhanced_prompt = "\n\n".join(file_contents) + "\n\nUser request: " + processed_text
    else:
        enhanced_prompt = processed_text
    
    return enhanced_prompt, file_contents


def show_interactive_help():
    """Show help for interactive commands using the registry."""
    help_text = generate_help_text()
    click.echo(help_text)
    click.echo("File References:")
    click.echo("  Use @filename to include file contents in your prompt")
    click.echo("  Example: @config.py or @\"file with spaces.txt\"")
    click.echo()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Agent CLI - A custom LLM CLI with local and external agent support."""
    pass


@cli.command()
@click.option("--provider", "-p", required=False,
              type=click.Choice(["ollama", "openai", "anthropic", "google"], case_sensitive=False),
              help="Provider to use (ollama, openai, anthropic, google). If not specified, uses last session provider.")
@click.option("--model", "-m", required=False,
              help="Model name to use. If not specified, uses last session model.")
@click.option("--interactive", "-i", is_flag=True,
              help="Run in interactive mode")
@click.option("--stream", "-s", is_flag=True,
              help="Stream the response token by token")
@click.argument("prompt", required=False)
def chat(provider, model, interactive, stream, prompt):
    """Chat with an LLM agent."""
    config = Config()
    
    # Load session state
    session_state = get_session_state()
    
    # Use provided values, or fall back to session state (for interactive mode)
    if interactive:
        # In interactive mode, use session state if provider/model not specified
        current_provider = provider or session_state.get("provider") or "ollama"
        current_model = model or session_state.get("model") or config.default_ollama_model
        current_stream = stream if stream else session_state.get("stream", False)
    else:
        # In non-interactive mode, provider and model are required
        if not provider or not model:
            click.echo("Error: --provider and --model are required in non-interactive mode.", err=True)
            if session_state:
                click.echo(f"\nLast session used: {session_state.get('provider')} / {session_state.get('model')}", err=True)
                click.echo("Use --interactive to continue with last session, or specify --provider and --model.", err=True)
            sys.exit(1)
        current_provider = provider
        current_model = model
        current_stream = stream
    
    # Validate model (warn if not in metadata, but don't fail)
    if not ModelFactory.validate_model(current_provider, current_model):
        click.echo(f"Warning: Model '{current_model}' not found in metadata for provider '{current_provider}'.", err=True)
        click.echo("Proceeding anyway, but some features may not work optimally.", err=True)
        click.echo("Use 'agent-cli list-models' to see available models.\n", err=True)
    
    # Save initial state to session
    if interactive:
        save_session_state({
            "provider": current_provider,
            "model": current_model,
            "stream": current_stream,
        })
    
    # Conversation history for context
    history: List[Dict[str, str]] = []
    
    def create_agent():
        """Create agent with current provider and model."""
        return AgentFactory.create(current_provider, current_model, config)
    
    if interactive:
        click.echo("Entering interactive mode. Type '/help' for commands, 'exit' or 'quit' to end.")
        click.echo(f"Using {current_provider} with model {current_model}")
        if current_stream:
            click.echo("Streaming mode enabled.\n")
        else:
            click.echo()
        
        agent = create_agent()
        
        while True:
            try:
                user_input = click.prompt("You", default="", show_default=False)
                
                # Handle exit
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                # Handle empty input
                if not user_input.strip():
                    continue
                
                # Handle commands starting with / using the registry
                if user_input.startswith("/"):
                    # Build context for command handlers
                    command_context = {
                        CONTEXT_KEY_AGENT: agent,
                        CONTEXT_KEY_PROVIDER: current_provider,
                        CONTEXT_KEY_MODEL: current_model,
                        CONTEXT_KEY_STREAM: current_stream,
                        CONTEXT_KEY_HISTORY: history,
                        CONTEXT_KEY_CONFIG: config,
                    }
                    
                    # Handle command via registry
                    handled = handle_command(user_input, command_context)
                    
                    if handled:
                        # Update local variables from context (in case command changed them)
                        new_provider = command_context.get(CONTEXT_KEY_PROVIDER, current_provider)
                        new_model = command_context.get(CONTEXT_KEY_MODEL, current_model)
                        new_stream = command_context.get(CONTEXT_KEY_STREAM, current_stream)
                        
                        # Save to session if changed
                        if (new_provider != current_provider or 
                            new_model != current_model or 
                            new_stream != current_stream):
                            update_session_state(
                                provider=new_provider,
                                model=new_model,
                                stream=new_stream,
                            )
                        
                        current_provider = new_provider
                        current_model = new_model
                        current_stream = new_stream
                        agent = command_context.get(CONTEXT_KEY_AGENT, agent)
                    else:
                        click.echo(f"Unknown command: {user_input}. Type /help for available commands.\n", err=True)
                    continue
                
                # Process file references (@filename)
                processed_prompt, file_refs = process_file_references(user_input)
                
                if current_stream:
                    click.echo(f"\n{current_model}: ", nl=False)
                    response_parts = []
                    for token in agent.stream(processed_prompt, history):
                        click.echo(token, nl=False)
                        sys.stdout.flush()
                        response_parts.append(token)
                    click.echo("\n")
                    response = "".join(response_parts)
                else:
                    response = agent.chat(processed_prompt, history)
                    click.echo(f"\n{current_model}: {response}\n")
                
                # Update conversation history with automatic compaction
                history = add_to_history(history, "user", user_input)
                history = add_to_history(history, "assistant", response)
                
            except KeyboardInterrupt:
                click.echo("\nExiting...")
                break
            except Exception as e:
                click.echo(f"\nError: {e}\n", err=True)
    else:
        if not prompt:
            click.echo("Error: Prompt is required in non-interactive mode.")
            click.echo("Use --interactive for interactive mode or provide a prompt.")
            return
        
        # Process file references (@filename)
        processed_prompt, file_refs = process_file_references(prompt)
        if file_refs:
            click.echo(f"Including {len(file_refs)} file(s) in prompt...\n", err=True)
        
        try:
            if stream:
                for token in agent.stream(processed_prompt, history):
                    click.echo(token, nl=False)
                    sys.stdout.flush()
                click.echo()  # New line after streaming
            else:
                response = agent.chat(processed_prompt, history)
                click.echo(response)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@cli.command()
@click.option("--provider", "-p", 
              type=click.Choice(["ollama", "openai", "anthropic", "google"], case_sensitive=False),
              help="Filter by provider")
@click.option("--detailed", "-d", is_flag=True,
              help="Show detailed model information")
def list_models(provider, detailed):
    """List available models for each provider."""
    config = Config()
    
    # Get models from ModelFactory
    all_models = ModelFactory.get_available_models(provider)
    
    if not all_models:
        click.echo("No models found.")
        return
    
    click.echo("Available Providers and Models:\n")
    
    for prov, models in sorted(all_models.items()):
        provider_display = prov.capitalize()
        if prov == "ollama":
            provider_display = "Ollama (Local)"
            # Try to get actual Ollama models
            try:
                agent = AgentFactory.create("ollama", "dummy", config)
                actual_models = agent.list_models()
                if actual_models:
                    click.echo(f"{provider_display}:")
                    for model in actual_models:
                        metadata = ModelFactory.get_model_metadata(prov, model)
                        if detailed and metadata:
                            click.echo(f"  - {model} (context: {metadata.context_length}, max: {metadata.max_tokens})")
                        else:
                            click.echo(f"  - {model}")
                    click.echo()
                    continue
            except Exception:
                pass  # Fall through to metadata models
        
        click.echo(f"{provider_display}:")
        for model_name in sorted(models.keys()):
            metadata = ModelFactory.get_model_metadata(prov, model_name)
            if detailed and metadata:
                click.echo(f"  - {model_name}")
                click.echo(f"    Context: {metadata.context_length:,} tokens")
                click.echo(f"    Max tokens: {metadata.max_tokens:,}")
                click.echo(f"    Streaming: {'Yes' if metadata.supports_streaming else 'No'}")
                if metadata.default_temperature:
                    click.echo(f"    Default temperature: {metadata.default_temperature}")
            else:
                click.echo(f"  - {model_name}")
        click.echo()


@cli.command()
def config():
    """Show current configuration."""
    config = Config()
    click.echo("Current Configuration:")
    click.echo(f"  Ollama URL: {config.ollama_base_url}")
    click.echo(f"  OpenAI API Key: {'Set' if config.openai_api_key else 'Not set'}")
    click.echo(f"  Anthropic API Key: {'Set' if config.anthropic_api_key else 'Not set'}")
    click.echo(f"  Google API Key: {'Set' if config.google_api_key else 'Not set'}")


@cli.group()
def mcp():
    """Manage MCP (Model Context Protocol) servers."""
    pass


@mcp.command("list")
@click.option("--detailed", "-d", is_flag=True,
              help="Show detailed server information")
def mcp_list(detailed):
    """List configured MCP servers."""
    config = Config()
    servers = config.get_mcp_servers()
    
    if not servers:
        click.echo("No MCP servers configured.")
        click.echo("\nTo add a server, use: agent-cli mcp add <name> <command> [args...]")
        click.echo("Example: agent-cli mcp add filesystem npx -y @modelcontextprotocol/server-filesystem /path/to/dir")
        return
    
    click.echo(f"Configured MCP Servers ({len(servers)}):\n")
    for name, server_config in sorted(servers.items()):
        click.echo(f"  {name}:")
        click.echo(f"    Command: {server_config.get('command', 'N/A')}")
        if server_config.get('args'):
            click.echo(f"    Args: {' '.join(server_config['args'])}")
        if server_config.get('env'):
            if detailed:
                click.echo(f"    Environment variables:")
                for key, value in server_config['env'].items():
                    # Mask sensitive values
                    display_value = value if len(value) < 20 else value[:10] + "..."
                    click.echo(f"      {key}={display_value}")
            else:
                env_count = len(server_config['env'])
                click.echo(f"    Environment: {env_count} variable(s) set")
        click.echo()


@mcp.command("add")
@click.argument("name")
@click.argument("command")
@click.argument("args", nargs=-1)
@click.option("--env", "-e", multiple=True, help="Environment variables in KEY=VALUE format")
@click.option("--validate", is_flag=True, help="Validate server configuration after adding")
def mcp_add(name, command, args, env, validate):
    """Add or update an MCP server configuration.
    
    Examples:
        agent-cli mcp add filesystem npx -y @modelcontextprotocol/server-filesystem /path/to/dir
        agent-cli mcp add github npx -y @modelcontextprotocol/server-github -e GITHUB_TOKEN=xxx
    """
    config = Config()
    
    # Parse environment variables
    env_dict = {}
    for env_var in env:
        if "=" in env_var:
            key, value = env_var.split("=", 1)
            env_dict[key] = value
        else:
            click.echo(f"Warning: Invalid environment variable format '{env_var}'. Use KEY=VALUE", err=True)
    
    try:
        config.add_mcp_server(name, command, list(args) if args else None, env_dict if env_dict else None)
        click.echo(f"MCP server '{name}' added successfully.")
        
        if validate:
            # Basic validation - check if command exists
            import shutil
            cmd_name = command.split()[0] if command else command
            if shutil.which(cmd_name):
                click.echo(f"✓ Command '{cmd_name}' found in PATH")
            else:
                click.echo(f"⚠ Warning: Command '{cmd_name}' not found in PATH", err=True)
                click.echo("  Make sure the command is available when the MCP server runs.", err=True)
    except Exception as e:
        click.echo(f"Error adding MCP server: {e}", err=True)
        sys.exit(1)


@mcp.command("remove")
@click.argument("name")
@click.option("--force", "-f", is_flag=True, help="Don't prompt for confirmation")
def mcp_remove(name, force):
    """Remove an MCP server configuration."""
    config = Config()
    servers = config.get_mcp_servers()
    
    if name not in servers:
        click.echo(f"MCP server '{name}' not found.", err=True)
        sys.exit(1)
    
    if not force:
        if not click.confirm(f"Remove MCP server '{name}'?"):
            click.echo("Cancelled.")
            return
    
    if config.remove_mcp_server(name):
        click.echo(f"MCP server '{name}' removed successfully.")
    else:
        click.echo(f"Error removing MCP server '{name}'.", err=True)
        sys.exit(1)


@mcp.command("show")
@click.argument("name")
def mcp_show(name):
    """Show detailed information about an MCP server."""
    config = Config()
    servers = config.get_mcp_servers()
    
    if name not in servers:
        click.echo(f"MCP server '{name}' not found.", err=True)
        sys.exit(1)
    
    server_config = servers[name]
    click.echo(f"MCP Server: {name}\n")
    click.echo(f"Command: {server_config.get('command', 'N/A')}")
    
    if server_config.get('args'):
        click.echo(f"Arguments: {' '.join(server_config['args'])}")
    
    if server_config.get('env'):
        click.echo("\nEnvironment Variables:")
        for key, value in server_config['env'].items():
            # Mask long values
            display_value = value if len(value) < 50 else value[:30] + "..." + value[-10:]
            click.echo(f"  {key}={display_value}")
    else:
        click.echo("\nEnvironment Variables: None")
    
    click.echo()


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
