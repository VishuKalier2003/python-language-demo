from dataclasses import dataclass
from typing import Optional

from auth.login import hash_password, verify_password


@dataclass(frozen=True)
class UserRecord:
    user_id: str
    username: str
    salt: str
    password_hash: str
    roles: tuple
    active: bool = True


MOCK_SALT = "mock-salt"

# Mocked user store; passwords are "<username>-pass". carol is deactivated.
MOCK_USERS = {
    "alice": UserRecord(
        user_id="u-001",
        username="alice",
        salt=MOCK_SALT,
        password_hash=hash_password("alice-pass", MOCK_SALT),
        roles=("admin", "payments"),
    ),
    "bob": UserRecord(
        user_id="u-002",
        username="bob",
        salt=MOCK_SALT,
        password_hash=hash_password("bob-pass", MOCK_SALT),
        roles=("viewer",),
    ),
    "carol": UserRecord(
        user_id="u-003",
        username="carol",
        salt=MOCK_SALT,
        password_hash=hash_password("carol-pass", MOCK_SALT),
        roles=("payments",),
        active=False,
    ),
}


def find_user(username: str) -> Optional[UserRecord]:
    return MOCK_USERS.get(username.strip().lower())


def authenticate(username: str, password: str) -> Optional[UserRecord]:
    user = find_user(username)
    if user is None or not user.active:
        return None
    if not verify_password(password, user.salt, user.password_hash):
        return None
    return user
