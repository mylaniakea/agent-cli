# Custom Bead Creation Design

**Status:** Phase 3 Feature
**Date:** 2024-12-17

## Overview

Users need the ability to create custom personality beads for their specific needs. We'll provide two approaches:

1. **DIY**: `/bead create` command for manual bead creation
2. **AI-Assisted**: Specialized "Bead Designer" agent that helps craft effective beads

---

## Approach 1: Manual Bead Creation

### Command: `/bead create`

Interactive wizard that guides users through creating a bead:

```bash
🦙 Matthew ➜ /bead create

Creating new personality bead...

Bead ID (lowercase, hyphenated): my-custom-trait
Bead Name: My Custom Trait
Description: A brief description of what this bead does

Select bead type:
1. base         - Core personality traits
2. professional - Communication styles
3. domain       - Expertise areas
4. modifier     - Response adjustments
5. behavior     - Behavioral patterns

Type (1-5): 4

Priority (0-100, default 0 for base, 10 for professional, 20 for domain, 100 for modifiers): 100

Tags (comma-separated): custom, modifier, experimental

Override mode:
1. append   - Add to existing traits
2. prepend  - Add before existing traits
3. replace  - Replace all previous content

Mode (1-3): 1

Now enter the bead content (the actual personality trait description).
This is what will be composed into the system prompt.
Press Ctrl-D or type "END" on a new line when done.

> You should always consider edge cases and potential issues.
> Think about error handling and graceful failures.
> Anticipate user needs proactively.
> END

Preview:
╭───────────────────────────────────────────────────────╮
│ ID: my-custom-trait                                   │
│ Name: My Custom Trait                                 │
│ Type: modifier                                        │
│ Priority: 100                                         │
│ Override: append                                      │
│                                                       │
│ Content:                                              │
│ You should always consider edge cases and potential   │
│ issues. Think about error handling and graceful      │
│ failures. Anticipate user needs proactively.         │
╰───────────────────────────────────────────────────────╯

Save this bead? (y/N): y

✓ Bead saved to ~/.agent-cli/beads/personalities/modifiers/my-custom-trait.yaml

You can now use it with:
  /agent create myagent llama3 --beads helpful,python-expert,my-custom-trait
```

### YAML Output

```yaml
# ~/.agent-cli/beads/personalities/modifiers/my-custom-trait.yaml

id: my-custom-trait
name: My Custom Trait
type: modifier
priority: 100
override_mode: append
description: A brief description of what this bead does
author: user
version: 1.0.0
tags:
  - custom
  - modifier
  - experimental

content: |
  You should always consider edge cases and potential issues.
  Think about error handling and graceful failures.
  Anticipate user needs proactively.
```

### Validation

Before saving, validate:
- ✅ ID is unique (doesn't conflict with system beads)
- ✅ ID follows naming convention (lowercase, hyphenated)
- ✅ All required fields present
- ✅ Content is not empty
- ✅ Priority is reasonable for bead type

---

## Approach 2: AI-Assisted Bead Designer

### Pre-Built Agent: "Bead Designer"

A specialized agent that helps users create high-quality beads through conversation.

**Agent Configuration:**
```yaml
name: bead-designer
model: claude-3-5-sonnet  # Or user's preferred model
beads:
  - creative        # Think outside the box
  - analytical      # Break down requirements
  - teaching        # Explain concepts clearly
  - technical       # Understand prompt engineering
```

**System Prompt:**
```
You are an expert at designing personality beads for AI agents.

Your expertise:
- Prompt engineering and system prompt design
- Psychology and personality traits
- Clear, concise technical writing
- Understanding trade-offs in AI behavior

When helping users create beads, you:

1. **Understand the Goal**
   - Ask what behavior/trait they want
   - Clarify the use case
   - Identify which bead type fits best

2. **Design the Bead**
   - Write clear, actionable trait descriptions
   - Use concrete examples and guidelines
   - Keep content focused and specific
   - Consider interactions with other beads

3. **Validate & Refine**
   - Check for clarity and specificity
   - Ensure trait is composable
   - Verify it doesn't conflict with common beads
   - Suggest improvements

Best practices for bead content:
- Start with trait declaration ("You are...", "You focus on...")
- Provide specific guidelines or approaches
- Include what to do AND what to avoid
- Keep it focused on ONE trait/behavior
- Write 3-10 concise bullet points
- Use action-oriented language

Bead types guide:
- base: Core personality (helpful, creative, analytical)
- professional: Communication style (formal, casual, technical)
- domain: Expertise area (python-expert, devops-expert)
- modifier: Response adjustments (concise, verbose, patient)
- behavior: Behavioral patterns (proactive, defensive)

Priorities:
- base: 0 (applied first)
- professional: 10
- domain: 20
- modifier: 100 (applied last)
- behavior: 50

Help users create beads that are:
✓ Clear and specific
✓ Composable with others
✓ Focused on one trait
✓ Actionable and concrete
✓ Well-structured
```

### Usage Flow

```bash
# User creates the bead designer agent (pre-configured in Phase 2 library)
🦙 Matthew ➜ /agent create bead-designer claude-3-5-sonnet --beads creative,analytical,teaching,technical

# OR use pre-installed bead-designer agent
🦙 Matthew ➜ /agent use bead-designer

🦙 Matthew [creative][analytic][teaching][tech] ➜ I want to create a bead that makes responses more security-focused

🤖 Great! A security-focused bead sounds useful. Let me help you design it.

First, let's clarify:
1. What type of security? Code security, data privacy, operational security, or general security awareness?
2. Is this for code reviews, general advice, or something else?
3. Should it be cautious/defensive, or balanced with practicality?

🦙 Matthew ➜ It's for code reviews, specifically looking for vulnerabilities and security issues in code

🤖 Perfect! This sounds like a **modifier** bead that adjusts review behavior. Let me draft it:

**Bead Design: security-focused**

```yaml
id: security-focused
name: Security-Focused Reviewer
type: modifier
priority: 100
description: Focus on security vulnerabilities and secure coding practices

content: |
  Focus on security aspects in all code reviews:

  Security checks:
  - Identify potential vulnerabilities (SQL injection, XSS, CSRF)
  - Check authentication and authorization
  - Review input validation and sanitization
  - Examine cryptography usage
  - Assess data exposure risks
  - Look for hardcoded secrets or credentials

  Approach:
  - Explain security implications clearly
  - Suggest secure alternatives
  - Reference OWASP Top 10 when relevant
  - Balance security with practicality
  - Provide remediation guidance
```

What do you think? Should we:
- Add specific vulnerability types?
- Adjust the tone (more/less cautious)?
- Include compliance considerations?

🦙 Matthew ➜ That looks great! Maybe add something about dependencies too?

🤖 Good call! Updated:

```yaml
content: |
  Focus on security aspects in all code reviews:

  Security checks:
  - Identify potential vulnerabilities (SQL injection, XSS, CSRF)
  - Check authentication and authorization
  - Review input validation and sanitization
  - Examine cryptography usage
  - Assess data exposure risks
  - Look for hardcoded secrets or credentials
  - Audit dependencies for known vulnerabilities
  - Check for secure dependency versions

  Approach:
  - Explain security implications clearly
  - Suggest secure alternatives
  - Reference OWASP Top 10 when relevant
  - Balance security with practicality
  - Provide remediation guidance
```

Ready to save this bead? I'll guide you through the /bead create command.

🦙 Matthew ➜ yes!

🤖 Perfect! Run this command:

```
/bead create
```

Then enter these values when prompted:
- ID: security-focused
- Name: Security-Focused Reviewer
- Type: 4 (modifier)
- Priority: 100
- Tags: security, code-review, modifier
- Override: 1 (append)
- Content: [paste the content above]

Or, even easier - I can generate a ready-to-use YAML file. Would you like me to output the complete YAML?

🦙 Matthew ➜ /bead save-last

✓ Bead saved to ~/.agent-cli/beads/personalities/modifiers/security-focused.yaml

You can now use it with:
  /agent create security-reviewer gpt-4 --beads analytical,technical,security-focused
```

---

## Implementation Plan

### Phase 3.3: Custom Bead Creation

**1. Add `/bead create` Command**
```python
@register_command(
    name="bead",
    description="Manage personality beads",
    # ... existing subcommands
)
def handle_bead(command: str, context: dict) -> bool:
    # ... existing code

    elif action == "create":
        create_custom_bead(ui)

    elif action == "save-last":
        # Save last AI-generated bead design
        save_last_bead_design(context)
```

**2. Interactive Bead Creator**
```python
def create_custom_bead(ui):
    """Interactive wizard for creating custom beads."""

    # Collect bead metadata
    bead_id = ui.interactive_session.session.prompt("Bead ID: ")
    name = ui.interactive_session.session.prompt("Bead Name: ")
    description = ui.interactive_session.session.prompt("Description: ")

    # Select type
    ui.print_info("\nSelect bead type:")
    ui.print_info("1. base")
    ui.print_info("2. professional")
    ui.print_info("3. domain")
    ui.print_info("4. modifier")
    ui.print_info("5. behavior")
    type_choice = ui.interactive_session.session.prompt("Type (1-5): ")

    # ... collect other fields

    # Multi-line content input
    ui.print_info("\nEnter bead content (Ctrl-D or 'END' to finish):")
    content_lines = []
    while True:
        line = ui.interactive_session.session.prompt("> ")
        if line.strip().upper() == "END":
            break
        content_lines.append(line)

    content = "\n".join(content_lines)

    # Preview
    show_bead_preview(ui, bead_id, name, ...)

    # Confirm
    confirm = ui.interactive_session.session.prompt("Save this bead? (y/N): ")
    if confirm.lower() == 'y':
        save_custom_bead(bead_id, name, content, ...)
        ui.print_success(f"✓ Bead saved!")
```

**3. Pre-Install Bead Designer Agent**

Create system agent in Phase 2:
```yaml
# agent_cli/beads_library/agents/bead-designer.json
{
  "name": "bead-designer",
  "description": "AI assistant for creating high-quality personality beads",
  "model": "claude-3-5-sonnet",
  "beads": ["creative", "analytical", "teaching", "technical"],
  "system_prompt": "[The comprehensive system prompt from above]"
}
```

Auto-install on first run or via:
```bash
/agent install-default bead-designer
```

---

## Validation & Best Practices

### Bead Content Guidelines

**Good Bead Content:**
✓ Specific and actionable
✓ 3-10 concise points
✓ Clear trait declaration
✓ Examples when helpful
✓ Focus on ONE behavior

**Example (Good):**
```yaml
content: |
  You are extremely patient when explaining concepts.

  Approach:
  - Break down complex ideas into small steps
  - Repeat explanations in different ways
  - Check understanding frequently
  - Never make learners feel inadequate
  - Celebrate progress and effort
```

**Bad Bead Content:**
❌ Too vague
❌ Multiple conflicting traits
❌ No actionable guidance
❌ Overly verbose

**Example (Bad):**
```yaml
content: |
  You should be good at teaching and also creative but also make sure to be
  very detailed and thorough while keeping things brief and to the point and
  also be funny and serious at the same time...
```

### Validation Rules

```python
def validate_bead(bead_data: dict) -> tuple[bool, list[str]]:
    """Validate bead data before saving.

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Required fields
    required = ["id", "name", "type", "content"]
    for field in required:
        if not bead_data.get(field):
            errors.append(f"Missing required field: {field}")

    # ID format
    bead_id = bead_data.get("id", "")
    if not re.match(r'^[a-z][a-z0-9-]*$', bead_id):
        errors.append("ID must be lowercase, start with letter, and use hyphens")

    # Check for conflicts with system beads
    from agent_cli.personality_beads import BeadLibrary
    library = BeadLibrary()
    if library.get_bead(bead_id):
        errors.append(f"Bead ID '{bead_id}' already exists")

    # Content length
    content = bead_data.get("content", "")
    if len(content) < 50:
        errors.append("Content is too short (minimum 50 characters)")
    if len(content) > 2000:
        errors.append("Content is too long (maximum 2000 characters)")

    # Priority range
    priority = bead_data.get("priority", 0)
    if priority < 0 or priority > 100:
        errors.append("Priority must be between 0 and 100")

    return (len(errors) == 0, errors)
```

---

## Benefits

### For Users
✓ Create custom traits for specific needs
✓ Build organization-specific bead libraries
✓ Iterate and improve bead designs
✓ Share custom beads with team

### For Bead Quality
✓ AI assistance ensures well-structured beads
✓ Built-in best practices
✓ Validation prevents common mistakes
✓ Community can share great beads

### For Ecosystem
✓ User-contributed bead marketplace (future)
✓ Domain-specific bead packs
✓ Community standards emerge
✓ Continuous improvement

---

## Future Enhancements

### Phase 4+
- `/bead test` - Test bead in isolation
- `/bead edit` - Edit existing beads
- `/bead fork` - Copy and modify system beads
- `/bead export/import` - Share bead packs
- `/bead marketplace` - Browse community beads
- Bead analytics - Track which beads perform best
- Bead versioning - Track changes over time

---

## Example: Complete Custom Bead Creation Flow

```bash
# Approach 1: Manual DIY
🦙 Matthew ➜ /bead create
[Interactive wizard...]
✓ Bead created: ~/.agent-cli/beads/personalities/modifiers/my-trait.yaml

# Approach 2: AI-Assisted
🦙 Matthew ➜ /agent use bead-designer
🦙 Matthew [creative][analytic][teaching][tech] ➜ Help me create a bead for security reviews
[Conversation with AI...]
🦙 Matthew ➜ /bead save-last
✓ Bead created: ~/.agent-cli/beads/personalities/modifiers/security-focused.yaml

# Use the new bead
🦙 Matthew ➜ /agent create secure-reviewer gpt-4 --beads analytical,technical,security-focused
✓ Agent 'secure-reviewer' created!

🦙 Matthew ➜ /agent use secure-reviewer
🦙 Matthew [analytic][tech][security] ➜ Review this code...
```

This gives users the power to craft exactly the personalities they need! 🎨
