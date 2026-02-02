from typing import Dict, List

# In-memory session store
sessions: Dict[str, List[str]] = {}

def add_message(session_id: str, message: str):
    """
    Store messages per session
    """
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append(message)

def get_conversation(session_id: str) -> List[str]:
    """
    Get full conversation for a session
    """
    return sessions.get(session_id, [])
