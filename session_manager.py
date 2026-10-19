"""
session_manager.py

Research Workspace and Session Management for FinSight AI.
Supports Milestone 2 Task 2:
- Named research sessions (e.g., "Tech Sector FY24 YoY Audit", "IT Services Peer Benchmarking")
- Persistent storage of session state, notes, selected companies, and chat conversation history
- Session switching, listing, creation, export/import, and document association
"""

import json
import uuid
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import PROJECT_ROOT

SESSIONS_DIR = PROJECT_ROOT / "sessions"
SESSIONS_INDEX_FILE = SESSIONS_DIR / "sessions_index.json"


def ensure_sessions_dir() -> Path:
    """Ensure sessions storage directory exists."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR


def _load_index() -> Dict[str, Any]:
    ensure_sessions_dir()
    if not SESSIONS_INDEX_FILE.exists():
        initial_index = {
            "active_session_id": None,
            "sessions": {}
        }
        _save_index(initial_index)
        return initial_index

    try:
        with open(SESSIONS_INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"active_session_id": None, "sessions": {}}


def _save_index(index_data: Dict[str, Any]) -> None:
    ensure_sessions_dir()
    with open(SESSIONS_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


def _get_session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def create_session(name: str, description: str = "", pinned_companies: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create a new named research workspace session.
    """
    ensure_sessions_dir()
    session_id = str(uuid.uuid4())[:8]
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    session_data = {
        "session_id": session_id,
        "name": name.strip() or f"Research Session {session_id}",
        "description": description.strip(),
        "created_at": now_str,
        "updated_at": now_str,
        "pinned_companies": pinned_companies or [],
        "notes": "",
        "chat_history": [],
        "pinned_analyses": [],
        "documents": [],
    }

    session_file = _get_session_path(session_id)
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    index = _load_index()
    index["sessions"][session_id] = {
        "session_id": session_id,
        "name": session_data["name"],
        "description": session_data["description"],
        "created_at": session_data["created_at"],
        "updated_at": session_data["updated_at"],
        "pinned_companies": session_data["pinned_companies"],
    }
    index["active_session_id"] = session_id
    _save_index(index)

    return session_data


def list_sessions() -> List[Dict[str, Any]]:
    """Return summary list of all available research sessions."""
    index = _load_index()
    sessions = list(index.get("sessions", {}).values())
    # Sort by updated_at descending
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions


def get_active_session_id() -> Optional[str]:
    """Get the ID of the current active session."""
    index = _load_index()
    active_id = index.get("active_session_id")
    if active_id and active_id in index.get("sessions", {}):
        return active_id
    # Default to first session or None
    sessions = list_sessions()
    if sessions:
        set_active_session(sessions[0]["session_id"])
        return sessions[0]["session_id"]
    return None


def set_active_session(session_id: str) -> bool:
    """Set the currently active research session."""
    index = _load_index()
    if session_id in index.get("sessions", {}):
        index["active_session_id"] = session_id
        _save_index(index)
        return True
    return False


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Load complete session state including chat history, notes, and pinned artifacts."""
    session_file = _get_session_path(session_id)
    if not session_file.exists():
        return None
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[SESSION] Error loading session {session_id}: {exc}")
        return None


def save_session(session_data: Dict[str, Any]) -> bool:
    """Persist session updates to disk."""
    session_id = session_data.get("session_id")
    if not session_id:
        return False

    session_data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    session_file = _get_session_path(session_id)

    try:
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        index = _load_index()
        index["sessions"][session_id] = {
            "session_id": session_id,
            "name": session_data.get("name", "Untitled Session"),
            "description": session_data.get("description", ""),
            "created_at": session_data.get("created_at", ""),
            "updated_at": session_data["updated_at"],
            "pinned_companies": session_data.get("pinned_companies", []),
        }
        _save_index(index)
        return True
    except Exception as exc:
        print(f"[SESSION] Error saving session {session_id}: {exc}")
        return False


def delete_session(session_id: str) -> bool:
    """Delete a research session."""
    index = _load_index()
    if session_id in index.get("sessions", {}):
        del index["sessions"][session_id]
        if index.get("active_session_id") == session_id:
            index["active_session_id"] = None
        _save_index(index)

    session_file = _get_session_path(session_id)
    if session_file.exists():
        try:
            session_file.unlink()
        except OSError:
            pass
    return True


def initialize_default_sessions_if_empty() -> Dict[str, Any]:
    """Ensure at least one default workspace session exists."""
    sessions = list_sessions()
    if not sessions:
        default_session = create_session(
            name="Default Financial Research",
            description="Institutional multi-agent workspace for corporate filings analysis",
            pinned_companies=["Apple", "Microsoft", "Amazon", "Infosys"]
        )
        return default_session
    active_id = get_active_session_id()
    if active_id:
        s = load_session(active_id)
        if s:
            return s
    return load_session(sessions[0]["session_id"]) or sessions[0]
