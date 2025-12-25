import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str 
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


@dataclass
class ChatSession:
    session_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: dict = field(default_factory=dict) 
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        self.messages.append(Message(
            role=role,
            content=content,
            metadata=metadata or {}
        ))
        self.last_activity = datetime.now()
    
    def get_history(self, max_messages: int = 20) -> List[dict]:
        """Get message history for LLM context"""
        recent_messages = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
    
    def update_context(self, key: str, value):
        self.context[key] = value


class SessionMemoryManager:
    
    def __init__(self, timeout_minutes: int = 30):
        self._sessions: Dict[str, ChatSession] = {}
        self._timeout_minutes = timeout_minutes
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = ChatSession(session_id=session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        session = self._sessions.get(session_id)
        if session:
            # Check if session is expired
            if datetime.now() - session.last_activity > timedelta(minutes=self._timeout_minutes):
                self.delete_session(session_id)
                return None
            return session
        return None
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        # Create new session
        new_id = self.create_session()
        return self._sessions[new_id]
    
    def add_message(self, session_id: str, role: str, content: str, metadata: dict = None) -> bool:
        session = self.get_session(session_id)
        if session:
            session.add_message(role, content, metadata)
            return True
        return False
    
    def get_history(self, session_id: str, max_messages: int = 20) -> List[dict]:
        session = self.get_session(session_id)
        if session:
            return session.get_history(max_messages)
        return []
    
    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        current_time = datetime.now()
        expired = [
            sid for sid, session in self._sessions.items()
            if current_time - session.last_activity > timedelta(minutes=self._timeout_minutes)
        ]
        for sid in expired:
            del self._sessions[sid]


# Global session manager instance
session_manager = SessionMemoryManager()
