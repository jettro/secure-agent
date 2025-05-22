from threading import Lock

from semantic_kernel.contents import ChatHistory

user_sessions = {}
user_sessions_lock = Lock()

def get_user_session(user_id: str):
    with user_sessions_lock:
        if user_id not in user_sessions:
            history = ChatHistory()
            user_sessions[user_id] = (history)
        return user_sessions[user_id]