from agent_cli.command_registry import register_command
from agent_cli.commands.constants import (
    CONTEXT_KEY_AGENT,
    CONTEXT_KEY_CONFIG,
    CONTEXT_KEY_HISTORY,
)
from agent_cli.ui import ui


@register_command(
    name="clear",
    description="Clear conversation history",
    usage="/clear",
    aliases=["c"],
    category="session",
    detailed_help="Clear the conversation history for the current session.\n" \
    "This removes all previous messages from context.",
)
def handle_clear(command: str, context: dict) -> bool:
    """Handle /clear command."""
    history = context.get(CONTEXT_KEY_HISTORY, [])
    if history:
        history.clear()
        ui.print_success("Conversation history cleared.")
    else:
        ui.print_info("No conversation history to clear.")
    return True


@register_command(
    name="history",
    description="Show recent conversation history",
    usage="/history [compact]",
    aliases=["hist"],
    category="session",
    detailed_help="Show the recent conversation history.\n" \
    "Displays the last 10 messages in the conversation.\n" \
    "Use '/history compact' to manually compact the history.",
)
def handle_history(command: str, context: dict) -> bool:
    """Handle /history command."""
    from agent_cli.history_manager import compact_history, format_history_summary

    history = context.get(CONTEXT_KEY_HISTORY, [])

    # Check for compact subcommand
    parts = command.split(None, 1)
    if len(parts) > 1 and parts[1].lower() == "compact":
        if history:
            config = context.get(CONTEXT_KEY_CONFIG)
            strategy = (
                config.get_value("HISTORY_COMPACTION_STRATEGY", "recent") if config else "recent"
            )
            compacted = compact_history(history, strategy)
            context[CONTEXT_KEY_HISTORY] = compacted
            ui.print_success(f"History compacted: {len(history)} → {len(compacted)} messages")
        else:
            ui.print_info("No history to compact.")
        return True

    if history:
        summary = format_history_summary(history, max_lines=10)
        ui.print_markdown(f"**Recent Conversation History:**\n\n```\n{summary}\n```")
    else:
        ui.print_info("No conversation history.")
    return True


@register_command(
    name="compress",
    description="Compress conversation history into a summary",
    usage="/compress",
    aliases=[],
    category="session",
    detailed_help="Compress the conversation history into a concise summary.\n" \
    "This reduces token usage while preserving key context.",
)
def handle_compress(command: str, context: dict) -> bool:
    """Handle /compress command."""
    history = context.get(CONTEXT_KEY_HISTORY, [])
    agent = context.get(CONTEXT_KEY_AGENT)

    if not history:
        ui.print_warning("No history to compress.")
        return True

    if not agent:
        ui.print_error("No agent available.")
        return True

    ui.print_info("Compressing conversation history...")
    try:
        with ui.create_spinner("Summarizing context..."):
            summary_prompt = (
                "Summarize our conversation so far into a concise context string "
                "that captures all key information, decisions, and current state. "
                "Do not lose important details."
            )
            summary = agent.chat(summary_prompt, history=history)

        # Replace history with summary
        history.clear()
        history.append({"role": "user", "content": "Previous Context Summary: " + summary})
        history.append({"role": "assistant", "content": "Understood. I have the context."})
        ui.print_success("Context compressed!")
    except Exception as e:
        ui.print_error(f"Error compressing history: {e}")

    return True
