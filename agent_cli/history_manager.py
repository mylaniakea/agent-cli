"""Smart message history management with compaction and limits.

Inspired by code-puppy's message history management, adapted for agent-cli.
"""

from typing import Dict, List

from agent_cli.config import Config


def get_message_limit() -> int:
    """Get the maximum number of messages to keep in history.

    Returns:
        Maximum message count from config or default
    """
    config = Config()
    limit = config.get_value("MESSAGE_LIMIT", "50")
    try:
        return int(limit)
    except ValueError:
        return 50


def should_compact_history(history: List[Dict[str, str]]) -> bool:
    """Check if history should be compacted.

    Args:
        history: Current conversation history

    Returns:
        True if history exceeds limit
    """
    limit = get_message_limit()
    return len(history) > limit


def compact_history(
    history: List[Dict[str, str]], strategy: str = "recent"
) -> List[Dict[str, str]]:
    """Compact conversation history using specified strategy.

    Args:
        history: Current conversation history
        strategy: Compaction strategy ("recent", "first", "middle")
            - "recent": Keep most recent messages (default)
            - "first": Keep first and last messages
            - "middle": Keep evenly distributed messages

    Returns:
        Compacted history
    """
    limit = get_message_limit()

    if len(history) <= limit:
        return history

    if strategy == "recent":
        # Keep most recent messages
        return history[-limit:]

    elif strategy == "first":
        # Keep first few and last few
        keep_first = limit // 3
        keep_last = limit - keep_first
        return history[:keep_first] + history[-keep_last:]

    elif strategy == "middle":
        # Keep evenly distributed messages
        step = len(history) // limit
        return [history[i] for i in range(0, len(history), step)][:limit]

    else:
        # Default to recent
        return history[-limit:]


def add_to_history(history: List[Dict[str, str]], role: str, content: str) -> List[Dict[str, str]]:
    """Add a message to history with automatic compaction.

    Args:
        history: Current conversation history
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Updated history (may be compacted)
    """
    history.append({"role": role, "content": content})

    # Auto-compact if needed
    if should_compact_history(history):
        config = Config()
        strategy = config.get_value("HISTORY_COMPACTION_STRATEGY", "recent")
        history = compact_history(history, strategy)

    return history


def format_history_summary(history: List[Dict[str, str]], max_lines: int = 10) -> str:
    """Format history for display with truncation.

    Args:
        history: Conversation history
        max_lines: Maximum number of messages to show

    Returns:
        Formatted history string
    """
    if not history:
        return "No conversation history."

    lines = []
    lines.append(f"Conversation History ({len(history)} messages):\n")

    # Show last N messages
    recent = history[-max_lines:] if len(history) > max_lines else history

    for i, msg in enumerate(recent, 1):
        role = msg["role"].capitalize()
        content = msg["content"]

        # Truncate long messages
        if len(content) > 150:
            content = content[:147] + "..."

        # Show relative position if truncated
        if len(history) > max_lines and i == 1:
            lines.append(f"  ... ({len(history) - max_lines} earlier messages) ...\n")

        lines.append(f"  {i + max(0, len(history) - max_lines)}. {role}: {content}\n")

    return "".join(lines)


def get_token_count(messages: list[dict[str, str]]) -> int:
    """Get estimated token count for message history.

    Args:
        messages: List of message dicts

    Returns:
        Estimated token count
    """
    from agent_cli.token_counter import TokenCounter

    return TokenCounter.estimate_messages_tokens(messages)


def get_context_info(messages: list[dict[str, str]], max_context: int) -> dict[str, any]:
    """Get context window usage information.

    Args:
        messages: List of message dicts
        max_context: Maximum context window size

    Returns:
        Dict with context info (token_count, max_tokens, percentage, status)
    """
    from agent_cli.token_counter import TokenCounter

    token_count = get_token_count(messages)
    percentage, status = TokenCounter.get_context_percentage(token_count, max_context)

    return {
        "token_count": token_count,
        "max_tokens": max_context,
        "percentage": percentage,
        "status": status,
        "message_count": len(messages),
    }
