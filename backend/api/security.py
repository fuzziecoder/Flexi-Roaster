"""Authentication and authorization utilities for the API."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pydantic import BaseModel

from backend.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class TokenRequest(BaseModel):
    """Token request payload for username/password login."""

    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    @property
    def principal(self) -> str:
        """Return the best available login principal from the payload."""
        return (self.username or self.email or "").strip()


class TokenResponse(BaseModel):
    """Token response payload."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    roles: List[str]


@dataclass
class UserPrincipal:
    """Authenticated user context extracted from the JWT token."""

    username: str
    roles: List[str]
    scopes: List[str]
    subject: str


# Demo identity store. Replace with DB/IdP integration in production.
DEMO_USERS: Dict[str, Dict[str, List[str] | str]] = {
    "admin": {"password": "admin123", "roles": ["admin", "operator"], "scopes": ["pipelines:write", "executions:write"]},
    "operator": {"password": "operator123", "roles": ["operator"], "scopes": ["executions:write"]},
    "viewer": {"password": "viewer123", "roles": ["viewer"], "scopes": ["pipelines:read"]},
}


PUBLIC_PATHS: Set[str] = {
    "/",
    "/health",
    f"{settings.API_PREFIX}/auth/token",
    f"{settings.API_PREFIX}/auth/oidc/keycloak/config",
    f"{settings.API_PREFIX}/auth/oidc/keycloak/callback",
}


class SecurityError(HTTPException):
    """Typed exception for auth errors."""


def _create_token(payload: dict) -> str:
    exp_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    exp = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    token_payload = {
        **payload,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(token_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def _candidate_usernames(principal: str) -> List[str]:
    """Generate username candidates from either username or email principals."""
    normalized = principal.strip().lower()
    if not normalized:
        return []

    candidates = [normalized]
    if "@" in normalized:
        candidates.append(normalized.split("@", 1)[0])
    return candidates


def authenticate_user(principal: str, password: str) -> Optional[UserPrincipal]:
    """Validate local user credentials against demo identity store."""
    for username in _candidate_usernames(principal):
        record = DEMO_USERS.get(username)
        if not record or record["password"] != password:
            continue

        return UserPrincipal(
            username=username,
            roles=list(record["roles"]),
            scopes=list(record["scopes"]),
            subject=f"local:{username}",
        )
    return None


def create_access_token(user: UserPrincipal) -> TokenResponse:
    """Issue a JWT for an authenticated principal."""
    ttl_seconds = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    token = _create_token(
        {
            "sub": user.subject,
            "preferred_username": user.username,
            "roles": user.roles,
            "scope": " ".join(user.scopes),
            "provider": "local",
        }
    )
    return TokenResponse(access_token=token, expires_in=ttl_seconds, roles=user.roles)


def _principal_from_payload(payload: dict) -> UserPrincipal:
    roles = payload.get("roles") or payload.get("realm_access", {}).get("roles", [])
    if isinstance(roles, str):
        roles = [roles]
    scope = payload.get("scope", "")
    scopes = scope.split() if isinstance(scope, str) and scope else []
    username = payload.get("preferred_username") or payload.get("email") or payload.get("sub", "unknown")
    return UserPrincipal(
        username=username,
        roles=roles,
        scopes=scopes,
        subject=payload.get("sub", username),
    )


def decode_jwt_token(token: str) -> UserPrincipal:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except InvalidTokenError as exc:
        raise SecurityError(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}")

    return _principal_from_payload(payload)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserPrincipal:
    """Return the authenticated principal for protected endpoints."""
    if request.url.path in PUBLIC_PATHS or request.url.path.startswith((f"{settings.API_PREFIX}/docs", f"{settings.API_PREFIX}/openapi", f"{settings.API_PREFIX}/redoc")):
        return UserPrincipal(username="anonymous", roles=["public"], scopes=[], subject="public")

    if not credentials:
        raise SecurityError(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    return decode_jwt_token(credentials.credentials)


def require_roles(*allowed_roles: str):
    """Dependency factory to enforce RBAC role checks."""

    async def _require_roles(user: UserPrincipal = Depends(get_current_user)) -> UserPrincipal:
        if not allowed_roles:
            return user
        if not set(allowed_roles).intersection(set(user.roles)):
            raise SecurityError(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Allowed: {', '.join(allowed_roles)}",
            )
        return user

    return _require_roles
