"""Personality Beads: Composable AI personality system.

This module implements the core personality bead system, allowing users to
compose AI personalities from reusable trait modules (beads).
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
import yaml


class BeadType(Enum):
    """Types of personality beads."""

    BASE = "base"  # Core personality traits
    PROFESSIONAL = "professional"  # Communication style
    DOMAIN = "domain"  # Expertise areas
    MODIFIER = "modifier"  # Trait adjustments
    BEHAVIOR = "behavior"  # Behavioral patterns


class OverrideMode(Enum):
    """How a bead interacts with existing content."""

    APPEND = "append"  # Add to existing (default)
    PREPEND = "prepend"  # Add before existing
    REPLACE = "replace"  # Replace specific sections
    SUBTRACT = "subtract"  # Remove/negate traits


@dataclass
class PersonalityBead:
    """A single personality trait bead.

    Beads are composable units of personality traits that can be
    combined to create complex AI personalities.

    Attributes:
        id: Unique identifier for the bead
        name: Human-readable name
        type: Category of the bead (base, professional, domain, etc.)
        content: The actual personality trait description
        priority: Composition order (higher = later in chain)
        tags: Searchable tags for discovery
        override_mode: How this bead interacts with others
        description: User-facing description of what this bead does
        author: Creator of the bead
        version: Semantic version of the bead
    """

    id: str
    name: str
    type: BeadType
    content: str
    priority: int = 0
    tags: list[str] = field(default_factory=list)
    override_mode: OverrideMode = OverrideMode.APPEND
    description: str = ""
    author: str = ""
    version: str = "1.0.0"

    def __str__(self) -> str:
        """String representation of the bead."""
        return f"{self.name} ({self.id})"

    def __repr__(self) -> str:
        """Detailed representation of the bead."""
        return f"PersonalityBead(id='{self.id}', name='{self.name}', type={self.type})"


class PersonalityComposer:
    """Compose personality beads into system prompts.

    The composer takes multiple beads and combines them according to their
    priority and override modes to create a final system prompt.
    """

    def __init__(self):
        """Initialize the composer with an empty cache."""
        self.cache: dict[str, str] = {}

    def compose(self, beads: list[PersonalityBead]) -> str:
        """Compose beads into final system prompt.

        Args:
            beads: List of beads to compose

        Returns:
            Composed system prompt string
        """
        if not beads:
            return ""

        # Sort by priority (lower priority applied first)
        sorted_beads = sorted(beads, key=lambda b: b.priority)

        # Apply beads sequentially
        result: list[str] = []

        for bead in sorted_beads:
            content = self._render_bead(bead)

            if bead.override_mode == OverrideMode.APPEND:
                result.append(content)
            elif bead.override_mode == OverrideMode.PREPEND:
                result.insert(0, content)
            elif bead.override_mode == OverrideMode.REPLACE:
                # Replace all previous content
                result = [content]
            # SUBTRACT mode handled separately (advanced feature)

        # Join all bead contents with double newline
        return "\n\n".join(result)

    def _render_bead(self, bead: PersonalityBead) -> str:
        """Render a single bead's content.

        Args:
            bead: The bead to render

        Returns:
            Rendered content string
        """
        # Check cache first
        if bead.id in self.cache:
            return self.cache[bead.id]

        # Render and cache
        rendered = bead.content.strip()
        self.cache[bead.id] = rendered
        return rendered

    def clear_cache(self):
        """Clear the rendering cache."""
        self.cache.clear()


class BeadLibrary:
    """Manage bead library and loading.

    The library loads beads from both system directories (shipped with agent-cli)
    and user directories (in ~/.agent-cli/beads/). User beads can override
    system beads with the same ID.
    """

    def __init__(self):
        """Initialize the bead library."""
        # System beads (shipped with agent-cli)
        self.system_beads_dir = Path(__file__).parent / "beads_library" / "personalities"

        # User beads (in ~/.agent-cli/beads/)
        from agent_cli.config import CONFIG_DIR

        self.user_beads_dir = CONFIG_DIR / "beads" / "personalities"

        # Ensure directories exist
        self.user_beads_dir.mkdir(parents=True, exist_ok=True)

        # Storage for loaded beads
        self._beads: dict[str, PersonalityBead] = {}

        # Load all beads
        self._load_all()

    def _load_all(self):
        """Load all beads from system and user directories."""
        # Load system beads first
        if self.system_beads_dir.exists():
            self._load_from_directory(self.system_beads_dir)

        # Load user beads (can override system beads)
        if self.user_beads_dir.exists():
            self._load_from_directory(self.user_beads_dir)

    def _load_from_directory(self, directory: Path):
        """Load beads from a directory recursively.

        Args:
            directory: Directory to scan for .yaml bead files
        """
        if not directory.exists():
            return

        for bead_file in directory.rglob("*.yaml"):
            try:
                bead = self._load_bead_file(bead_file)
                self._beads[bead.id] = bead
            except Exception as e:
                print(f"Warning: Failed to load bead {bead_file}: {e}")

    def _load_bead_file(self, path: Path) -> PersonalityBead:
        """Load a single bead from YAML file.

        Args:
            path: Path to the YAML bead file

        Returns:
            Loaded PersonalityBead

        Raises:
            ValueError: If the YAML file is invalid
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        # Validate required fields
        required = ["id", "name", "type", "content"]
        for field_name in required:
            if field_name not in data:
                raise ValueError(f"Missing required field '{field_name}' in {path}")

        return PersonalityBead(
            id=data["id"],
            name=data["name"],
            type=BeadType(data["type"]),
            content=data["content"],
            priority=data.get("priority", 0),
            tags=data.get("tags", []),
            override_mode=OverrideMode(data.get("override_mode", "append")),
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
        )

    def get_bead(self, bead_id: str) -> Optional[PersonalityBead]:
        """Get a bead by ID.

        Args:
            bead_id: The unique identifier of the bead

        Returns:
            PersonalityBead if found, None otherwise
        """
        return self._beads.get(bead_id)

    def list_beads(self, bead_type: Optional[BeadType] = None) -> list[PersonalityBead]:
        """List all beads, optionally filtered by type.

        Args:
            bead_type: Optional type to filter by

        Returns:
            List of PersonalityBead objects
        """
        beads = list(self._beads.values())

        if bead_type:
            beads = [b for b in beads if b.type == bead_type]

        # Sort by type then name for consistent ordering
        beads.sort(key=lambda b: (b.type.value, b.name))

        return beads

    def search_beads(self, query: str) -> list[PersonalityBead]:
        """Search beads by name, description, or tags.

        Args:
            query: Search string

        Returns:
            List of matching PersonalityBead objects
        """
        query_lower = query.lower()
        results = []

        for bead in self._beads.values():
            # Search in name, description, and tags
            if (
                query_lower in bead.name.lower()
                or query_lower in bead.description.lower()
                or any(query_lower in tag.lower() for tag in bead.tags)
            ):
                results.append(bead)

        return results

    def reload(self):
        """Reload all beads from disk."""
        self._beads.clear()
        self._load_all()

    def get_categories(self) -> list[str]:
        """Get list of all bead categories.

        Returns:
            List of category names (bead types)
        """
        return [bt.value for bt in BeadType]

    def count(self) -> int:
        """Get total number of loaded beads.

        Returns:
            Count of beads in library
        """
        return len(self._beads)


# ============================================================
# Bead Pill UI Rendering (Phase 3)
# ============================================================

# Shortname mapping for display
BEAD_SHORTNAMES = {
    "python-expert": "python",
    "javascript-expert": "js",
    "rust-expert": "rust",
    "data-scientist": "data",
    "devops-expert": "devops",
    "frontend-dev": "frontend",
    "analytical": "analytic",
    "supportive": "support",
    "technical": "tech",
    "executive": "exec",
    "humorous": "humor",
}

# Color mapping by bead type
BEAD_TYPE_COLORS = {
    BeadType.BASE: "#a6e3a1",        # Green
    BeadType.PROFESSIONAL: "#89b4fa", # Blue
    BeadType.DOMAIN: "#cba6f7",      # Purple
    BeadType.MODIFIER: "#f9e2af",    # Yellow
    BeadType.BEHAVIOR: "#89dceb",    # Cyan
}


def get_bead_shortname(bead: PersonalityBead) -> str:
    """Get shortened display name for a bead.

    Args:
        bead: The bead to get shortname for

    Returns:
        Shortened name suitable for display
    """
    return BEAD_SHORTNAMES.get(bead.id, bead.id[:8])


def is_light_color(hex_color: str) -> bool:
    """Determine if a color is light (needs dark text).

    Args:
        hex_color: Hex color string like "#a6e3a1"

    Returns:
        True if color is light, False if dark
    """
    # Remove # if present
    hex_color = hex_color.lstrip("#")

    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Calculate relative luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255

    return luminance > 0.5


def get_bead_color(bead_type: BeadType, theme: Optional[dict] = None) -> str:
    """Get themed color for a bead type.

    Args:
        bead_type: The type of bead
        theme: Optional theme dict to pull colors from

    Returns:
        Hex color string
    """
    # Use theme colors if available, otherwise defaults
    if theme:
        # Try to get color from theme based on bead type
        # This maps to rich theme color names
        theme_keys = {
            BeadType.BASE: "repr.number",      # Green-ish
            BeadType.PROFESSIONAL: "repr.url", # Blue-ish
            BeadType.DOMAIN: "repr.tag_name",  # Purple-ish
            BeadType.MODIFIER: "repr.attrib_name", # Yellow-ish
            BeadType.BEHAVIOR: "repr.str",     # Cyan-ish
        }

        key = theme_keys.get(bead_type)
        if key and key in theme:
            return theme[key]

    # Fallback to default colors
    return BEAD_TYPE_COLORS.get(bead_type, "#888888")


def render_bead_pills(beads: list[PersonalityBead], theme: Optional[dict] = None, max_display: int = 5) -> list[tuple]:
    """Render beads as colored pill tokens for prompt_toolkit.

    Args:
        beads: List of beads to render
        theme: Optional theme dict for colors
        max_display: Maximum beads to show before truncating

    Returns:
        List of (style, text) tuples for FormattedText
    """
    if not beads:
        return []

    pills = []
    display_beads = beads[:max_display]
    remaining = len(beads) - max_display

    for bead in display_beads:
        # Get color for this bead type
        bg_color = get_bead_color(bead.type, theme)

        # Determine text color for contrast
        text_color = "#000000" if is_light_color(bg_color) else "#ffffff"

        # Get shortname
        short_name = get_bead_shortname(bead)

        # Create pill style with background and text color
        style = f"bg:{bg_color} {text_color}"

        # Add pill with brackets
        pills.append((style, f"[{short_name}]"))
        pills.append(("", " "))  # Space between pills

    # Add truncation indicator if needed
    if remaining > 0:
        pills.append(("", f"[+{remaining}] "))

    return pills
