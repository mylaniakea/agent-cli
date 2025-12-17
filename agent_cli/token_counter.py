"""Token counting utilities for context management."""


class TokenCounter:
    """Estimate token counts for different providers."""

    # Rough estimation: ~4 characters per token for English text
    CHARS_PER_TOKEN = 4

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count from text.

        This is a rough approximation. For accurate counts:
        - OpenAI/Anthropic: Use tiktoken library
        - Google: Use their tokenizer
        - Ollama: Model-specific

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return max(1, len(text) // TokenCounter.CHARS_PER_TOKEN)

    @staticmethod
    def estimate_messages_tokens(messages: list[dict[str, str]]) -> int:
        """Estimate total tokens in message history.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Estimated total tokens
        """
        total = 0
        for msg in messages:
            # Count content tokens
            content = msg.get("content", "")
            total += TokenCounter.estimate_tokens(content)
            # Add overhead for role and structure (~4 tokens per message)
            total += 4
        return total

    @staticmethod
    def get_context_percentage(current_tokens: int, max_tokens: int) -> tuple[float, str]:
        """Calculate context window usage percentage.

        Args:
            current_tokens: Current token count
            max_tokens: Maximum context window size

        Returns:
            Tuple of (percentage, status) where status is 'ok', 'warning', or 'critical'
        """
        if max_tokens <= 0:
            return 0.0, "ok"

        percentage = (current_tokens / max_tokens) * 100

        if percentage >= 90:
            status = "critical"
        elif percentage >= 75:
            status = "warning"
        else:
            status = "ok"

        return percentage, status

    @staticmethod
    def format_token_count(count: int) -> str:
        """Format token count for display.

        Args:
            count: Token count

        Returns:
            Formatted string (e.g., "1.2K", "500")
        """
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        else:
            return str(count)
