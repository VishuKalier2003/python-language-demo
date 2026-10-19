import hashlib
from dataclasses import dataclass
from typing import Optional

from auth.credentials import UserRecord

MOCK_SECRET = "mock-secret"
MOCK_NOW = 1_700_000_000
TOKEN_TTL = 3600


@dataclass(frozen=True)
class AccessToken:
    value: str
    user_id: str
    roles: tuple
    issued_at: int
    expires_at: int


def _sign(user_id: str, issued_at: int) -> str:
    payload = f"{user_id}:{issued_at}:{MOCK_SECRET}"
    return hashlib.sha256(payload.encode()).hexdigest()[:32]


def issue_token(user: UserRecord, now: int = MOCK_NOW) -> AccessToken:
    return AccessToken(
        value=_sign(user.user_id, now),
        user_id=user.user_id,
        roles=user.roles,
        issued_at=now,
        expires_at=now + TOKEN_TTL,
    )


def validate_token(token: AccessToken, now: int = MOCK_NOW) -> Optional[str]:
    if token.value != _sign(token.user_id, token.issued_at):
        return "invalid_signature"
    if now >= token.expires_at:
        return "expired"
    return None
