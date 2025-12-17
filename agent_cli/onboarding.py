"""Interactive provider onboarding flow."""
from typing import Optional, Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.table import Table
import os
from pathlib import Path
import requests


class ProviderOnboarding:
    """Interactive onboarding for provider setup."""

    PROVIDER_INFO = {
        "openai": {
            "name": "OpenAI",
            "icon": "🤖",
            "color": "bright_green",
            "models": ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini"],
            "api_key_name": "OPENAI_API_KEY",
            "api_key_prefix": "sk-",
            "signup_url": "https://platform.openai.com/api-keys",
            "description": "Access GPT-4, GPT-4o, and o1 reasoning models",
        },
        "anthropic": {
            "name": "Anthropic",
            "icon": "🧠",
            "color": "bright_magenta",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "api_key_name": "ANTHROPIC_API_KEY",
            "api_key_prefix": "sk-ant-",
            "signup_url": "https://console.anthropic.com/settings/keys",
            "description": "Access Claude 3.5 Sonnet and Haiku models",
        },
        "google": {
            "name": "Google",
            "icon": "✨",
            "color": "bright_blue",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
            "api_key_name": "GOOGLE_API_KEY",
            "api_key_prefix": "",
            "signup_url": "https://makersuite.google.com/app/apikey",
            "description": "Access Gemini 1.5 Pro and Flash models",
        },
        "ollama": {
            "name": "Ollama",
            "icon": "🦙",
            "color": "bright_yellow",
            "models": ["llama3.3", "llama3.2", "qwen2.5", "deepseek-coder-v2"],
            "api_key_name": None,
            "signup_url": "https://ollama.ai",
            "description": "Run local open-source models (no API key needed)",
        },
    }

    def __init__(self, console: Console):
        self.console = console

    def run_onboarding(self, provider: str) -> Optional[Dict[str, str]]:
        """Run interactive onboarding for a provider.

        Returns dict with config if successful, None if cancelled
        """
        if provider not in self.PROVIDER_INFO:
            self.console.print(f"[red]Unknown provider: {provider}[/red]")
            return None

        info = self.PROVIDER_INFO[provider]
        
        # Welcome panel
        self._show_welcome(provider, info)

        # Ollama is special - no API key needed
        if provider == "ollama":
            return self._onboard_ollama(info)
        
        # Other providers need API keys
        return self._onboard_api_provider(provider, info)

    def _show_welcome(self, provider: str, info: Dict):
        """Show themed welcome panel."""
        color = info["color"]
        icon = info["icon"]
        name = info["name"]
        
        welcome_text = f"""
# {icon} Welcome to {name} Setup!

{info['description']}

**Available Models:**
{chr(10).join(f'- {m}' for m in info['models'])}

Let's get you set up in just a few steps!
"""
        
        panel = Panel(
            Markdown(welcome_text),
            title=f"[{color}]{icon} {name} Setup[/{color}]",
            border_style=color,
            padding=(1, 2),
        )
        self.console.print()
        self.console.print(panel)
        self.console.print()

    def _test_ollama_connection(self, base_url: str) -> bool:
        """Test connection to Ollama server."""
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _get_ollama_models(self, base_url: str) -> List[str]:
        """Fetch available models from Ollama server."""
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        return []

    def _onboard_ollama(self, info: Dict) -> Optional[Dict[str, str]]:
        """Onboard Ollama (local, no API key)."""
        color = info["color"]
        self.console.print(f"[{color}]Ollama runs locally - no API key needed! {info['icon']}[/{color}]\n")
        
        # Ask for IP/hostname
        self.console.print("[dim]Enter the Ollama server address (hostname or IP)[/dim]")
        hostname = Prompt.ask(
            "Hostname/IP",
            default="localhost",
            console=self.console
        )
        
        port = Prompt.ask(
            "Port",
            default="11434",
            console=self.console
        )
        
        base_url = f"http://{hostname}:{port}"
        
        # Test connection
        self.console.print(f"\n[{color}]Testing connection to {base_url}...[/{color}]")
        
        if not self._test_ollama_connection(base_url):
            self.console.print(f"[red]✗[/red] Could not connect to Ollama at {base_url}")
            self.console.print("[yellow]Make sure Ollama is running and accessible[/yellow]")
            if not Confirm.ask("\nContinue anyway?", default=False, console=self.console):
                return None
            models = []
        else:
            self.console.print(f"[green]✓[/green] Connected successfully!\n")
            
            # Fetch available models
            self.console.print(f"[{color}]Fetching available models...[/{color}]")
            models = self._get_ollama_models(base_url)
        
        # Model selection
        default_model = None
        if models:
            # Display models in a table
            table = Table(title="Available Models", show_header=True, header_style="bold")
            table.add_column("#", style="dim", width=4)
            table.add_column("Model Name", style=color)
            
            for idx, model in enumerate(models, 1):
                table.add_row(str(idx), model)
            
            self.console.print()
            self.console.print(table)
            self.console.print()
            
            # Let user select
            selection = Prompt.ask(
                f"Select default model [1-{len(models)}] or enter custom name",
                default="1",
                console=self.console
            )
            
            # Parse selection
            try:
                idx = int(selection)
                if 1 <= idx <= len(models):
                    default_model = models[idx - 1]
                else:
                    default_model = selection
            except ValueError:
                default_model = selection
        else:
            # Manual entry
            self.console.print(f"\n[{color}]Enter the model name you want to use[/{color}]")
            default_model = Prompt.ask(
                "Model name",
                default="llama3.3",
                console=self.console
            )
        
        # Keep-alive time
        self.console.print(f"\n[{color}]Set model keep-alive time[/{color}]")
        self.console.print("[dim]How long to keep the model loaded in GPU memory (minutes)[/dim]")
        self.console.print("[dim]0 = unload immediately, -1 = keep indefinitely[/dim]")
        
        keep_alive = Prompt.ask(
            "Keep-alive (minutes)",
            default="5",
            console=self.console
        )
        
        # Validate keep_alive is numeric
        try:
            keep_alive_val = int(keep_alive)
        except ValueError:
            self.console.print("[yellow]Invalid value, using default of 5 minutes[/yellow]")
            keep_alive = "5"
        
        # Summary
        self.console.print(f"\n[{color}]Configuration Summary:[/{color}]")
        self.console.print(f"  Base URL: {base_url}")
        self.console.print(f"  Default Model: {default_model}")
        self.console.print(f"  Keep-alive: {keep_alive} minutes")
        
        # Ask to save
        if Confirm.ask("\n💾 Save this configuration?", default=True, console=self.console):
            config = {
                "OLLAMA_BASE_URL": base_url,
                "DEFAULT_OLLAMA_MODEL": default_model,
                "OLLAMA_KEEP_ALIVE": keep_alive,
            }
            
            for key, value in config.items():
                self._save_to_env(key, value)
            
            self.console.print(f"\n[green]✓[/green] Saved to .env file")
            return config
        
        return None

    def _onboard_api_provider(self, provider: str, info: Dict) -> Optional[Dict[str, str]]:
        """Onboard API-based provider."""
        color = info["color"]
        api_key_name = info["api_key_name"]
        
        # Show instructions
        self.console.print(f"[{color}]📝 You'll need an API key from {info['name']}[/{color}]\n")
        
        # Check if they have one
        has_key = Confirm.ask(
            "Do you have an API key?",
            default=False,
            console=self.console
        )
        
        if not has_key:
            self.console.print(f"\n[{color}]Get your API key:[/{color}]")
            self.console.print(f"🔗 {info['signup_url']}\n")
            
            if not Confirm.ask("Ready to enter your API key?", default=True, console=self.console):
                self.console.print("\n[yellow]Setup cancelled. Run again when you have your API key.[/yellow]")
                return None
        
        # Get API key
        self.console.print()
        api_key = Prompt.ask(
            f"[{color}]Enter your {info['name']} API key[/{color}]",
            password=True,
            console=self.console
        )
        
        # Validate prefix
        if info["api_key_prefix"] and not api_key.startswith(info["api_key_prefix"]):
            self.console.print(
                f"\n[yellow]⚠️  Warning: {info['name']} API keys usually start with '{info['api_key_prefix']}'[/yellow]"
            )
            if not Confirm.ask("Continue anyway?", default=False, console=self.console):
                return None
        
        # Save
        if Confirm.ask("\n💾 Save API key to .env file?", default=True, console=self.console):
            self._save_to_env(api_key_name, api_key)
            self.console.print(f"\n[green]✓[/green] Saved {api_key_name} to .env")
            return {api_key_name: api_key}
        
        return {api_key_name: api_key}

    def _save_to_env(self, key: str, value: str):
        """Save to .env file."""
        env_file = Path.cwd() / ".env"
        
        # Read existing .env
        existing = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        existing[k] = v
        
        # Update
        existing[key] = value
        
        # Write back
        with open(env_file, 'w') as f:
            for k, v in existing.items():
                f.write(f"{k}={v}\n")
        
        # Also set in current environment
        os.environ[key] = value

    @staticmethod
    def quick_setup(provider: str, console: Console) -> bool:
        """Quick onboarding flow. Returns True if successful."""
        onboarding = ProviderOnboarding(console)
        result = onboarding.run_onboarding(provider)
        
        if result:
            console.print(f"\n[green bold]🎉 Setup complete![/green bold]")
            console.print(f"[dim]You can now use: agent chat --provider {provider}[/dim]\n")
            return True
        
        return False
