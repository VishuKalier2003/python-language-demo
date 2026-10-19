from dataclasses import dataclass
from typing import Optional

from auth.credentials import authenticate
from auth.session import SessionStore
from auth.tokens import MOCK_NOW, issue_token


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    reason: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


def login_flow(store: SessionStore, username: str, password: str, now: int = MOCK_NOW) -> AuthResult:
    user = authenticate(username, password)
    if user is None:
        return AuthResult(ok=False, reason="bad_credentials")
    token = issue_token(user, now)
    session = store.open(token)
    return AuthResult(ok=True, reason="authenticated", session_id=session.session_id, user_id=user.user_id)


def authorize(store: SessionStore, session_id: str, required_role: str, now: int = MOCK_NOW) -> AuthResult:
    session = store.resolve(session_id, now)
    if session is None:
        return AuthResult(ok=False, reason="no_session")
    if required_role not in session.token.roles:
        return AuthResult(ok=False, reason="forbidden", session_id=session_id, user_id=session.token.user_id)
    return AuthResult(ok=True, reason="authorized", session_id=session_id, user_id=session.token.user_id)


def logout_flow(store: SessionStore, session_id: str) -> AuthResult:
    if not store.close(session_id):
        return AuthResult(ok=False, reason="no_session")
    return AuthResult(ok=True, reason="logged_out", session_id=session_id)
