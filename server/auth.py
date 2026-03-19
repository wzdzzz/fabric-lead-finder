"""JWT 认证模块"""

import time
import hashlib
import hmac
import json
import base64

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import ADMIN_USERNAME, ADMIN_PASSWORD, JWT_SECRET

security = HTTPBearer()

# JWT 有效期 7 天
TOKEN_EXPIRE = 7 * 24 * 3600


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(s: str) -> bytes:
    s += "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s)


def create_token(username: str) -> str:
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64encode(json.dumps({
        "sub": username,
        "exp": int(time.time()) + TOKEN_EXPIRE,
    }).encode())
    signature = _b64encode(
        hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{signature}"


def verify_token(token: str) -> str:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token")

        header, payload, signature = parts
        expected_sig = _b64encode(
            hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError("Invalid signature")

        data = json.loads(_b64decode(payload))
        if data.get("exp", 0) < time.time():
            raise ValueError("Token expired")

        return data["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="无效或过期的登录凭证")


def verify_login(username: str, password: str) -> bool:
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return verify_token(credentials.credentials)
