from dataclasses import dataclass, field
from typing import Dict, Optional

from auth.tokens import MOCK_NOW, AccessToken, validate_token


@dataclass
class Session:
    session_id: str
    token: AccessToken
    active: bool = True


@dataclass
class SessionStore:
    sessions: Dict[str, Session] = field(default_factory=dict)

    def open(self, token: AccessToken) -> Session:
        session_id = f"s-{token.user_id}-{token.issued_at}"
        session = Session(session_id=session_id, token=token)
        self.sessions[session_id] = session
        return session

    def resolve(self, session_id: str, now: int = MOCK_NOW) -> Optional[Session]:
        session = self.sessions.get(session_id)
        if session is None or not session.active:
            return None
        if validate_token(session.token, now) is not None:
            session.active = False
            return None
        return session

    def close(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session is None or not session.active:
            return False
        session.active = False
        return True
