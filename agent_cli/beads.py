"""Beads: Conversation summarization for extended context.

Beads automatically summarizes older parts of conversations to fit within
context windows while preserving recent messages for coherence.
"""

from typing import Optional


class BeadsManager:
    """Manage conversation beads (summaries)."""

    def __init__(
        self,
        enabled: bool = True,
        max_messages: int = 20,
        summary_threshold: int = 15,
    ):
        """Initialize beads manager.

        Args:
            enabled: Whether beads is enabled
            max_messages: Maximum messages to keep in full form
            summary_threshold: Trigger summary when messages exceed this
        """
        self.enabled = enabled
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
        self.summaries: list[str] = []

    def should_summarize(self, messages: list[dict]) -> bool:
        """Check if conversation should be summarized.

        Args:
            messages: Current message list

        Returns:
            True if summarization should occur
        """
        if not self.enabled:
            return False
        return len(messages) > self.summary_threshold

    def create_summary_prompt(self, messages: list[dict]) -> str:
        """Create prompt for summarizing messages.

        Args:
            messages: Messages to summarize

        Returns:
            Summary prompt
        """
        # Format messages for summary
        conversation = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            conversation.append(f"{role.upper()}: {content}")

        conv_text = "\n\n".join(conversation)

        return f"""Please summarize the following conversation concisely, preserving key information, decisions, and context. Focus on:
- Main topics discussed
- Important facts or data mentioned
- Decisions or conclusions reached
- Open questions or action items

CONVERSATION:
{conv_text}

SUMMARY:"""

    def summarize_messages(self, messages: list[dict], summary_agent_fn) -> Optional[str]:
        """Summarize old messages using the agent.

        Args:
            messages: Messages to summarize
            summary_agent_fn: Function to call agent for summary (returns string)

        Returns:
            Summary text or None if failed
        """
        if not messages:
            return None

        try:
            prompt = self.create_summary_prompt(messages)
            summary = summary_agent_fn(prompt)
            return summary
        except Exception as e:
            print(f"Warning: Failed to create summary: {e}")
            return None

    def compact_messages(self, messages: list[dict], summary_agent_fn) -> list[dict]:
        """Compact message history using beads.

        Args:
            messages: Full message history
            summary_agent_fn: Function to get summary from agent

        Returns:
            Compacted message list with summaries
        """
        if not self.should_summarize(messages):
            return messages

        # Split messages into old (to summarize) and recent (keep as-is)
        split_point = len(messages) - self.max_messages
        if split_point <= 0:
            return messages

        old_messages = messages[:split_point]
        recent_messages = messages[split_point:]

        # Create summary of old messages
        summary = self.summarize_messages(old_messages, summary_agent_fn)

        if summary:
            # Store summary
            self.summaries.append(summary)

            # Create summary message
            summary_msg = {
                "role": "system",
                "content": f"[Previous conversation summary: {summary}]",
            }

            # Return summary + recent messages
            return [summary_msg] + recent_messages
        else:
            # Fallback: just return recent messages if summary fails
            return recent_messages

    def get_all_summaries(self) -> list[str]:
        """Get all stored summaries.

        Returns:
            List of summary strings
        """
        return self.summaries.copy()
