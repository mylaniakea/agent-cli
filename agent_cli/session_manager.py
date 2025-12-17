"""Session management for tracking per-terminal session state.

Inspired by code-puppy's session-based agent selection, adapted for agent-cli.
"""

import json
import os
from pathlib import Path

from agent_cli.config import STATE_DIR


def get_terminal_session_id() -> str:
    """Get a unique identifier for the current terminal session.

    Uses parent process ID (PPID) as the session identifier.
    This works across all platforms and provides session isolation.

    Returns:
        str: Unique session identifier (e.g., "session_12345")
    """
    try:
        ppid = os.getppid()
        return f"session_{ppid}"
    except (OSError, AttributeError):
        # Fallback to current process ID if PPID unavailable
        return f"fallback_{os.getpid()}"


def _get_session_file_path() -> Path:
    """Get the path to the sessions file."""
    return Path(STATE_DIR) / "sessions.json"


def _is_process_alive(pid: int) -> bool:
    """Check if a process with the given PID is still alive, cross-platform.

    Args:
        pid: Process ID to check

    Returns:
        bool: True if process likely exists, False otherwise
    """
    try:
        if os.name == "nt":
            # Windows: use OpenProcess to probe liveness safely
            import ctypes
            from ctypes import wintypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000  # noqa: N806
            kernel32 = ctypes.windll.kernel32
            kernel32.OpenProcess.argtypes = [
                wintypes.DWORD,
                wintypes.BOOL,
                wintypes.DWORD,
            ]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
            if handle:
                kernel32.CloseHandle(handle)
                return True
            # If access denied, process likely exists but we can't query it
            last_error = kernel32.GetLastError()
            return last_error == 5  # ERROR_ACCESS_DENIED
        else:
            # Unix-like: signal 0 does not deliver a signal but checks existence
            os.kill(int(pid), 0)
            return True
    except PermissionError:
        # No permission to signal -> process exists
        return True
    except (OSError, ProcessLookupError):
        # Process does not exist
        return False
    except ValueError:
        # Invalid signal or pid format
        return False


def _load_sessions() -> dict[str, dict]:
    """Load session data from file.

    Returns:
        Dictionary mapping session IDs to session data
    """
    session_file = _get_session_file_path()
    if not session_file.exists():
        return {}

    try:
        with open(session_file) as f:
            sessions = json.load(f)

        # Clean up dead sessions (sessions whose parent process no longer exists)
        cleaned_sessions = {}
        for session_id, session_data in sessions.items():
            if session_id.startswith("session_"):
                try:
                    pid = int(session_id.split("_")[1])
                    if _is_process_alive(pid):
                        cleaned_sessions[session_id] = session_data
                except (ValueError, IndexError):
                    # Invalid session ID format, skip it
                    continue
            elif session_id.startswith("fallback_"):
                # Keep fallback sessions (they're process-based, not terminal-based)
                try:
                    pid = int(session_id.split("_")[1])
                    if _is_process_alive(pid):
                        cleaned_sessions[session_id] = session_data
                except (ValueError, IndexError):
                    continue
            else:
                # Unknown format, keep it
                cleaned_sessions[session_id] = session_data

        # Save cleaned sessions if we removed any
        if len(cleaned_sessions) != len(sessions):
            _save_sessions(cleaned_sessions)

        return cleaned_sessions
    except (OSError, json.JSONDecodeError):
        return {}


def _save_sessions(sessions: dict[str, dict]) -> None:
    """Save session data to file.

    Args:
        sessions: Dictionary mapping session IDs to session data
    """
    session_file = _get_session_file_path()
    session_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    try:
        with open(session_file, "w") as f:
            json.dump(sessions, f, indent=2)
    except OSError:
        # Silently fail if we can't write (e.g., permissions)
        pass


def get_session_state() -> dict:
    """Get the current session's state.

    Returns:
        Dictionary with session state (provider, model, etc.)
    """
    session_id = get_terminal_session_id()
    sessions = _load_sessions()
    return sessions.get(session_id, {})


def save_session_state(state: dict) -> None:
    """Save the current session's state.

    Args:
        state: Dictionary with session state to save
    """
    session_id = get_terminal_session_id()
    sessions = _load_sessions()
    sessions[session_id] = state
    _save_sessions(sessions)


def update_session_state(**kwargs) -> None:
    """Update specific fields in the current session's state.

    Args:
        **kwargs: Key-value pairs to update in session state
    """
    current_state = get_session_state()
    current_state.update(kwargs)
    save_session_state(current_state)


def clear_session_state() -> None:
    """Clear the current session's state."""
    session_id = get_terminal_session_id()
    sessions = _load_sessions()
    if session_id in sessions:
        del sessions[session_id]
        _save_sessions(sessions)


def create_new_session() -> str:
    """Create a new session (clears current session state).

    Returns:
        New session ID
    """
    clear_session_state()
    return get_terminal_session_id()


def list_all_sessions() -> dict[str, dict]:
    """List all active sessions.

    Returns:
        Dictionary mapping session IDs to session data
    """
    return _load_sessions()
