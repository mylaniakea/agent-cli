"""Context file management for persistent project memory."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from agent_cli.git_hooks import GitHooksManager


class ContextManager:
    """Manages project context files for persistent memory."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize context manager.

        Args:
            project_path: Path to project (default: current directory)
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.context_dir = self.project_path / ".agent" / "context"
        self.git_manager = GitHooksManager(self.project_path)

    def ensure_context_dir(self):
        """Ensure context directory exists."""
        self.context_dir.mkdir(parents=True, exist_ok=True)

    def initialize_context(self, project_info: Dict) -> Path:
        """Initialize project context with basic information.

        Args:
            project_info: Dictionary with project information

        Returns:
            Path to created context file
        """
        self.ensure_context_dir()

        context_file = self.context_dir / "project-overview.md"

        content = self._generate_initial_context(project_info)
        context_file.write_text(content)

        return context_file

    def _generate_initial_context(self, project_info: Dict) -> str:
        """Generate initial context content.

        Args:
            project_info: Dictionary with project information

        Returns:
            Markdown content for context file
        """
        lines = []
        lines.append("# Project Overview\n")
        lines.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Basic information
        if project_info.get("name"):
            lines.append(f"**Project:** {project_info['name']}\n")

        if project_info.get("description"):
            lines.append(f"**Description:** {project_info['description']}\n")

        # Language and frameworks
        if project_info.get("primary_language"):
            lines.append(f"**Primary Language:** {project_info['primary_language'].title()}\n")

        if project_info.get("frameworks"):
            frameworks = ", ".join(project_info["frameworks"])
            lines.append(f"**Frameworks:** {frameworks}\n")

        # Project characteristics
        if project_info.get("complexity"):
            lines.append(f"**Complexity:** {project_info['complexity'].title()}\n")

        if project_info.get("total_loc"):
            lines.append(f"**Size:** ~{project_info['total_loc']:,} lines of code\n")

        # Dependencies
        if project_info.get("dependency_files"):
            lines.append("\n## Dependencies\n")
            for dep_file in project_info["dependency_files"]:
                lines.append(f"- {dep_file}")
            lines.append("")

        # Features
        features = []
        if project_info.get("has_tests"):
            features.append("✓ Tests")
        if project_info.get("has_docs"):
            features.append("✓ Documentation")
        if project_info.get("has_ci"):
            features.append("✓ CI/CD")

        if features:
            lines.append("## Features\n")
            for feature in features:
                lines.append(f"- {feature}")
            lines.append("")

        # Git information
        if self.git_manager.is_git_repo():
            lines.append("## Git Information\n")
            branch = self.git_manager.get_branch_name()
            if branch:
                lines.append(f"**Current Branch:** {branch}\n")

            commits = self.git_manager.get_recent_commits(3)
            if commits:
                lines.append("\n**Recent Commits:**")
                for commit in commits:
                    short_hash = commit["hash"][:7]
                    lines.append(f"- `{short_hash}` {commit['message']}")
                lines.append("")

        # Architecture notes (placeholder)
        lines.append("## Architecture\n")
        lines.append("*Add notes about your project architecture here.*\n")

        # Development guidelines (placeholder)
        lines.append("## Development Guidelines\n")
        lines.append("*Add team conventions and guidelines here.*\n")

        # Recent changes (placeholder)
        lines.append("## Recent Changes\n")
        lines.append("*This section will be automatically updated by git hooks.*\n")

        return "\n".join(lines)

    def update_context(self, hook_name: Optional[str] = None):
        """Update context files based on current project state.

        Args:
            hook_name: Name of git hook triggering update (if any)
        """
        self.ensure_context_dir()

        # Update recent changes
        changes_file = self.context_dir / "recent-changes.md"
        content = self._generate_changes_summary(hook_name)
        changes_file.write_text(content)

        # Update git summary
        git_file = self.context_dir / "git-summary.md"
        git_content = self.git_manager.generate_context_summary()
        git_file.write_text(git_content)

    def _generate_changes_summary(self, hook_name: Optional[str]) -> str:
        """Generate summary of recent changes.

        Args:
            hook_name: Name of git hook triggering update

        Returns:
            Markdown content
        """
        lines = []
        lines.append("# Recent Changes\n")
        lines.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        if hook_name:
            lines.append(f"*Triggered by: {hook_name}*\n")
        else:
            lines.append("")

        # Get recent commits
        commits = self.git_manager.get_recent_commits(10)
        if commits:
            lines.append("## Recent Commits\n")
            for commit in commits:
                short_hash = commit["hash"][:7]
                date = commit["date"][:10]
                lines.append(f"### {commit['message']}")
                lines.append(f"`{short_hash}` by {commit['author']} on {date}\n")

        # Get changed files
        changed_files = self.git_manager.get_changed_files()
        if changed_files:
            lines.append("## Uncommitted Changes\n")
            for file in changed_files[:20]:
                lines.append(f"- {file}")
            if len(changed_files) > 20:
                lines.append(f"\n*... and {len(changed_files) - 20} more files*")

        return "\n".join(lines)

    def get_context_files(self) -> List[Path]:
        """Get list of all context files.

        Returns:
            List of context file paths
        """
        if not self.context_dir.exists():
            return []

        return list(self.context_dir.glob("*.md"))

    def get_context_summary(self) -> str:
        """Get a summary of available context.

        Returns:
            Summary string
        """
        files = self.get_context_files()

        if not files:
            return "No context files found"

        lines = []
        lines.append(f"Context Directory: {self.context_dir}")
        lines.append(f"\nAvailable Files: {len(files)}")
        for file in sorted(files):
            size = file.stat().st_size
            lines.append(f"  - {file.name} ({size:,} bytes)")

        return "\n".join(lines)

    def read_all_context(self) -> str:
        """Read and combine all context files.

        Returns:
            Combined context content
        """
        files = self.get_context_files()

        if not files:
            return ""

        contents = []
        for file in sorted(files):
            try:
                content = file.read_text()
                contents.append(f"# {file.name}\n\n{content}")
            except Exception:
                pass

        return "\n\n---\n\n".join(contents)

    def add_note(self, note: str, category: str = "general"):
        """Add a note to the context.

        Args:
            note: Note content
            category: Note category (default: 'general')
        """
        self.ensure_context_dir()

        notes_file = self.context_dir / f"notes-{category}.md"

        # Read existing notes
        existing = ""
        if notes_file.exists():
            existing = notes_file.read_text()

        # Add new note with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_content = f"## {timestamp}\n\n{note}\n\n---\n\n{existing}"

        notes_file.write_text(new_content)

    def create_session_summary(self, session_data: Dict):
        """Create a session summary file.

        Args:
            session_data: Dictionary with session information
        """
        self.ensure_context_dir()

        sessions_dir = self.context_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        session_file = sessions_dir / f"session-{timestamp}.md"

        content = self._generate_session_summary(session_data)
        session_file.write_text(content)

    def _generate_session_summary(self, session_data: Dict) -> str:
        """Generate session summary content.

        Args:
            session_data: Session information

        Returns:
            Markdown content
        """
        lines = []
        lines.append(f"# Session {session_data.get('id', 'Unknown')}\n")
        lines.append(f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        if session_data.get("duration"):
            lines.append(f"**Duration:** {session_data['duration']}\n")

        if session_data.get("provider"):
            lines.append(f"**Provider:** {session_data['provider']}")
            if session_data.get("model"):
                lines.append(f" ({session_data['model']})")
            lines.append("\n")

        if session_data.get("message_count"):
            lines.append(f"**Messages:** {session_data['message_count']}\n")

        if session_data.get("summary"):
            lines.append("## Summary\n")
            lines.append(session_data["summary"])
            lines.append("")

        if session_data.get("topics"):
            lines.append("## Topics Discussed\n")
            for topic in session_data["topics"]:
                lines.append(f"- {topic}")
            lines.append("")

        if session_data.get("files_modified"):
            lines.append("## Files Modified\n")
            for file in session_data["files_modified"]:
                lines.append(f"- {file}")
            lines.append("")

        return "\n".join(lines)


def initialize_project_context(project_path: Optional[Path] = None, project_info: Optional[Dict] = None) -> Path:
    """Convenience function to initialize project context.

    Args:
        project_path: Path to project (default: current directory)
        project_info: Dictionary with project information

    Returns:
        Path to created context file
    """
    if project_info is None:
        project_info = {}

    manager = ContextManager(project_path)
    return manager.initialize_context(project_info)
