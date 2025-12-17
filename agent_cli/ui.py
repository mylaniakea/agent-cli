"""
Centralized UI module for Agent CLI using Rich and Prompt Toolkit.
Provides styled output, spinners, themes, and interactive session management.
"""

import sys
from typing import Any, Dict, List

# Prompt Toolkit imports
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style as PromptStyle
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status
from rich.table import Table
from rich.theme import Theme

# Define preset themes
PRESET_THEMES = {
    "default": {
        "info": "dim cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "prompt": "cyan",
        "user_input": "bold white",
        "assistant": "green",
        "code": "bright_black",
        "header": "bold blue",
        "panel.border": "blue",
        "status.bar": "blue on black",
        "completion-menu.completion": "black on #e0e0e0",
        "completion-menu.completion.current": "white on #4a9eff",
        "completion-menu.meta.completion": "#888888 on #f5f5f5",
        "completion-menu.meta.completion.current": "#cccccc on #4a9eff",
        "prompt.border": "blue",
        "prompt.text": "bold white",
        "border.pattern": "solid",  # solid, hashed, morse
    },
    "catppuccin": {
        "info": "#89b4fa",  # blue
        "warning": "#f9e2af",  # yellow
        "error": "#f38ba8",  # red
        "success": "#a6e3a1",  # green
        "prompt": "#cba6f7",  # mauve
        "user_input": "#cdd6f4",  # text
        "assistant": "#a6e3a1",  # green
        "code": "#6c7086",  # overlay0
        "header": "#89b4fa",  # blue
        "panel.border": "#cba6f7",  # mauve
        "status.bar": "#1e1e2e on #89b4fa",  # base on blue
        "completion-menu.completion": "#cdd6f4 on #1e1e2e",
        "completion-menu.completion.current": "#1e1e2e on #cba6f7",
        "completion-menu.meta.completion": "#cdd6f4 on #1e1e2e",
        "completion-menu.meta.completion.current": "#1e1e2e on #cba6f7",
        "prompt.border": "#cba6f7",
        "prompt.text": "#cdd6f4",
        "border.pattern": "hashed",
    },
    "dracula": {
        "info": "#8be9fd",  # cyan
        "warning": "#f1fa8c",  # yellow
        "error": "#ff5555",  # red
        "success": "#50fa7b",  # green
        "prompt": "#bd93f9",  # purple
        "user_input": "#f8f8f2",  # foreground
        "assistant": "#50fa7b",  # green
        "code": "#6272a4",  # comment
        "header": "#bd93f9",  # purple
        "panel.border": "#bd93f9",  # purple
        "status.bar": "#282a36 on #bd93f9",  # background on purple
        "completion-menu.completion": "#f8f8f2 on #282a36",
        "completion-menu.completion.current": "#282a36 on #bd93f9",
        "completion-menu.meta.completion": "#f8f8f2 on #282a36",
        "completion-menu.meta.completion.current": "#282a36 on #bd93f9",
        "prompt.border": "#bd93f9",
        "prompt.text": "#f8f8f2",
        "border.pattern": "morse",
    },
    "monokai": {
        "info": "#66d9ef",  # blue
        "warning": "#fd971f",  # orange
        "error": "#f92672",  # pink
        "success": "#a6e22e",  # green
        "prompt": "#ae81ff",  # purple
        "user_input": "#f8f8f2",  # white
        "assistant": "#a6e22e",  # green
        "code": "#75715e",  # grey
        "header": "#66d9ef",  # blue
        "panel.border": "#ae81ff",
        "status.bar": "#272822 on #66d9ef",
        "completion-menu.completion": "#f8f8f2 on #272822",
        "completion-menu.completion.current": "#272822 on #ae81ff",
        "completion-menu.meta.completion": "#f8f8f2 on #272822",
        "completion-menu.meta.completion.current": "#272822 on #ae81ff",
        "prompt.border": "#ae81ff",
        "prompt.text": "#f8f8f2",
        "border.pattern": "solid",
    },
    "simple": {
        "info": "ansiblue",
        "warning": "ansiyellow",
        "error": "ansired",
        "success": "ansigreen",
        "prompt": "ansiwhite",
        "user_input": "ansiwhite",
        "assistant": "ansiwhite",
        "code": "ansiwhite",
        "header": "ansiblue",
        "panel.border": "ansiblue",
        "status.bar": "ansiblue",
        "completion-menu.completion": "black on #e0e0e0",
        "completion-menu.completion.current": "white on #4a9eff",
        "completion-menu.meta.completion": "#888888 on #f5f5f5",
        "completion-menu.meta.completion.current": "#cccccc on #4a9eff",
        "prompt.border": "ansiwhite",
        "prompt.text": "bold ansiwhite",
        "border.pattern": "solid",
    },
    "solarized": {
        "info": "#268bd2",  # blue
        "warning": "#b58900",  # yellow
        "error": "#dc322f",  # red
        "success": "#859900",  # green
        "prompt": "#2aa198",  # cyan
        "user_input": "#839496",  # base0
        "assistant": "#859900",  # green
        "code": "#586e75",  # base01
        "header": "#268bd2",  # blue
        "panel.border": "#2aa198",
        "status.bar": "#002b36 on #2aa198",
        "completion-menu.completion": "#839496 on #002b36",
        "completion-menu.completion.current": "#002b36 on #2aa198",
        "completion-menu.meta.completion": "#839496 on #002b36",
        "completion-menu.meta.completion.current": "#002b36 on #2aa198",
        "prompt.border": "#2aa198",
        "prompt.text": "#839496",
        "border.pattern": "hashed",
    },
    "nord": {
        "info": "#88c0d0",  # cyan
        "warning": "#ebcb8b",  # yellow
        "error": "#bf616a",  # red
        "success": "#a3be8c",  # green
        "prompt": "#81a1c1",  # blue
        "user_input": "#eceff4",  # white
        "assistant": "#a3be8c",  # green
        "code": "#4c566a",  # bright black
        "header": "#88c0d0",  # cyan
        "panel.border": "#81a1c1",
        "status.bar": "#2e3440 on #88c0d0",
        "completion-menu.completion": "#eceff4 on #2e3440",
        "completion-menu.completion.current": "#2e3440 on #81a1c1",
        "completion-menu.meta.completion": "#eceff4 on #2e3440",
        "completion-menu.meta.completion.current": "#2e3440 on #81a1c1",
        "prompt.border": "#81a1c1",
        "prompt.text": "#eceff4",
        "border.pattern": "morse",
    },
    "gruvbox": {
        "info": "#83a598",  # blue
        "warning": "#fabd2f",  # yellow
        "error": "#fb4934",  # red
        "success": "#b8bb26",  # green
        "prompt": "#d3869b",  # purple
        "user_input": "#ebdbb2",  # white
        "assistant": "#b8bb26",  # green
        "code": "#928374",  # gray
        "header": "#83a598",  # blue
        "panel.border": "#d3869b",
        "status.bar": "#282828 on #83a598",
        "completion-menu.completion": "#ebdbb2 on #282828",
        "completion-menu.completion.current": "#282828 on #d3869b",
        "completion-menu.meta.completion": "#ebdbb2 on #282828",
        "completion-menu.meta.completion.current": "#282828 on #d3869b",
        "prompt.border": "#d3869b",
        "prompt.text": "#ebdbb2",
        "border.pattern": "solid",
    },
    "tokyo-night": {
        "info": "#7dcfff",  # cyan
        "warning": "#e0af68",  # yellow
        "error": "#f7768e",  # red
        "success": "#9ece6a",  # green
        "prompt": "#bb9af7",  # purple
        "user_input": "#c0caf5",  # white
        "assistant": "#9ece6a",  # green
        "code": "#565f89",  # comment
        "header": "#7aa2f7",  # blue
        "panel.border": "#bb9af7",
        "status.bar": "#1a1b26 on #7aa2f7",
        "completion-menu.completion": "#c0caf5 on #1a1b26",
        "completion-menu.completion.current": "#1a1b26 on #bb9af7",
        "completion-menu.meta.completion": "#c0caf5 on #1a1b26",
        "completion-menu.meta.completion.current": "#1a1b26 on #bb9af7",
        "prompt.border": "#bb9af7",
        "prompt.text": "#c0caf5",
        "border.pattern": "hashed",
    },
    "one-dark": {
        "info": "#61afef",  # blue
        "warning": "#e5c07b",  # yellow
        "error": "#e06c75",  # red
        "success": "#98c379",  # green
        "prompt": "#c678dd",  # purple
        "user_input": "#abb2bf",  # white
        "assistant": "#98c379",  # green
        "code": "#5c6370",  # grey
        "header": "#61afef",  # blue
        "panel.border": "#c678dd",
        "status.bar": "#282c34 on #61afef",
        "completion-menu.completion": "#abb2bf on #282c34",
        "completion-menu.completion.current": "#282c34 on #c678dd",
        "completion-menu.meta.completion": "#abb2bf on #282c34",
        "completion-menu.meta.completion.current": "#282c34 on #c678dd",
        "prompt.border": "#c678dd",
        "prompt.text": "#abb2bf",
        "border.pattern": "morse",
    },
    "synthwave": {
        "info": "#36f9f6",  # cyan neon
        "warning": "#f9d336",  # yellow neon
        "error": "#ff2a6d",  # pink neon
        "success": "#05ffa1",  # green neon
        "prompt": "#b967ff",  # purple neon
        "user_input": "#ffffff",  # white
        "assistant": "#05ffa1",  # green
        "code": "#2b2b2b",  # dark grey
        "header": "#36f9f6",  # cyan neon
        "panel.border": "#b967ff",
        "status.bar": "#120458 on #ff2a6d",
        "completion-menu.completion": "#ffffff on #120458",
        "completion-menu.completion.current": "#120458 on #36f9f6",
        "completion-menu.meta.completion": "#ffffff on #120458",
        "completion-menu.meta.completion.current": "#120458 on #36f9f6",
        "prompt.border": "#b967ff",
        "prompt.text": "#ffffff",
        "border.pattern": "solid",
    },
}


class ThemeManager:
    """Manages UI themes."""

    def __init__(self, console: Console):
        self.console = console
        self.current_theme_name = "default"
        self.current_theme_data = PRESET_THEMES["default"]  # Store full data

    def set_theme(self, theme_name: str):
        """Set the current theme."""
        if theme_name not in PRESET_THEMES:
            raise ValueError(f"Theme '{theme_name}' not found.")

        self.current_theme_name = theme_name
        self.current_theme_data = PRESET_THEMES[theme_name]

        # Filter out non-style keys before creating Rich Theme
        styles = {k: v for k, v in self.current_theme_data.items() if k != "border.pattern"}
        self.console.push_theme(Theme(styles, inherit=False))

    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return list(PRESET_THEMES.keys())

    def get_current_style_for_prompt(self) -> PromptStyle:
        """Get a prompt_toolkit style object matching the current theme."""
        # Map Rich styles to prompt_toolkit styles
        rich_styles = self.current_theme_data

        def convert_style(rich_style: str) -> str:
            """Convert 'fg on bg' to 'fg bg:bg'."""
            if " on " in rich_style:
                fg, bg = rich_style.split(" on ")
                return f"{fg} bg:{bg}"
            return rich_style

        # Basic style from prompt/toolbar colors
        base_style = {
            "prompt": convert_style(rich_styles["prompt"]),
            "bottom-toolbar": convert_style(rich_styles.get("status.bar", "reverse")),
            "bottom-toolbar.text": "#ffffff",
            # Add borders
            "prompt.border": convert_style(rich_styles.get("prompt.border", rich_styles["prompt"])),
            "prompt.text": convert_style(rich_styles.get("prompt.text", "#ffffff")),
        }

        # Add completion menu styles if defined (using direct mapping)
        # prompt_toolkit expects exact class names
        if "completion-menu.completion" in rich_styles:
            base_style["completion-menu.completion"] = convert_style(
                rich_styles["completion-menu.completion"]
            )
            base_style["completion-menu.completion.current"] = convert_style(
                rich_styles["completion-menu.completion.current"]
            )
            base_style["completion-menu.meta.completion"] = convert_style(
                rich_styles["completion-menu.meta.completion"]
            )
            base_style["completion-menu.meta.completion.current"] = convert_style(
                rich_styles["completion-menu.meta.completion.current"]
            )

        return PromptStyle.from_dict(base_style)


from prompt_toolkit.shortcuts import CompleteStyle, PromptSession


class InteractiveSession:
    """Manages the interactive prompt session."""

    class SlashCommandCompleter(Completer):
        """Custom completer for slash commands to handle / prefix correctly."""

        def __init__(self, commands: Dict[str, Any], ui_manager):
            self.commands = commands
            self.ui = ui_manager

        def get_completions(self, document, complete_event):
            text = document.text_before_cursor

            # If line works with slash
            if text.startswith("/"):
                parts = text.split()

                # Case 1: Typing the command itself (e.g. "/mod")
                if len(parts) <= 1 and (not text.endswith(" ")):
                    current = parts[0] if parts else "/"
                    for cmd in self.commands.keys():
                        if cmd.startswith(current):
                            # Remove the slash for display if needed, but yield full command
                            yield Completion(cmd, start_position=-len(current))

                # Case 2: Typing arguments (e.g. "/model gpt")
                elif len(parts) >= 1:
                    cmd = parts[0]
                    if cmd in self.commands:
                        sub = self.commands[cmd]
                        # If sub is a dict (like model list or provider list)
                        if isinstance(sub, dict):
                            # Get the current arg text
                            # text is "/model gpt" -> arg is "gpt"
                            # But wait, parts include the cmd.
                            # If text ends with space, we are at start of new arg.
                            if text.endswith(" "):
                                current_arg = ""
                            else:
                                current_arg = parts[-1]

                            for sub_cmd in sub.keys():
                                if sub_cmd.startswith(current_arg):
                                    yield Completion(sub_cmd, start_position=-len(current_arg))

    def __init__(self, ui_manager):
        self.ui = ui_manager
        # Initial completer dictionary
        # Helper for set options
        config_keys = {
            "ollama_base_url": None,
            "openai_api_key": None,
            "anthropic_api_key": None,
            "google_api_key": None,
            "default_ollama_model": None,
            "default_openai_model": None,
            "default_anthropic_model": None,
            "default_google_model": None,
            "THEME": None,
        }

        self.completer_dict = {
            "/help": None,
            "/model": None,
            "/provider": {"ollama": None, "openai": None, "anthropic": None, "google": None},
            "/stream": {"true": None, "false": None},
            "/clear": None,
            "/history": None,
            "/session": None,
            "/config": None,
            "/mcp": None,
            "/set": config_keys,
            "/theme": {t: None for t in ui_manager.theme_manager.get_available_themes()},
            "/agent": {"create": None, "list": None, "use": None, "delete": None, "show": None},
            "/keepalive": None,
            "/reasoning": None,
            "/compress": None,
            "/beads": {"status": None, "context": None},
            "exit": None,
            "quit": None,
        }

        self.slash_completer = InteractiveSession.SlashCommandCompleter(
            self.completer_dict, self.ui
        )

        self.session = PromptSession(
            completer=self.slash_completer,
            style=self.ui.theme_manager.get_current_style_for_prompt(),
            complete_while_typing=True,
            complete_style=CompleteStyle.MULTI_COLUMN,
        )
        self.provider = "Unknown"
        self.model = "Unknown"
        self.is_connected = False

    def update_status(self, provider: str, model: str, connected: bool = True):
        """Update status bar info."""
        self.provider = provider
        self.model = model
        self.is_connected = connected

    def update_completion_models(self, models: List[str]):
        """Update the list of models for autocomplete."""
        # Update the dict directly
        self.completer_dict["/model"] = {m: None for m in models}
        # Re-initialize completer with updated dict
        self.slash_completer.commands = self.completer_dict

    def _get_provider_icon(self, provider: str) -> str:
        """Get emoji/icon for provider."""
        icons = {
            "openai": "🤖",      # Robot for ChatGPT/OpenAI
            "anthropic": "🧠",   # Brain for Claude
            "google": "✨",      # Sparkle for Gemini
            "ollama": "🦙",      # Llama for Ollama
        }
        return icons.get(provider.lower(), "💬")  # Default chat bubble

    def _get_toolbar_tokens(self):
        """Generate tokens for the bottom status toolbar."""
        # Define styles for the toolbar components
        style_model = "class:toolbar.model"
        style_stats = "class:toolbar.stats"
        style_timer = "class:toolbar.timer"
        style_meta = "class:toolbar.meta"

        tokens = []

        # Connection status indicator
        conn_symbol = "*" if self.is_connected else "x"
        conn_color = "ansigreen" if self.is_connected else "ansired"
        tokens.append((f"fg:{conn_color}", f" {conn_symbol} "))

        # Model & Provider
        tokens.append((style_model, f"{self.model} "))
        tokens.append((style_meta, f"({self.provider})"))

        # Usage Stats
        if hasattr(self, "agent") and hasattr(self.agent, "get_last_usage"):
            usage = self.agent.get_last_usage()
            if usage["total_tokens"] > 0:
                p = usage["prompt_tokens"]
                c = usage["completion_tokens"]
                t = usage["total_tokens"]
                tokens.append((style_stats, f" | In:{p} Out:{c} Total:{t}"))

        # Timer
        if hasattr(self, "agent") and hasattr(self.agent, "get_time_remaining"):
            remaining = self.agent.get_time_remaining()
            if remaining:
                tokens.append((style_stats, " | Expires: "))
                if remaining == "Expired":
                    tokens.append(("ansired bold", remaining))
                else:
                    tokens.append((style_timer, remaining))

        return tokens

    def prompt(self, default: str = "") -> str:
        """Get input from user with encapsulated style."""
        # Update style before prompt in case theme changed
        self.session.style = self.ui.theme_manager.get_current_style_for_prompt()

        # Get border properties from current theme
        theme_name = self.ui.theme_manager.current_theme_name

        # --- SIMPLE THEME (No Box) ---
        if theme_name == "simple":
            # Function to generate status bar content (Keep status bar in simple mode)
            def get_bottom_toolbar_simple():
                return self._get_toolbar_tokens()

            # Minimal toolbar style
            from prompt_toolkit.styles import Style, merge_styles

            simple_toolbar = Style.from_dict(
                {
                    "bottom-toolbar": "noreverse",
                    "toolbar.model": "bold",
                    "toolbar.stats": "#888888",
                    "toolbar.timer": "ansiyellow",
                    "toolbar.meta": "italic #888888",
                }
            )
            final_style = merge_styles([self.session.style, simple_toolbar])

            return self.session.prompt(
                [("class:prompt.text", f"You {self._get_provider_icon(self.provider)} ➜ ")],
                bottom_toolbar=get_bottom_toolbar_simple,
                style=final_style,
                refresh_interval=1.0,
            )

        # --- BOXED THEME (Standard) ---
        rich_styles = PRESET_THEMES[theme_name]
        border_color = rich_styles.get("prompt.border", "blue")
        border_pattern = rich_styles.get("border.pattern", "solid")

        # Define patterns
        if border_pattern == "morse":
            char = ".-"
        elif border_pattern == "hashed":
            char = "//"
        else:  # solid
            char = "─"

        # Create borders using console width
        width = self.ui.console.width

        # Helper to generate border line
        def make_border(start_char, end_char):
            target_len = max(0, width - 2)
            if border_pattern == "solid":
                b_str = (char * target_len)[:target_len]
            else:
                repeats = (target_len // len(char)) + 1
                b_str = (char * repeats)[:target_len]
            return f"{start_char}{b_str}{end_char}"

        top_border = make_border("╭", "╮")
        bottom_border_str = make_border("╰", "╯")


        # Print top border using Rich
        self.ui.console.print(f"[{border_color}]{top_border}[/{border_color}]")

        # Function for right border
        def get_rprompt():
            return [("class:rprompt", "│")]

        # Define custom style for toolbar
        from prompt_toolkit.styles import Style, merge_styles

        # Base style from theme manager
        base_style = self.ui.theme_manager.get_current_style_for_prompt()

        # Toolbar style
        toolbar_style = Style.from_dict(
            {
                "rprompt": f"{border_color} bg:default",
                "prompt.border": border_color,
            }
        )

        final_style = merge_styles([base_style, toolbar_style])

        # Bottom toolbar shows the bottom border persistently
        def get_bottom_toolbar():
            return [("class:prompt.border", bottom_border_str)]

        # Use a prompt that mimics a left border
        result = self.session.prompt(
            [("class:prompt.border", "│ "), ("class:prompt.text", f"You {self._get_provider_icon(self.provider)} ➜ ")],
            bottom_toolbar=get_bottom_toolbar,
            rprompt=get_rprompt,
            style=final_style,
        )

        # Print bottom border to close the box
        self.ui.console.print(f"[{border_color}]{bottom_border_str}[/{border_color}]")

        return result


class UI:
    """Centralized UI manager."""

    def __init__(self):
        # Filter default theme styles
        default_styles = {
            k: v for k, v in PRESET_THEMES["default"].items() if k != "border.pattern"
        }
        self.console = Console(theme=Theme(default_styles))
        self.theme_manager = ThemeManager(self.console)
        self.interactive_session = InteractiveSession(self)

    def print_welcome(self):
        """Print the welcome banner."""
        title = r"""
    _                     _      ____ _     ___ 
   / \   __ _  ___ _ __ | |_   / ___| |   |_ _|
  / _ \ / _` |/ _ \ '_ \| __| | |   | |    | | 
 / ___ \ (_| |  __/ | | | |_  | |___| |___ | | 
/_/   \_\__, |\___|_| |_|\__|  \____|_____|___|
        |___/                                  
        """
        self.console.print(
            Panel(
                f"[bold blue]{title}[/bold blue]\n[dim]Interactive AI Agent CLI[/dim]",
                border_style="panel.border",
                expand=False,
            )
        )
        self.console.print("\nType [bold cyan]/help[/bold cyan] to see available commands.\n")

    def print_markdown(self, text: str):
        """Render markdown text."""
        md = Markdown(text)
        self.console.print(md)

    def print_error(self, text: str):
        """Print an error message."""
        self.console.print(f"[error]Error:[/error] {text}")

    def print_success(self, text: str):
        """Print a success message."""
        self.console.print(f"[success]Success:[/success] {text}")

    def print_warning(self, text: str):
        """Print a warning message."""
        self.console.print(f"[warning]Warning:[/warning] {text}")

    def print_info(self, text: str):
        """Print an info message."""
        self.console.print(f"[info]{text}[/info]")

    def create_spinner(self, text: str) -> Status:
        """Create a status spinner."""
        return self.console.status(f"[bold blue]{text}[/bold blue]", spinner="dots")

    def print_table(self, title: str, columns: List[str], rows: List[List[str]]):
        """Print a styled table."""
        table = Table(title=title, show_header=True, header_style="header")
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

    def prompt_user(self, prompt_text: str = "You", default: Any = None) -> str:
        """Prompt the user for input. Deprecated in favor of interactive_session.prompt() for main loop."""
        return Prompt.ask(f"[prompt]{prompt_text}[/prompt]", console=self.console, default=default)

    def print_agent_response(self, text: str, model: str):
        """Print a completed agent response."""
        # Get dynamic status subtitle from session
        subtitle = self.interactive_session._get_status_subtitle()

        self.console.print(
            Panel(
                Markdown(text),
                title="[assistant]AI Response[/assistant]",  # Generic title or user pref
                subtitle=subtitle,
                subtitle_align="left",
                border_style="assistant",
                expand=False,
            )
        )

    def print_stream_chunk(self, chunk: str):
        """Print a chunk of streamed text (simple version)."""
        self.console.print(chunk, end="")

    def flush(self):
        """Flush the console output."""
        sys.stdout.flush()


# Global UI instance
ui = UI()
