"""Interactive multi-select and checkbox UI components."""

from typing import Optional

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.styles import Style
from rich.console import Console


class MultiSelect:
    """Interactive multi-select with keyboard navigation and spacebar to toggle.

    Shows a checkbox-style interface like:

        Select providers to configure:

        [*] 🤖 OpenAI (GPT-4, o1)
        [ ] 🧠 Anthropic (Claude)
        [*] ✨ Google (Gemini)
        [ ] 🦙 Ollama (Local)

        Use ↑/↓ to navigate, SPACE to select, ENTER when done
    """

    def __init__(
        self,
        options: list[dict[str, str]],
        title: str = "Select options:",
        instruction: str = "Use ↑/↓ to navigate, SPACE to select, ENTER when done",
        console: Optional[Console] = None,
    ):
        """Initialize multi-select.

        Args:
            options: List of dicts with 'key', 'label', and optional 'icon'
            title: Title to display above options
            instruction: Instruction text to display
            console: Rich console for output
        """
        self.options = options
        self.title = title
        self.instruction = instruction
        self.console = console or Console()
        self.selected = set()
        self.current_index = 0

    def _render_options(self) -> list[tuple[str, str]]:
        """Render options as formatted text."""
        lines = []

        # Title
        lines.append(("class:title", f"{self.title}\n\n"))

        # Options
        for idx, option in enumerate(self.options):
            # Checkbox
            is_selected = option['key'] in self.selected
            is_current = idx == self.current_index

            checkbox = "[*]" if is_selected else "[ ]"
            icon = option.get('icon', '')
            label = option['label']

            # Style based on state
            if is_current:
                checkbox_style = "class:checkbox.current"
                text_style = "class:text.current"
            else:
                checkbox_style = "class:checkbox"
                text_style = "class:text"

            # Build line
            line_parts = [
                (checkbox_style, f"{checkbox} "),
            ]
            if icon:
                line_parts.append((text_style, f"{icon} "))
            line_parts.append((text_style, f"{label}\n"))

            lines.extend(line_parts)

        # Instruction
        lines.append(("class:instruction", f"\n{self.instruction}"))

        return lines

    def show(self) -> list[str]:
        """Show the multi-select UI and return selected keys.

        Returns:
            List of selected option keys
        """
        # Create buffer (not used but required for Application)
        buffer = Buffer()

        # Key bindings
        kb = KeyBindings()

        @kb.add("up")
        def _(event):
            """Move selection up."""
            self.current_index = max(0, self.current_index - 1)

        @kb.add("down")
        def _(event):
            """Move selection down."""
            self.current_index = min(len(self.options) - 1, self.current_index + 1)

        @kb.add("space")
        def _(event):
            """Toggle current option."""
            current_key = self.options[self.current_index]['key']
            if current_key in self.selected:
                self.selected.remove(current_key)
            else:
                self.selected.add(current_key)

        @kb.add("enter")
        def _(event):
            """Confirm selection."""
            event.app.exit(result=list(self.selected))

        @kb.add("c-c")
        def _(event):
            """Cancel."""
            event.app.exit(result=[])

        @kb.add("escape")
        def _(event):
            """Cancel."""
            event.app.exit(result=[])

        # Style
        style = Style.from_dict({
            "title": "bold cyan",
            "checkbox": "#888888",
            "checkbox.current": "bold #4a9eff",
            "text": "",
            "text.current": "bold",
            "instruction": "dim",
        })

        # Layout
        def get_content():
            return self._render_options()

        root_container = HSplit([
            Window(
                content=FormattedTextControl(get_content),
                height=len(self.options) + 5,  # Title + options + instruction + spacing
            ),
        ])

        layout = Layout(root_container)

        # Create and run application
        app = Application(
            layout=layout,
            key_bindings=kb,
            style=style,
            full_screen=False,
            mouse_support=False,
        )

        result = app.run()
        return result if result is not None else []


class SingleSelect:
    """Interactive single-select with keyboard navigation.

    Shows a radio-button style interface like:

        Select default provider:

        ( ) 🤖 OpenAI
        (*) 🧠 Anthropic
        ( ) ✨ Google
        ( ) 🦙 Ollama

        Use ↑/↓ to navigate, ENTER to select
    """

    def __init__(
        self,
        options: list[dict[str, str]],
        title: str = "Select an option:",
        instruction: str = "Use ↑/↓ to navigate, ENTER to select",
        default_index: int = 0,
        console: Optional[Console] = None,
    ):
        """Initialize single-select.

        Args:
            options: List of dicts with 'key', 'label', and optional 'icon'
            title: Title to display above options
            instruction: Instruction text to display
            default_index: Index of default selected option
            console: Rich console for output
        """
        self.options = options
        self.title = title
        self.instruction = instruction
        self.console = console or Console()
        self.current_index = default_index

    def _render_options(self) -> list[tuple[str, str]]:
        """Render options as formatted text."""
        lines = []

        # Title
        lines.append(("class:title", f"{self.title}\n\n"))

        # Options
        for idx, option in enumerate(self.options):
            is_current = idx == self.current_index

            radio = "(*)" if is_current else "( )"
            icon = option.get('icon', '')
            label = option['label']

            # Style based on state
            if is_current:
                radio_style = "class:radio.current"
                text_style = "class:text.current"
            else:
                radio_style = "class:radio"
                text_style = "class:text"

            # Build line
            line_parts = [
                (radio_style, f"{radio} "),
            ]
            if icon:
                line_parts.append((text_style, f"{icon} "))
            line_parts.append((text_style, f"{label}\n"))

            lines.extend(line_parts)

        # Instruction
        lines.append(("class:instruction", f"\n{self.instruction}"))

        return lines

    def show(self) -> Optional[str]:
        """Show the single-select UI and return selected key.

        Returns:
            Selected option key, or None if cancelled
        """
        # Create buffer (not used but required for Application)
        buffer = Buffer()

        # Key bindings
        kb = KeyBindings()

        @kb.add("up")
        def _(event):
            """Move selection up."""
            self.current_index = max(0, self.current_index - 1)

        @kb.add("down")
        def _(event):
            """Move selection down."""
            self.current_index = min(len(self.options) - 1, self.current_index + 1)

        @kb.add("enter")
        def _(event):
            """Confirm selection."""
            selected_key = self.options[self.current_index]['key']
            event.app.exit(result=selected_key)

        @kb.add("c-c")
        def _(event):
            """Cancel."""
            event.app.exit(result=None)

        @kb.add("escape")
        def _(event):
            """Cancel."""
            event.app.exit(result=None)

        # Style
        style = Style.from_dict({
            "title": "bold cyan",
            "radio": "#888888",
            "radio.current": "bold #4a9eff",
            "text": "",
            "text.current": "bold",
            "instruction": "dim",
        })

        # Layout
        def get_content():
            return self._render_options()

        root_container = HSplit([
            Window(
                content=FormattedTextControl(get_content),
                height=len(self.options) + 5,  # Title + options + instruction + spacing
            ),
        ])

        layout = Layout(root_container)

        # Create and run application
        app = Application(
            layout=layout,
            key_bindings=kb,
            style=style,
            full_screen=False,
            mouse_support=False,
        )

        result = app.run()
        return result
