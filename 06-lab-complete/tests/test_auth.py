import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth import create_token, verify_token, authenticate_user

def test_authenticate_user_success():
    user = authenticate_user("student", "demo123")
    assert user["username"] == "student"
    assert user["role"] == "user"

def test_authenticate_user_failure():
    with pytest.raises(HTTPException) as exc:
        authenticate_user("student", "wrong")
    assert exc.value.status_code == 401
    
    with pytest.raises(HTTPException):
        authenticate_user("unknown", "secret")
    
def test_create_and_verify_token():
    token = create_token("user1", "user")
    assert isinstance(token, str)
    
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    payload = verify_token(creds)
    assert payload["username"] == "user1"
    assert payload["role"] == "user"

def test_verify_token_invalid():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
    with pytest.raises(HTTPException) as exc:
        verify_token(creds)
    assert exc.value.status_code == 403
