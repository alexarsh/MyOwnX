"""Password hashing and JWT issuing/verification.

bcrypt runs in a worker thread so it never blocks the event loop.
"""

import time

import bcrypt
import jwt
from anyio import to_thread
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

bearer = HTTPBearer(auto_error=False)


async def hash_password(raw: str) -> str:
    hashed = await to_thread.run_sync(bcrypt.hashpw, raw.encode(), bcrypt.gensalt())
    return hashed.decode()


async def verify_password(raw: str, hashed: str) -> bool:
    return await to_thread.run_sync(bcrypt.checkpw, raw.encode(), hashed.encode())


def issue_token(user_id: int, username: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": int(time.time()) + settings.jwt_ttl_seconds,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def _decode(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(payload["sub"])


def current_user_id(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> int:
    if creds is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return _decode(creds.credentials)


def optional_user_id(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> int | None:
    return _decode(creds.credentials) if creds else None
