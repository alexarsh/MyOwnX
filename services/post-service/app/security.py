"""Local JWT verification — no network call to user-service needed."""

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

bearer = HTTPBearer(auto_error=False)


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
