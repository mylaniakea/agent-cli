# Personality Beads: Composable AI Personality System

**Status:** Research & Design Phase
**Author:** Matthew + Claude
**Date:** 2024-12-17

## Executive Summary

Personality Beads is a novel approach to AI agent personality composition that combines established personality trait research with modular prompt architecture. Initial research shows NO existing implementation of this concept - making this a potential standout feature for agent-cli.

The key innovation: Using the beads system architecture (originally designed for conversation summarization) as the foundation for composable personality traits.

---

## Background Research

### What Currently Exists

#### 1. AI Personality Research (2024-2025)
- **Proven Methods:** Prompt engineering for personality traits (Big Five, MBTI, HEXACO)
- **Research:** Stanford HAI study shows AI can simulate 1052 individual personalities with high accuracy
- **Finding:** Personality affects AI performance - balanced teams outperform skewed teams by 22.9%
- **Application:** Matching AI personality to task type (e.g., high agreeableness for customer service)

**Sources:**
- [AI Agents Simulate Personalities - Stanford HAI](https://hai.stanford.edu/news/ai-agents-simulate-1052-individuals-personalities-with-impressive-accuracy)
- [Evaluating LLM Personality - Scientific Reports](https://www.nature.com/articles/s41598-024-84109-5)

#### 2. Modular/Composable Prompts
- **Architecture:** Reusable, independent prompt modules
- **Techniques:** Prompt chaining, compositional prompting, prompt scaffolding
- **Benefits:** Portability, reusability, independent optimization
- **Patterns:** Sequential, branching, iterative chaining

**Sources:**
- [Prompt Routers and Modular Architecture - PromptLayer](https://blog.promptlayer.com/prompt-routers-and-modular-prompt-architecture-8691d7a57aee/)
- [Modular Prompting - OptizenApp](https://optizenapp.com/ai-prompts/modular-prompting)
- [Prompt Chaining Guide](https://www.promptingguide.ai/techniques/prompt_chaining)

#### 3. Beads System (Steve Yegge)
- **Purpose:** Conversation context compression
- **Method:** Summarize old messages, preserve recent ones
- **Architecture:** Sequential processing, maintains context chain
- **Location:** `agent_cli/beads.py` - BeadsManager class

### What Does NOT Exist

**"Personality Beads"** as a composable personality system:
- ❌ No chaining of personality traits like beads
- ❌ No mix/match personality modules
- ❌ No "beads" metaphor for personality composition
- ❌ No reusable personality trait libraries

**Conclusion:** This concept appears to be NOVEL.

---

## The Key Question: Moniker or Architecture?

### Initial Thought: Just a Moniker
Use "beads" as a metaphor for chained personality traits, but implement as a separate system:
```
personality_beads/
  ├── professional.bead
  ├── creative.bead
  └── python-expert.bead
```

### Deeper Insight: Use the Beads Architecture

**Matthew's Hypothesis:**
> "How [beads] works as an efficient note/progress database for AI, it could be an efficient and robust way to implement personalities/stringed personalities."

**Why This Makes Sense:**

#### Parallel Architectures

| Beads for Conversation | Beads for Personality |
|------------------------|----------------------|
| Compresses history into summaries | Compresses traits into personas |
| Sequential processing (order matters) | Sequential composition (order matters) |
| Recent messages + summary context | Core traits + modifying traits |
| Maintains coherence across time | Maintains coherence across traits |
| Context window management | Personality complexity management |

#### Shared Design Patterns

1. **Composition**: Both build complex outputs from simpler inputs
2. **Sequential Processing**: Order matters in both systems
3. **Context Management**: What to include, what to compress
4. **Incremental Building**: Add/modify without rebuilding from scratch
5. **State Management**: Track what's been included/applied

---

## Proposed Architecture: Beads as Foundation

### Core Concept

Extend the BeadsManager to handle TWO types of beads:
1. **Conversation Beads** (existing) - Context compression
2. **Personality Beads** (new) - Trait composition

### Unified Bead System

```python
class BeadType(Enum):
    CONVERSATION = "conversation"  # Context summaries
    PERSONALITY = "personality"    # Trait definitions
    MODIFIER = "modifier"          # Trait modifiers
    BEHAVIOR = "behavior"          # Behavioral patterns

class Bead:
    """A single bead - can be conversation or personality."""
    id: str
    type: BeadType
    content: str
    priority: int = 0
    tags: list[str] = []
    override_mode: str = "append"  # append, prepend, replace

class BeadsChain:
    """A chain of beads - sequential composition."""
    beads: list[Bead]

    def compose(self) -> str:
        """Compose all beads into final output."""
        # Apply beads in order, respecting override modes
        pass
```

### How It Works

#### Conversation Beads (Existing)
```
[Summary Bead 1] → [Summary Bead 2] → [Recent Messages]
     ↓                    ↓                    ↓
  "Early context"    "Mid context"      "Latest context"
```

#### Personality Beads (New)
```
[Base Trait] → [Professional] → [Domain Expert] → [Modifier]
     ↓              ↓                 ↓               ↓
 "Helpful AI"   "+ formal"      "+ Python"      "- verbose"
```

#### Combined System
The same infrastructure handles BOTH:
- **Storage**: Both use ~/.agent-cli/beads/
- **Processing**: Same composition engine
- **State**: Both maintain chain state
- **API**: Unified bead management

---

## Design Iterations

### Iteration 1: Basic Personality Beads

**Structure:**
```
~/.agent-cli/beads/
├── personalities/          # Personality trait beads
│   ├── base/
│   │   ├── helpful.bead
│   │   ├── creative.bead
│   │   └── analytical.bead
│   ├── professional/
│   │   ├── formal.bead
│   │   ├── casual.bead
│   │   └── technical.bead
│   └── domain/
│       ├── python-expert.bead
│       ├── frontend-dev.bead
│       └── devops.bead
└── conversations/          # Conversation summary beads
    └── [session-id]/
        ├── summary-1.bead
        └── summary-2.bead
```

**Bead Format (YAML):**
```yaml
# professional/formal.bead
type: personality
priority: 10
tags: [professional, communication]
override_mode: append

content: |
  You communicate in a professional, formal manner.
  - Use complete sentences
  - Avoid slang or casual language
  - Maintain respectful tone
  - Provide structured responses
```

**Usage:**
```bash
/agent create senior-dev llama3 --beads base/helpful,professional/formal,domain/python-expert
/agent add-bead senior-dev professional/mentor
/agent show senior-dev  # See composed personality
```

### Iteration 2: Trait Composition with Override Modes

**Override Modes:**
1. **append** - Add to existing traits (default)
2. **prepend** - Add before existing traits (higher priority)
3. **replace** - Replace specific aspects
4. **subtract** - Remove or negate traits

**Example:**
```yaml
# modifiers/concise.bead
type: modifier
priority: 100  # High priority = applied last
override_mode: append

content: |
  IMPORTANT: Keep responses concise and to the point.
  - Aim for brevity without losing clarity
  - Avoid unnecessary elaboration
  - Get straight to the answer
```

When composed:
```
[helpful] + [python-expert] + [concise]
    ↓            ↓               ↓
"I'm here   "I know       "Keep it
 to help"    Python"       brief!"
```

Result: A helpful Python expert who gives concise answers.

### Iteration 3: Context-Aware Beads

**Dynamic Beads:** Beads that read project context

```yaml
# dynamic/project-aware.bead
type: behavior
priority: 50
requires_context: true

content: |
  You are aware of the current project context:
  - Project type: {{project.type}}
  - Languages: {{project.languages}}
  - Frameworks: {{project.frameworks}}

  Tailor your responses to this tech stack.
```

**Template Variables:**
- `{{project.*}}` - From .agent/context/
- `{{git.*}}` - From git status/history
- `{{session.*}}` - From current session
- `{{user.*}}` - From config (e.g., user.name)

### Iteration 4: Bead Inheritance & Composition

**Bead Templates:**
```yaml
# templates/code-reviewer.bead
type: personality
inherits:
  - base/analytical
  - professional/technical
extends:
  - domain/{{language}}-expert

content: |
  You are a code reviewer focused on:
  - Code quality and best practices
  - Security vulnerabilities
  - Performance implications
  - Maintainability
```

**Instance:**
```bash
/agent create py-reviewer llama3 --template code-reviewer --language python
```

Resolves to:
```
base/analytical → professional/technical → domain/python-expert → code-reviewer
```

---

## How Beads Enable Robust Personality Management

### 1. Efficient Storage
- Small, reusable files (like conversation summaries)
- No duplication - compose on demand
- Version control friendly (git-trackable)

### 2. Progressive Refinement
Like conversation beads that build context over time, personality beads refine traits:
```
Session 1: [helpful] + [python-expert]
Session 2: Add [concise] because responses too long
Session 3: Add [patient] for teaching mode
```

### 3. Context Compression
Just as conversation beads compress history, personality beads compress complex personas:
- Instead of: 5000 token system prompt
- Use: 5 beads × 200 tokens each = 1000 tokens + composition logic

### 4. State Management
Beads system already tracks:
- What's been applied
- Order of application
- State between sessions

Apply same to personality:
- Which traits are active
- Order of trait composition
- Persistence across sessions

### 5. Incremental Updates
Conversation beads: Add new summary without rebuilding history
Personality beads: Add new trait without rewriting entire persona

---

## Implementation Strategy

### Phase 1: Extend Beads System
```python
# agent_cli/beads.py - EXTEND existing BeadsManager

class BeadsManager:
    """Unified bead management for conversations AND personalities."""

    def __init__(self):
        self.conversation_beads: list[Bead] = []
        self.personality_beads: list[Bead] = []

    def load_personality_bead(self, path: str) -> Bead:
        """Load a personality bead from file."""
        pass

    def compose_personality(self, bead_ids: list[str]) -> str:
        """Compose personality beads into system prompt."""
        pass

    def compose_context(self, messages: list[dict]) -> list[dict]:
        """Compose conversation beads (existing functionality)."""
        pass
```

### Phase 2: Bead Library
Create default personality beads:
```
agent_cli/beads_library/
├── personalities/
│   ├── base/
│   │   ├── helpful.yaml
│   │   ├── creative.yaml
│   │   ├── analytical.yaml
│   │   └── teaching.yaml
│   ├── professional/
│   │   ├── formal.yaml
│   │   ├── technical.yaml
│   │   └── executive.yaml
│   ├── domain/
│   │   ├── python-expert.yaml
│   │   ├── javascript-expert.yaml
│   │   ├── devops-expert.yaml
│   │   └── data-scientist.yaml
│   └── modifiers/
│       ├── concise.yaml
│       ├── verbose.yaml
│       ├── patient.yaml
│       └── direct.yaml
```

### Phase 3: Agent Integration
```python
# Extend /agent command to support beads

@register_command(name="agent")
def handle_agent(command: str, context: dict) -> bool:
    # NEW: Support bead composition
    if action == "create":
        # /agent create name model --beads helpful,python-expert,concise
        beads = parse_beads_flag(command)
        personality_prompt = compose_beads(beads)

    elif action == "add-bead":
        # /agent add-bead name technical
        pass

    elif action == "remove-bead":
        # /agent remove-bead name verbose
        pass

    elif action == "list-beads":
        # /agent list-beads [category]
        pass
```

### Phase 4: Bead Studio (Future)
Interactive bead creation and testing:
```bash
/bead-studio
  > create new personality bead
  > test bead composition
  > preview system prompt
  > save to library
```

---

## Advantages of Using Beads Architecture

### 1. Unified System
- One architecture for conversation AND personality
- Shared infrastructure, less code duplication
- Consistent mental model for users

### 2. Proven Foundation
- Beads already work for conversation management
- Battle-tested composition logic
- Existing state management

### 3. Natural Extensions
Everything beads do for conversations applies to personality:
- **Summarization** → Trait compression
- **Sequential processing** → Trait composition
- **Context management** → Personality management
- **State tracking** → Active trait tracking

### 4. Future Synergy
Conversation beads + Personality beads together:
```
Session Context = Conversation Beads + Personality Beads + Current Message
                        ↓                    ↓                    ↓
                  "What we discussed"  "Who I am"         "What you want"
```

---

## Open Questions for Iteration

### 1. Composition Order
**Question:** Does order always matter, or can some beads be order-independent?

**Options:**
- **Priority-based**: Beads have priority numbers, applied in order
- **Category-based**: Base → Professional → Domain → Modifiers
- **Dependency graph**: Beads declare dependencies, system resolves

### 2. Conflict Resolution
**Question:** What happens when beads conflict?

**Example:**
```
[formal] says: "Use complete sentences"
[concise] says: "Be brief, even fragments OK"
```

**Options:**
- **Last-wins**: Later beads override earlier
- **Priority-based**: Higher priority wins
- **Explicit override modes**: Beads declare how they interact
- **User prompts**: Ask user to resolve conflicts

### 3. Context Injection
**Question:** How much project/session context should beads access?

**Options:**
- **Static beads**: Pure trait definitions, no context
- **Template beads**: Can reference {{variables}}
- **Dynamic beads**: Execute code to read context
- **Hybrid**: Some beads static, some dynamic

### 4. Bead Format
**Question:** YAML, JSON, or custom format?

**Comparison:**
```yaml
# YAML - Human readable
type: personality
content: |
  You are helpful and professional.
```

```json
// JSON - Machine readable
{
  "type": "personality",
  "content": "You are helpful and professional."
}
```

```python
# Python - Most flexible
class HelpfulBead(Bead):
    def render(self, context):
        return f"You are helpful. Project: {context.project.type}"
```

### 5. Sharing & Distribution
**Question:** How do users share beads?

**Options:**
- **Git repos**: Clone personality libraries
- **Package manager**: `agent-cli install beads-awesome-pack`
- **Marketplace**: Browse/download from web UI
- **Export/import**: `/bead export my-personality.zip`

### 6. Testing & Validation
**Question:** How do users know if their bead composition works?

**Options:**
- **Dry-run mode**: Preview system prompt without activating
- **Test prompts**: Send test messages to validate behavior
- **A/B testing**: Compare responses with/without bead
- **Metrics**: Track response quality, user satisfaction

---

## Next Steps

1. **Validate Architecture**: Review with user, refine design
2. **Prototype Core**: Extend BeadsManager for personality beads
3. **Create Library**: Build 10-15 base personality beads
4. **Test Composition**: Verify bead chaining works as expected
5. **User Testing**: Get feedback on bead concept
6. **Iterate**: Refine based on real usage

---

## Success Metrics

**Technical:**
- ✅ Personality beads compose correctly
- ✅ Order and priority respected
- ✅ No conflicts or errors
- ✅ Performance (composition < 100ms)

**User Experience:**
- ✅ Users can create custom beads
- ✅ Users understand bead composition
- ✅ Users share beads with others
- ✅ Users prefer beads over monolithic prompts

**Differentiation:**
- ✅ Novel feature not found elsewhere
- ✅ Clear value proposition
- ✅ Generates community interest

---

## Conclusion

Personality Beads leverages the existing beads architecture (designed for conversation management) as the foundation for composable personality traits. This is a novel approach that combines established personality research with modular prompt architecture.

**Key Innovation:** Using the same system for BOTH conversation context AND personality context creates a unified, powerful framework for AI agent customization.

This could be a standout feature for agent-cli that doesn't exist in any other AI CLI tool.
