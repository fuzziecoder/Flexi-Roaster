"""JWT + RBAC security helpers for advanced orchestration routes."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    """Authenticated identity context extracted from a JWT token."""

    subject: str
    roles: List[str]
    claims: Dict[str, Any]


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _decode_hs256_jwt(token: str, secret: str) -> Dict[str, Any]:
    """Decode and verify a compact JWT token signed with HS256."""
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Malformed JWT token") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    expected_signature = hmac.new(
        secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    supplied_signature = _b64url_decode(signature_segment)

    if not hmac.compare_digest(expected_signature, supplied_signature):
        raise HTTPException(status_code=401, detail="Invalid JWT signature")

    header = json.loads(_b64url_decode(header_segment).decode("utf-8"))
    if header.get("alg") != "HS256":
        raise HTTPException(status_code=401, detail="Unsupported JWT algorithm")

    payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
    exp = payload.get("exp")
    if exp is not None:
        expires_at = datetime.fromtimestamp(float(exp), tz=timezone.utc)
        if datetime.now(tz=timezone.utc) >= expires_at:
            raise HTTPException(status_code=401, detail="JWT token is expired")

    return payload


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AuthContext:
    """Extract JWT identity and roles from Authorization bearer token."""
    if not settings.JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT security is not configured",
        )

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    claims = _decode_hs256_jwt(credentials.credentials, settings.JWT_SECRET)
    subject = claims.get("sub")
    roles = claims.get("roles") or []

    if not subject:
        raise HTTPException(status_code=401, detail="JWT subject is required")
    if not isinstance(roles, list):
        raise HTTPException(status_code=401, detail="JWT roles claim must be a list")

    return AuthContext(subject=subject, roles=roles, claims=claims)


def require_roles(*required_roles: str):
    """Dependency factory enforcing at least one RBAC role."""

    async def _role_guard(auth: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if required_roles and not any(role in auth.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}",
            )
        return auth

    return _role_guard
