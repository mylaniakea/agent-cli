"""
Centralized UI module for Agent CLI using Rich and Prompt Toolkit.
Provides styled output, spinners, themes, and interactive session management.
"""

import sys
from importlib.metadata import version
from typing import Any

# Prompt Toolkit imports
from prompt_toolkit import Application, PromptSession
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import ConditionalContainer, Float, FloatContainer, HSplit, Layout, VSplit, Window
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.styles import Style, merge_styles
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
        "status.bar": "#888888 on black",
        "completion-menu": "#ffffff on #2b2b2b",
        "completion-menu.completion": "#ffffff on #2b2b2b",
        "completion-menu.completion.current": "#ffffff on #4a9eff",
        "completion-menu.meta": "#888888 on #1a1a1a",
        "completion-menu.meta.completion": "#888888 on #1a1a1a",
        "completion-menu.meta.completion.current": "#cccccc on #4a9eff",
        "scrollbar.background": "on #1a1a1a",
        "scrollbar.button": "on #4a9eff",
        "prompt.border": "#888888",
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
        "completion-menu": "on #181825 #cdd6f4",
        "completion-menu.completion": "#cdd6f4 on #181825",
        "completion-menu.completion.current": "#1e1e2e on #cba6f7",
        "completion-menu.meta": "on #11111b #7f849c",
        "completion-menu.meta.completion": "#7f849c on #11111b",
        "completion-menu.meta.completion.current": "#1e1e2e on #cba6f7",
        "scrollbar.background": "on #11111b",
        "scrollbar.button": "on #cba6f7",
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
        "completion-menu": "on #21222c #f8f8f2",
        "completion-menu.completion": "#f8f8f2 on #21222c",
        "completion-menu.completion.current": "#282a36 on #bd93f9",
        "completion-menu.meta": "on #191a21 #6272a4",
        "completion-menu.meta.completion": "#6272a4 on #191a21",
        "completion-menu.meta.completion.current": "#282a36 on #bd93f9",
        "scrollbar.background": "on #191a21",
        "scrollbar.button": "on #bd93f9",
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
        "completion-menu": "on #1e1f1c #f8f8f2",
        "completion-menu.completion": "#f8f8f2 on #1e1f1c",
        "completion-menu.completion.current": "#272822 on #ae81ff",
        "completion-menu.meta": "on #131411 #75715e",
        "completion-menu.meta.completion": "#75715e on #131411",
        "completion-menu.meta.completion.current": "#272822 on #ae81ff",
        "scrollbar.background": "on #131411",
        "scrollbar.button": "on #ae81ff",
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
        "completion-menu": "on #1a1a1a ansiwhite",
        "completion-menu.completion": "ansiwhite on #1a1a1a",
        "completion-menu.completion.current": "ansiblack on ansiblue",
        "completion-menu.meta": "on #0a0a0a #888888",
        "completion-menu.meta.completion": "#888888 on #0a0a0a",
        "completion-menu.meta.completion.current": "ansiblack on ansiblue",
        "scrollbar.background": "on #0a0a0a",
        "scrollbar.button": "on ansiblue",
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
        "completion-menu": "on #073642 #839496",
        "completion-menu.completion": "#839496 on #073642",
        "completion-menu.completion.current": "#002b36 on #2aa198",
        "completion-menu.meta": "on #002b36 #586e75",
        "completion-menu.meta.completion": "#586e75 on #002b36",
        "completion-menu.meta.completion.current": "#002b36 on #2aa198",
        "scrollbar.background": "on #002b36",
        "scrollbar.button": "on #2aa198",
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
        "completion-menu": "on #3b4252 #eceff4",
        "completion-menu.completion": "#eceff4 on #3b4252",
        "completion-menu.completion.current": "#2e3440 on #81a1c1",
        "completion-menu.meta": "on #2e3440 #4c566a",
        "completion-menu.meta.completion": "#4c566a on #2e3440",
        "completion-menu.meta.completion.current": "#2e3440 on #81a1c1",
        "scrollbar.background": "on #2e3440",
        "scrollbar.button": "on #81a1c1",
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
        "completion-menu": "on #3c3836 #ebdbb2",
        "completion-menu.completion": "#ebdbb2 on #3c3836",
        "completion-menu.completion.current": "#282828 on #d3869b",
        "completion-menu.meta": "on #282828 #928374",
        "completion-menu.meta.completion": "#928374 on #282828",
        "completion-menu.meta.completion.current": "#282828 on #d3869b",
        "scrollbar.background": "on #282828",
        "scrollbar.button": "on #d3869b",
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
        "completion-menu": "on #24283b #c0caf5",
        "completion-menu.completion": "#c0caf5 on #24283b",
        "completion-menu.completion.current": "#1a1b26 on #bb9af7",
        "completion-menu.meta": "on #1a1b26 #565f89",
        "completion-menu.meta.completion": "#565f89 on #1a1b26",
        "completion-menu.meta.completion.current": "#1a1b26 on #bb9af7",
        "scrollbar.background": "on #1a1b26",
        "scrollbar.button": "on #bb9af7",
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
        "completion-menu": "on #353b45 #abb2bf",
        "completion-menu.completion": "#abb2bf on #353b45",
        "completion-menu.completion.current": "#282c34 on #c678dd",
        "completion-menu.meta": "on #282c34 #5c6370",
        "completion-menu.meta.completion": "#5c6370 on #282c34",
        "completion-menu.meta.completion.current": "#282c34 on #c678dd",
        "scrollbar.background": "on #282c34",
        "scrollbar.button": "on #c678dd",
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
        "completion-menu": "on #241b2f #ffffff",
        "completion-menu.completion": "#ffffff on #241b2f",
        "completion-menu.completion.current": "#120458 on #36f9f6",
        "completion-menu.meta": "on #120458 #ff6ac1",
        "completion-menu.meta.completion": "#ff6ac1 on #120458",
        "completion-menu.meta.completion.current": "#120458 on #36f9f6",
        "scrollbar.background": "on #120458",
        "scrollbar.button": "on #b967ff",
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

        # Filter out non-Rich style keys before creating Rich Theme
        # (completion-menu and scrollbar are prompt_toolkit-only styles)
        excluded_keys = {
            "border.pattern",
            "completion-menu",
            "completion-menu.completion",
            "completion-menu.completion.current",
            "completion-menu.meta",
            "completion-menu.meta.completion",
            "completion-menu.meta.completion.current",
            "scrollbar.background",
            "scrollbar.button",
        }
        styles = {k: v for k, v in self.current_theme_data.items() if k not in excluded_keys}
        self.console.push_theme(Theme(styles, inherit=False))

    def get_available_themes(self) -> list[str]:
        """Get list of available themes."""
        return list(PRESET_THEMES.keys())

    def get_current_style_for_prompt(self) -> Style:
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

        return Style.from_dict(base_style)


class InteractiveSession:
    """Manages the interactive prompt session."""

    class CommandMenu:
        """Custom pop-out menu for showing all commands at once."""

        def __init__(self):
            self.visible = False
            self.selected_index = 0
            self.commands = []  # List of (cmd, description) tuples

        def show(self, commands):
            """Show menu with given commands."""
            self.commands = commands
            self.visible = True
            self.selected_index = 0

        def hide(self):
            """Hide the menu."""
            self.visible = False
            self.commands = []
            self.selected_index = 0

        def move_up(self):
            """Move selection up."""
            if self.commands:
                self.selected_index = max(0, self.selected_index - 1)

        def move_down(self):
            """Move selection down."""
            if self.commands:
                self.selected_index = min(len(self.commands) - 1, self.selected_index + 1)

        def get_selected(self):
            """Get currently selected command."""
            if self.commands and 0 <= self.selected_index < len(self.commands):
                return self.commands[self.selected_index][0]
            return None

        def render(self):
            """Render menu as formatted text in spreadsheet style."""
            if not self.visible or not self.commands:
                return []

            lines = []
            # Top border with title
            lines.append(("class:menu.border", "╔══════════════════╦══════════════════════════════════════════════╗\n"))
            lines.append(("class:menu.border", "║ "))
            lines.append(("class:menu.title", "Command          "))
            lines.append(("class:menu.border", "║ "))
            lines.append(("class:menu.title", "Description                                  "))
            lines.append(("class:menu.border", "║\n"))
            lines.append(("class:menu.border", "╠══════════════════╬══════════════════════════════════════════════╣\n"))

            # Commands with horizontal separators
            for idx, (cmd, desc) in enumerate(self.commands):
                is_selected = idx == self.selected_index

                if is_selected:
                    # Highlighted row with vertical separator
                    lines.append(("class:menu.selected", "║ "))
                    lines.append(("class:menu.selected", f"▶ {cmd:<15} "))
                    lines.append(("class:menu.selected", "║ "))
                    lines.append(("class:menu.selected.desc", f"{desc:<45}"))
                    lines.append(("class:menu.selected", "║\n"))
                else:
                    # Normal row with vertical separator
                    lines.append(("class:menu.border", "║ "))
                    lines.append(("class:menu.normal", f"  {cmd:<15} "))
                    lines.append(("class:menu.border", "║ "))
                    lines.append(("class:menu.desc", f"{desc:<45}"))
                    lines.append(("class:menu.border", "║\n"))

                # Add horizontal separator between rows (except last)
                if idx < len(self.commands) - 1:
                    if is_selected or (idx + 1 < len(self.commands) and self.selected_index == idx + 1):
                        # Use selected style for separator near selection
                        lines.append(("class:menu.selected", "╟──────────────────╫──────────────────────────────────────────────╢\n"))
                    else:
                        lines.append(("class:menu.separator", "╟──────────────────╫──────────────────────────────────────────────╢\n"))

            # Bottom border with instructions
            lines.append(("class:menu.border", "╚══════════════════╩══════════════════════════════════════════════╝\n"))
            lines.append(("class:menu.instructions", "  ↑↓ navigate  │  ENTER select  │  ESC cancel  "))

            return lines

    class SlashCommandCompleter(Completer):
        """Custom completer for slash commands to handle / prefix correctly."""

        def __init__(self, commands: dict[str, Any], ui_manager):
            self.commands = commands
            self.ui = ui_manager
            # Command descriptions for display
            self.descriptions = {
                "/help": "Show available commands",
                "/model": "Switch or show current model",
                "/provider": "Switch or show current provider",
                "/stream": "Toggle streaming mode",
                "/clear": "Clear conversation history",
                "/history": "Show recent conversation",
                "/session": "Show session info",
                "/config": "Show configuration",
                "/mcp": "Manage MCP servers",
                "/set": "Set configuration value",
                "/theme": "Change UI theme",
                "/agent": "Manage specialized agents (personas)",
                "/bead": "Manage personality beads",
                "/keepalive": "Set Ollama keep-alive",
                "/reasoning": "Toggle reasoning display",
                "/compress": "Compress history",
                "/beads": "Beads CLI integration (external tool)",
                "/export": "Export conversation",
                "/system": "Set system prompt",
                "/project": "Project configuration",
            }

        def get_completions(self, document, complete_event):
            text = document.text_before_cursor

            # If line works with slash
            if text.startswith("/"):
                parts = text.split()

                # Case 1: Typing the command itself (e.g. "/mod")
                if len(parts) <= 1 and (not text.endswith(" ")):
                    current = parts[0] if parts else "/"

                    # Show ALL commands when user types just "/"
                    # This creates a full popup menu of all available commands
                    for cmd in sorted(self.commands.keys()):
                        if cmd.startswith(current):
                            description = self.descriptions.get(cmd, "")
                            # Yield completion with description
                            yield Completion(
                                cmd,
                                start_position=-len(current),
                                display=cmd,
                                display_meta=description,
                            )

                # Case 2: Typing arguments (e.g. "/model gpt")
                elif len(parts) >= 1:
                    cmd = parts[0]
                    if cmd in self.commands:
                        sub = self.commands[cmd]
                        # If sub is a dict (like model list or provider list)
                        if isinstance(sub, dict):
                            # Get the current arg text
                            current_arg = "" if text.endswith(" ") else parts[-1]

                            for sub_cmd in sorted(sub.keys()):
                                if sub_cmd.startswith(current_arg):
                                    yield Completion(
                                        sub_cmd,
                                        start_position=-len(current_arg),
                                        display=sub_cmd,
                                    )

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

        # Build completer dict from registered commands
        # Try to load from command registry, but fall back to basic list if not available
        try:
            from agent_cli.command_registry import get_all_commands

            registered_commands = get_all_commands()
            self.completer_dict = {}

            # Add all registered commands
            for cmd_name, cmd_info in registered_commands.items():
                # Only add primary command names (not aliases)
                if cmd_name == cmd_info.name:
                    self.completer_dict[f"/{cmd_name}"] = None

        except (ImportError, Exception):
            # Fallback to basic command list if registry not available
            self.completer_dict = {
                "/help": None,
                "/model": None,
                "/provider": None,
                "/stream": None,
                "/clear": None,
                "/history": None,
                "/session": None,
                "/config": None,
                "/mcp": None,
                "/set": None,
                "/theme": None,
                "/agent": None,
                "/keepalive": None,
                "/reasoning": None,
                "/compress": None,
                "/beads": None,
                "/init": None,
                "/context": None,
                "/hooks": None,
            }

        # Add special completions for specific commands
        if "/provider" in self.completer_dict:
            self.completer_dict["/provider"] = {"ollama": None, "openai": None, "anthropic": None, "google": None}

        if "/stream" in self.completer_dict:
            self.completer_dict["/stream"] = {"true": None, "false": None}

        if "/set" in self.completer_dict:
            self.completer_dict["/set"] = config_keys

        if "/theme" in self.completer_dict:
            self.completer_dict["/theme"] = {t: None for t in ui_manager.theme_manager.get_available_themes()}

        if "/agent" in self.completer_dict:
            self.completer_dict["/agent"] = {"create": None, "list": None, "use": None, "delete": None, "show": None}

        if "/beads" in self.completer_dict:
            self.completer_dict["/beads"] = {"status": None, "context": None}

        # Add subcommands for new commands
        if "/context" in self.completer_dict:
            self.completer_dict["/context"] = {"status": None, "update": None, "view": None, "add": None}

        if "/hooks" in self.completer_dict:
            self.completer_dict["/hooks"] = {"install": None, "uninstall": None, "list": None}

        # Add common exit commands
        self.completer_dict["exit"] = None
        self.completer_dict["quit"] = None

        self.slash_completer = InteractiveSession.SlashCommandCompleter(
            self.completer_dict, self.ui
        )

        # Create custom command menu for pop-out display
        self.command_menu = InteractiveSession.CommandMenu()

        # Note: PromptSession will show completion menu automatically when configured
        # The MULTI_COLUMN style should display completions in a table format
        self.session = PromptSession(
            completer=self.slash_completer,
            style=self.ui.theme_manager.get_current_style_for_prompt(),
            complete_while_typing=True,
            complete_in_thread=True,
            complete_style=CompleteStyle.MULTI_COLUMN,  # Shows all options in columns
            enable_open_in_editor=False,
            mouse_support=True,  # Enable mouse for completion menu
        )
        self.provider = "Unknown"
        self.model = "Unknown"
        self.is_connected = False
        self.active_beads = []  # List of PersonalityBead objects

    def update_status(self, provider: str, model: str, connected: bool = True):
        """Update status bar info."""
        self.provider = provider
        self.model = model
        self.is_connected = connected

    def set_active_beads(self, beads: list):
        """Set the active personality beads for display.

        Args:
            beads: List of PersonalityBead objects
        """
        self.active_beads = beads if beads else []

    def _build_prompt_tokens(self) -> list:
        """Build prompt tokens including icon, name, bead pills, and arrow.

        Returns:
            List of (style, text) tuples for FormattedText
        """
        icon = self._get_provider_icon(self.provider)
        prompt_name = self.ui.config.prompt_name

        # Build prompt tokens
        tokens = [
            ("class:prompt", f"{icon} {prompt_name} "),
        ]

        # Add bead pills if any active
        if self.active_beads:
            try:
                from agent_cli.personality_beads import render_bead_pills

                pill_tokens = render_bead_pills(self.active_beads, theme=None, max_display=5)
                tokens.extend(pill_tokens)
            except Exception:
                pass  # Silently fail if pills can't render

        # Add arrow
        tokens.append(("class:prompt", "➜ "))

        return tokens

    def update_completion_models(self, models: list[str]):
        """Update the list of models for autocomplete."""
        # Update the dict directly
        self.completer_dict["/model"] = {m: None for m in models}
        # Re-initialize completer with updated dict
        self.slash_completer.commands = self.completer_dict

    def _shorten_model_name(self, model: str) -> str:
        """Shorten long model names for display."""
        if not model or model == "Unknown":
            return model

        # Remove version tags and suffixes after : or @ symbols
        # e.g., "devstral-small-2:24b" -> "devstral-small"
        base_name = model.split(":")[0].split("@")[0]

        # If still too long (>20 chars), truncate with ellipsis
        if len(base_name) > 20:
            return base_name[:17] + "..."

        return base_name

    def _has_nerd_fonts(self) -> bool:
        """Check if Nerd Fonts are available."""
        # Check if NERD_FONT env var is set
        import os
        if os.getenv("NERD_FONT") == "1":
            return True

        # Try to detect by checking common Nerd Font names in terminal
        term_program = os.getenv("TERM_PROGRAM", "")
        font_name = os.getenv("FONT_NAME", "")

        # Common indicators
        if "nerd" in font_name.lower() or "nf" in font_name.lower():
            return True

        # Default to False (use emojis) - user can set NERD_FONT=1 to enable
        return False

    def _get_provider_icon(self, provider: str) -> str:
        """Get emoji/icon for provider with Nerd Font support."""

        if self._has_nerd_fonts():
            # Nerd Font icons (requires Nerd Font installed)
            nerd_icons = {
                "openai": "",  # nf-md-robot icon
                "anthropic": "",  # nf-md-brain icon
                "google": "",  # nf-md-google icon
                "ollama": "󰝰",  # nf-md-llama icon (or  for meta)
            }
            icon = nerd_icons.get(provider.lower(), "")
            if icon:
                return icon

        # Fallback to emojis (works everywhere)
        emoji_icons = {
            "openai": "🤖",  # Robot for ChatGPT/OpenAI
            "anthropic": "🧠",  # Brain for Claude
            "google": "✨",  # Sparkle for Gemini
            "ollama": "🦙",  # Llama for Ollama
        }
        return emoji_icons.get(provider.lower(), "💬")  # Default chat bubble

    def _get_toolbar_tokens(self):
        """Generate tokens for the bottom status toolbar."""
        # Define styles for the toolbar components
        style_model = "class:toolbar.model"
        style_stats = "class:toolbar.stats"
        style_timer = "class:toolbar.timer"

        tokens = []

        # Connection status indicator
        conn_symbol = "*" if self.is_connected else "x"
        conn_color = "ansigreen" if self.is_connected else "ansired"
        tokens.append((f"fg:{conn_color}", f" {conn_symbol} "))

        # Provider icon only
        provider_icon = self._get_provider_icon(self.provider)
        tokens.append((style_model, f"{provider_icon} "))

        # Usage Stats
        if hasattr(self, "agent") and hasattr(self.agent, "get_last_usage"):
            usage = self.agent.get_last_usage()
            if usage["total_tokens"] > 0:
                p = usage["prompt_tokens"]
                c = usage["completion_tokens"]
                t = usage["total_tokens"]
                tokens.append((style_stats, f" | In:{p} Out:{c} Total:{t}"))

        # Ollama keep-alive timer (only for ollama provider)
        if self.provider == "ollama":
            try:
                from agent_cli.ollama_manager import get_ollama_manager

                ollama_mgr = get_ollama_manager()
                remaining_seconds = ollama_mgr.get_time_remaining()

                if remaining_seconds is not None and remaining_seconds > 0:
                    remaining_mins = remaining_seconds / 60
                    tokens.append((style_stats, " | "))
                    tokens.append((style_timer, f"⏱ {remaining_mins:.1f}m"))
            except Exception:
                pass  # Silently fail if ollama_manager not available

        return tokens

    def _get_status_subtitle(self) -> str:
        """Generate subtitle for response panels showing model and provider."""
        return f"{self.model} ({self.provider})"

    def prompt(self, default: str = "") -> str:
        """Get input from user with encapsulated style using custom container."""
        # Update style before prompt in case theme changed
        self.session.style = self.ui.theme_manager.get_current_style_for_prompt()

        # Get border properties from current theme
        theme_name = self.ui.theme_manager.current_theme_name

        # --- SIMPLE THEME (No Box) ---
        if theme_name == "simple":
            # Use regular session prompt for simple theme with completion menu
            def get_bottom_toolbar_simple():
                return self._get_toolbar_tokens()

            simple_toolbar = Style.from_dict(
                {
                    "bottom-toolbar": "noreverse",
                    "toolbar.model": "bold",
                    "toolbar.stats": "#888888",
                    "toolbar.timer": "ansiyellow",
                    "toolbar.meta": "italic #888888",
                    # Completion menu styles
                    "completion-menu": "bg:#1e1e1e #ffffff",
                    "completion-menu.completion": "bg:#1e1e1e #ffffff",
                    "completion-menu.completion.current": "bg:#4a9eff #000000 bold",
                    "completion-menu.meta.completion": "#888888",
                    "completion-menu.meta.completion.current": "#000000",
                    "scrollbar.background": "bg:#444444",
                    "scrollbar.button": "bg:#888888",
                }
            )
            final_style = merge_styles([self.session.style, simple_toolbar])

            # Build prompt tokens with beads
            prompt_tokens = self._build_prompt_tokens()

            return self.session.prompt(
                prompt_tokens,
                bottom_toolbar=get_bottom_toolbar_simple,
                style=final_style,
                refresh_interval=1.0,
                # Enable completion menu display
                complete_in_thread=True,
                complete_while_typing=True,
            )

        # --- BOXED THEME (Custom Container) ---
        rich_styles = PRESET_THEMES[theme_name]
        border_color = rich_styles.get("prompt.border", "#888888")
        char = rich_styles.get("prompt.border_char", "─")
        border_pattern = rich_styles.get("prompt.border_pattern", "solid")

        # Create borders
        width = self.ui.console.width

        def make_border_line(start_char, end_char):
            target_len = max(0, width - 2)
            if border_pattern == "solid":
                b_str = (char * target_len)[:target_len]
            else:
                repeats = (target_len // len(char)) + 1
                b_str = (char * repeats)[:target_len]
            return f"{start_char}{b_str}{end_char}"

        top_border = make_border_line("╭", "╮")
        bottom_border = make_border_line("╰", "╯")

        # Display status line (with timer) if using ollama provider
        if self.provider == "ollama":
            try:
                from agent_cli.ollama_manager import get_ollama_manager

                ollama_mgr = get_ollama_manager()
                remaining_seconds = ollama_mgr.get_time_remaining()

                if remaining_seconds is not None and remaining_seconds > 0:
                    remaining_mins = remaining_seconds / 60
                    icon = self._get_provider_icon(self.provider)
                    status = f"{icon} | ⏱ {remaining_mins:.1f}m"
                    self.ui.console.print(f"[dim]{status}[/dim]", justify="right")
            except Exception:
                pass  # Silently fail if ollama_manager not available

        # Create buffer for input with completer attached
        buffer = Buffer(
            completer=self.slash_completer,
            complete_while_typing=True,
        )

        # Get theme colors for menu
        menu_bg = "#1e1e1e"  # Dark background
        menu_text = rich_styles.get("prompt.text", "#ffffff")
        menu_border = rich_styles.get("prompt.border", "#888888")
        menu_highlight_bg = rich_styles.get("panel.border", "#4a9eff")  # Use theme accent
        menu_highlight_text = "#000000"  # Black text on highlight
        menu_desc = "#888888"  # Dimmed description

        # Extract just color from rich style strings (handle "bold #color" format)
        if " " in menu_text:
            menu_text = menu_text.split()[-1]
        if " " in menu_highlight_bg:
            menu_highlight_bg = menu_highlight_bg.split()[-1]

        # Create style with theme-aware custom menu styling
        custom_style = Style.from_dict(
            {
                "border": border_color,
                "prompt": "bold",
                # Custom command menu styles (spreadsheet table)
                "menu.border": f"{menu_border}",  # Border lines
                "menu.title": f"bold {menu_highlight_bg}",  # Header row
                "menu.normal": f"{menu_text}",  # Normal command text
                "menu.desc": f"{menu_desc}",  # Description text
                "menu.selected": f"bg:{menu_highlight_bg} {menu_highlight_text} bold",  # Selected row
                "menu.selected.desc": f"bg:{menu_highlight_bg} {menu_highlight_text}",  # Selected description
                "menu.separator": f"{menu_border}",  # Row separators
                "menu.instructions": f"{menu_desc}",  # Bottom instructions
            }
        )
        final_style = merge_styles([self.session.style, custom_style])

        # Build layout with borders
        root_container = HSplit(
            [
                # Top border
                Window(
                    content=FormattedTextControl(text=[("class:border", top_border)]),
                    height=1,
                ),
                # Input line with left border, prompt, input, right border
                VSplit(
                    [
                        Window(
                            content=FormattedTextControl(text=[("class:border", "│ ")]),
                            width=2,
                        ),
                        Window(
                            content=FormattedTextControl(
                                text=self._build_prompt_tokens()
                            ),
                            dont_extend_width=True,
                        ),
                        Window(content=BufferControl(buffer=buffer)),
                        Window(
                            content=FormattedTextControl(text=[("class:border", "│")]),
                            width=1,
                        ),
                    ]
                ),
                # Bottom border
                Window(
                    content=FormattedTextControl(text=[("class:border", bottom_border)]),
                    height=1,
                ),
            ]
        )

        # Wrap in FloatContainer with custom command menu
        # Create a window for the custom menu
        def calculate_menu_height():
            """Calculate height for spreadsheet menu with separators."""
            if not self.command_menu.visible:
                return 0
            # Top border (1) + Header (2) + Commands + Separators + Bottom (1) + Instructions (1)
            # Each command = 1 line, separator between = commands - 1
            num_commands = len(self.command_menu.commands)
            return 1 + 2 + num_commands + (num_commands - 1 if num_commands > 1 else 0) + 1 + 1

        menu_window = Window(
            content=FormattedTextControl(lambda: self.command_menu.render()),
            width=70,  # Fixed width for spreadsheet
            height=calculate_menu_height,
        )

        # FloatContainer with command menu that shows when visible
        float_container = FloatContainer(
            content=root_container,
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=ConditionalContainer(
                        content=menu_window,
                        filter=Condition(lambda: self.command_menu.visible),
                    ),
                )
            ],
        )

        layout = Layout(float_container, focused_element=buffer)

        # Key bindings
        kb = KeyBindings()

        @kb.add("enter")
        def _(event):
            """Handle enter - select from menu if visible, otherwise submit."""
            if self.command_menu.visible:
                # Select command from menu
                selected = self.command_menu.get_selected()
                if selected:
                    # Replace buffer content with selected command
                    buffer.text = selected + " "
                    buffer.cursor_position = len(buffer.text)
                self.command_menu.hide()
                event.app.invalidate()  # Redraw after hiding menu
            else:
                # Submit the input
                event.app.exit(result=buffer.text)

        @kb.add("escape")
        def _(event):
            """Hide menu on escape."""
            if self.command_menu.visible:
                self.command_menu.hide()
                event.app.invalidate()  # Redraw after hiding menu
            else:
                # Clear buffer if no menu
                buffer.text = ""

        @kb.add("up")
        def _(event):
            """Move up in menu if visible."""
            if self.command_menu.visible:
                self.command_menu.move_up()
                event.app.invalidate()  # Redraw to show updated selection

        @kb.add("down")
        def _(event):
            """Move down in menu if visible."""
            if self.command_menu.visible:
                self.command_menu.move_down()
                event.app.invalidate()  # Redraw to show updated selection

        @kb.add("c-c")
        def _(event):
            event.app.exit(result=None)

        @kb.add("tab")
        def _(event):
            """Handle tab - move down in menu if visible."""
            if self.command_menu.visible:
                self.command_menu.move_down()
                event.app.invalidate()  # Redraw to show updated selection
            else:
                # Normal tab behavior
                b = event.app.current_buffer
                if b.complete_state:
                    b.complete_next()
                else:
                    b.start_completion(select_first=False)

        @kb.add("s-tab")
        def _(event):
            """Handle shift-tab - move up in menu if visible."""
            if self.command_menu.visible:
                self.command_menu.move_up()
                event.app.invalidate()  # Redraw to show updated selection
            else:
                # Normal shift-tab behavior
                b = event.app.current_buffer
                if b.complete_state:
                    b.complete_previous()

        # Create and run application with mouse support for menu
        app = Application(
            layout=layout,
            key_bindings=kb,
            style=final_style,
            full_screen=False,
            mouse_support=True,  # Enable mouse for menu interaction
        )

        # Add handler to show custom command menu (after app creation so we can invalidate)
        def on_text_changed(_):
            """Show custom menu when user types '/'."""
            text = buffer.text
            # Show custom menu for initial "/"
            if text == "/":
                # Collect all commands with descriptions
                commands = []
                for cmd in sorted(self.completer_dict.keys()):
                    desc = self.slash_completer.descriptions.get(cmd, "")
                    commands.append((cmd, desc))
                self.command_menu.show(commands)
                app.invalidate()  # Force redraw
            # Show menu for command arguments if applicable
            elif text.startswith("/") and text.endswith(" "):
                parts = text.split()
                if len(parts) >= 1:
                    cmd = parts[0]
                    # Check if this command has sub-completions
                    if cmd in self.completer_dict and isinstance(self.completer_dict[cmd], dict):
                        # Show submenu with options
                        sub_commands = []
                        for sub_cmd in sorted(self.completer_dict[cmd].keys()):
                            sub_commands.append((sub_cmd, ""))
                        self.command_menu.show(sub_commands)
                        app.invalidate()  # Force redraw
                    else:
                        self.command_menu.hide()
                        app.invalidate()  # Force redraw
            else:
                # Hide menu if not typing "/" or command with space
                if self.command_menu.visible:  # Only invalidate if state changed
                    self.command_menu.hide()
                    app.invalidate()  # Force redraw

        buffer.on_text_changed += on_text_changed

        result = app.run()
        return result or ""


class UI:
    """Centralized UI manager."""

    def __init__(self):
        # Load config for UI preferences
        from agent_cli.config import Config
        self.config = Config()

        # Filter default theme styles
        default_styles = {
            k: v for k, v in PRESET_THEMES["default"].items() if k != "border.pattern"
        }
        self.console = Console(theme=Theme(default_styles))
        self.theme_manager = ThemeManager(self.console)
        self.interactive_session = InteractiveSession(self)

    def print_welcome(self):
        """Print the welcome banner."""
        # Get version from package metadata
        try:
            pkg_version = version("agent-cli")
        except Exception:
            pkg_version = "unknown"

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
                f"[bold blue]{title}[/bold blue]\n[dim]Interactive AI Agent CLI v{pkg_version}[/dim]",
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

    def print_table(self, title: str, columns: list[str], rows: list[list[str]]):
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
