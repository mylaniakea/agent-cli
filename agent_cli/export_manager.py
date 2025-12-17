"""Export and logging functionality for conversations."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class ExportManager:
    """Manage conversation exports and logging."""

    @staticmethod
    def export_to_markdown(
        messages: list[dict[str, str]],
        filename: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Export conversation to markdown format.

        Args:
            messages: List of message dicts with 'role' and 'content'
            filename: Output filename
            metadata: Optional metadata (provider, model, timestamp, etc.)

        Returns:
            Path to exported file
        """
        output_path = Path(filename).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            # Write header
            f.write("# Agent CLI Conversation Export\n\n")

            # Write metadata if provided
            if metadata:
                f.write("## Metadata\n\n")
                f.write(f"- **Provider**: {metadata.get('provider', 'Unknown')}\n")
                f.write(f"- **Model**: {metadata.get('model', 'Unknown')}\n")
                f.write(
                    f"- **Exported**: {metadata.get('timestamp', datetime.now().isoformat())}\n"
                )
                f.write(f"- **Messages**: {metadata.get('message_count', len(messages))}\n")
                f.write("\n---\n\n")

            # Write messages
            f.write("## Conversation\n\n")
            for msg in messages:
                role = msg.get("role", "unknown").title()
                content = msg.get("content", "")

                f.write(f"### {role}\n\n")
                f.write(f"{content}\n\n")

        return str(output_path)

    @staticmethod
    def export_to_json(
        messages: list[dict[str, str]],
        filename: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """Export conversation to JSON format.

        Args:
            messages: List of message dicts
            filename: Output filename
            metadata: Optional metadata

        Returns:
            Path to exported file
        """
        output_path = Path(filename).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "metadata": metadata or {},
            "messages": messages,
            "exported_at": datetime.now().isoformat(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return str(output_path)

    @staticmethod
    def get_default_export_path(format: str = "md") -> str:
        """Get default export path.

        Args:
            format: File format ('md' or 'json')

        Returns:
            Default export path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        downloads = Path.home() / "Downloads"

        # Fall back to home if Downloads doesn't exist
        if not downloads.exists():
            downloads = Path.home()

        return str(downloads / f"agent-cli-export-{timestamp}.{format}")


class ConversationLogger:
    """Log conversations to disk."""

    def __init__(self, log_dir: Optional[Path] = None, enabled: bool = True):
        """Initialize conversation logger.

        Args:
            log_dir: Directory for logs (default: ~/.agent-cli/logs/)
            enabled: Whether logging is enabled
        """
        self.enabled = enabled
        if log_dir is None:
            log_dir = Path.home() / ".agent-cli" / "logs"
        self.log_dir = Path(log_dir)
        if self.enabled:
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_conversation(
        self, messages: list[dict[str, str]], metadata: Optional[dict] = None
    ) -> Optional[str]:
        """Log a conversation to disk.

        Args:
            messages: List of message dicts
            metadata: Optional metadata

        Returns:
            Path to log file, or None if logging disabled
        """
        if not self.enabled or not messages:
            return None

        # Create date-based subdirectory
        date_dir = self.log_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%H%M%S")
        log_file = date_dir / f"conversation_{timestamp}.json"

        # Save conversation
        log_data = {
            "metadata": metadata or {},
            "messages": messages,
            "logged_at": datetime.now().isoformat(),
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        return str(log_file)

    def list_recent_logs(self, limit: int = 10) -> list[dict]:
        """List recent conversation logs.

        Args:
            limit: Maximum number of logs to return

        Returns:
            List of log info dicts
        """
        if not self.enabled or not self.log_dir.exists():
            return []

        log_files = sorted(
            self.log_dir.rglob("conversation_*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )[:limit]

        logs = []
        for log_file in log_files:
            try:
                with open(log_file, encoding="utf-8") as f:
                    data = json.load(f)
                    logs.append(
                        {
                            "path": str(log_file),
                            "timestamp": data.get("logged_at", ""),
                            "metadata": data.get("metadata", {}),
                            "message_count": len(data.get("messages", [])),
                        }
                    )
            except Exception:
                continue

        return logs
