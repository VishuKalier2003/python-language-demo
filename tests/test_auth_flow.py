import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from auth.credentials import authenticate
from auth.flow import authorize, login_flow, logout_flow
from auth.session import SessionStore
from auth.tokens import MOCK_NOW, TOKEN_TTL


def test_authenticate_mock_user():
    assert authenticate("alice", "alice-pass").user_id == "u-001"
    assert authenticate("alice", "wrong") is None
    assert authenticate("nobody", "x") is None


def test_login_authorize_logout():
    store = SessionStore()
    result = login_flow(store, "alice", "alice-pass")
    assert result.ok and result.user_id == "u-001"
    assert authorize(store, result.session_id, "payments").reason == "authorized"
    assert logout_flow(store, result.session_id).reason == "logged_out"
    assert authorize(store, result.session_id, "payments").reason == "no_session"


def test_bad_credentials():
    assert login_flow(SessionStore(), "bob", "nope").reason == "bad_credentials"


def test_inactive_user_cannot_login():
    assert authenticate("carol", "carol-pass") is None
    assert login_flow(SessionStore(), "carol", "carol-pass").reason == "bad_credentials"


def test_forbidden_role():
    store = SessionStore()
    result = login_flow(store, "bob", "bob-pass")
    assert authorize(store, result.session_id, "admin").reason == "forbidden"


def test_expired_session():
    store = SessionStore()
    result = login_flow(store, "alice", "alice-pass")
    later = MOCK_NOW + TOKEN_TTL
    assert authorize(store, result.session_id, "admin", now=later).reason == "no_session"
