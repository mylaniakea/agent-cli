# Bead Pill UI Design

**Status:** Phase 3 Feature Design
**Date:** 2024-12-17

## Visual Design

### Appearance
- **Shape:** Rounded pill/capsule `[text]`
- **Background:** Filled with color based on bead type
- **Text:** White text for contrast
- **Colors:** Match the active theme's color palette

### Positioning
Inline with prompt, between username and arrow:
```
🦙 Matthew [helpful][python][concise] ➜
```

## Color Mapping by Bead Type

### Standard Palette (Theme-Aware)
```python
# Colors pulled from active theme
BASE_BEAD_COLORS = {
    BeadType.BASE: "theme.primary",        # Usually green
    BeadType.PROFESSIONAL: "theme.info",   # Usually blue
    BeadType.DOMAIN: "theme.secondary",    # Usually purple
    BeadType.MODIFIER: "theme.warning",    # Usually yellow
    BeadType.BEHAVIOR: "theme.accent",     # Usually cyan
}
```

### Theme-Specific Examples

**Catppuccin Mocha:**
- Base (green): `#a6e3a1` bg, `#ffffff` text
- Professional (blue): `#89b4fa` bg, `#ffffff` text
- Domain (purple): `#cba6f7` bg, `#ffffff` text
- Modifier (yellow): `#f9e2af` bg, `#1e1e2e` text (dark for readability)
- Behavior (cyan): `#89dceb` bg, `#ffffff` text

**Dracula:**
- Base (green): `#50fa7b` bg, `#282a36` text
- Professional (blue): `#8be9fd` bg, `#282a36` text
- Domain (purple): `#bd93f9` bg, `#282a36` text
- Modifier (yellow): `#f1fa8c` bg, `#282a36` text
- Behavior (cyan): `#8be9fd` bg, `#282a36` text

**Nord:**
- Base (green): `#a3be8c` bg, `#2e3440` text
- Professional (blue): `#81a1c1` bg, `#2e3440` text
- Domain (purple): `#b48ead` bg, `#2e3440` text
- Modifier (yellow): `#ebcb8b` bg, `#2e3440` text
- Behavior (cyan): `#88c0d0` bg, `#2e3440` text

**Tokyo Night:**
- Base (green): `#9ece6a` bg, `#1a1b26` text
- Professional (blue): `#7aa2f7` bg, `#1a1b26` text
- Domain (purple): `#bb9af7` bg, `#1a1b26` text
- Modifier (yellow): `#e0af68` bg, `#1a1b26` text
- Behavior (cyan): `#7dcfff` bg, `#1a1b26` text

## Bead Name Shortening

### Rules
1. Single word: Use first 6-8 chars
2. Hyphenated: Use first word or abbreviation
3. Common patterns:
   - `helpful` → `helpful` (fits)
   - `python-expert` → `python` (common term)
   - `javascript-expert` → `js` (common abbreviation)
   - `data-scientist` → `data` (first word)
   - `devops-expert` → `devops` (fits)
   - `frontend-dev` → `frontend` (descriptive)

### Shortening Map
```python
BEAD_SHORTNAMES = {
    "python-expert": "python",
    "javascript-expert": "js",
    "rust-expert": "rust",
    "data-scientist": "data",
    "devops-expert": "devops",
    "frontend-dev": "frontend",
    "code-reviewer": "reviewer",
    # Keep short names as-is
    "helpful": "helpful",
    "creative": "creative",
    "analytical": "analytic",
    "teaching": "teaching",
    "supportive": "support",
    "technical": "tech",
    "formal": "formal",
    "casual": "casual",
    "executive": "exec",
    "friendly": "friendly",
    "concise": "concise",
    "verbose": "verbose",
    "patient": "patient",
    "direct": "direct",
    "humorous": "humor",
}
```

## Technical Implementation

### Prompt Toolkit Integration

The prompt is rendered with prompt_toolkit's `FormattedText`. We'll inject the pills as styled tokens:

```python
def render_bead_pills(beads: list[PersonalityBead], theme: dict) -> list[tuple]:
    """Render beads as colored pill tokens for prompt_toolkit.

    Returns:
        List of (style, text) tuples for FormattedText
    """
    pills = []

    for bead in beads:
        # Get theme color for this bead type
        bg_color = get_bead_color(bead.type, theme)

        # Determine if we need light or dark text for contrast
        text_color = "#ffffff" if is_dark_color(bg_color) else "#000000"

        # Get shortname
        short_name = BEAD_SHORTNAMES.get(bead.id, bead.id[:8])

        # Create pill style
        style = f"bg:{bg_color} {text_color}"

        # Add pill with surrounding brackets styled
        pills.append((style, f"[{short_name}]"))
        pills.append(("", " "))  # Space between pills

    return pills
```

### Theme Integration

Pull colors from the active theme:

```python
def get_bead_color(bead_type: BeadType, theme: dict) -> str:
    """Get themed color for a bead type."""

    # Map bead type to theme color key
    color_map = {
        BeadType.BASE: "status.good",        # Green-ish
        BeadType.PROFESSIONAL: "status.info", # Blue-ish
        BeadType.DOMAIN: "repr.tag_name",    # Purple-ish
        BeadType.MODIFIER: "status.warning", # Yellow-ish
        BeadType.BEHAVIOR: "repr.url",       # Cyan-ish
    }

    theme_key = color_map.get(bead_type, "status.good")
    color = theme.get(theme_key, "#888888")  # Fallback gray

    return color
```

### Prompt Modification

Modify the prompt rendering in `agent_cli/ui.py`:

```python
# In InteractiveSession.get_input_with_completion()

# Build prompt with provider icon, bead pills, and name
icon = self._get_provider_icon(self.provider)
prompt_name = self.ui.config.prompt_name

# Get active beads from context
active_beads = context.get("active_beads", [])

# Build prompt tokens
prompt_tokens = [
    ("class:prompt", icon),
    ("class:prompt", " "),
    ("class:prompt", prompt_name),
    ("class:prompt", " "),
]

# Add bead pills if any active
if active_beads:
    from agent_cli.personality_beads import render_bead_pills
    pill_tokens = render_bead_pills(active_beads, self.ui.theme_manager.current_theme)
    prompt_tokens.extend(pill_tokens)

# Add arrow
prompt_tokens.append(("class:prompt", "➜ "))

return self.session.prompt(
    prompt_tokens,
    # ... rest of config
)
```

## User Configuration

Allow users to customize display:

```python
# In config.ini or via /config command

[agent-cli]
# Display settings
bead_display = pills          # pills, minimal, text, off
bead_text_color = auto       # auto, white, black, theme
bead_max_display = 5         # Max beads to show, rest as [+2]
bead_shortnames = true       # Use short names vs full names
```

## Interactive Features (Future)

### Phase 3.1 (Current)
- Display pills in prompt
- Theme-aware colors
- Automatic shortening

### Phase 3.2 (Future)
- Click to remove bead (if terminal supports)
- Hover to see full bead details
- `/beads toggle` to hide/show
- Right-click menu for bead actions

## Example Compositions

### Python Developer
```
🦙 Matthew [helpful][python][concise] ➜
```
- Green `[helpful]`, Purple `[python]`, Yellow `[concise]`

### Code Reviewer
```
🦙 Matthew [analytic][tech][direct] ➜
```
- Green `[analytic]`, Blue `[tech]`, Yellow `[direct]`

### Programming Tutor
```
🦙 Matthew [teaching][support][patient][python] ➜
```
- Green `[teaching]`, Green `[support]`, Yellow `[patient]`, Purple `[python]`

### Frontend Developer (Truncated)
```
🦙 Matthew [creative][friendly][frontend][+2] ➜
```
- Shows first 3, indicates 2 more with `[+2]`

## Accessibility Considerations

1. **Color Blindness:** Use distinct shapes/borders, not just color
2. **High Contrast:** Ensure sufficient contrast for readability
3. **Screen Readers:** Pills should be readable as text
4. **Terminal Compatibility:** Fallback to simple brackets if no color support

## Implementation Checklist

- [ ] Create `render_bead_pills()` function
- [ ] Integrate with theme system colors
- [ ] Modify prompt rendering in ui.py
- [ ] Add bead shortname mapping
- [ ] Store active beads in context
- [ ] Test with all 11 themes
- [ ] Handle truncation for many beads
- [ ] Add config options for display
- [ ] Ensure backwards compatibility
- [ ] Test with various terminal types

## Visual Examples by Theme

### Catppuccin Mocha
```
🦙 Matthew [helpful][python][concise] ➜
```
Soft, muted colors with good contrast

### Dracula
```
🦙 Matthew [helpful][python][concise] ➜
```
Vibrant, high-contrast colors

### Nord
```
🦙 Matthew [helpful][python][concise] ➜
```
Cool, subtle nordic colors

### Tokyo Night
```
🦙 Matthew [helpful][python][concise] ➜
```
Deep blues with bright accents

### Gruvbox
```
🦙 Matthew [helpful][python][concise] ➜
```
Warm, retro color palette

## Final Notes

This design provides:
- ✅ Clear visual indication of active personality
- ✅ Theme integration for consistency
- ✅ Compact representation
- ✅ Good contrast and readability
- ✅ Professional appearance
- ✅ Scalable to many beads

The pill design is modern, clean, and informative while not being intrusive.
