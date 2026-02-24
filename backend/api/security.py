"""Security dependencies for OAuth2 / OpenID Connect authentication."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from backend.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    """Authenticated principal context."""

    subject: str
    scopes: List[str]
    audience: Optional[str]
    issuer: str
    token: Dict[str, Any]


@lru_cache(maxsize=1)
def _fetch_openid_config() -> Dict[str, Any]:
    if not settings.OIDC_ISSUER_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OIDC issuer URL is not configured",
        )

    config_url = f"{settings.OIDC_ISSUER_URL.rstrip('/')}/.well-known/openid-configuration"
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(config_url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to load OpenID configuration: {exc}",
        ) from exc


@lru_cache(maxsize=1)
def _fetch_jwks() -> Dict[str, Any]:
    openid_config = _fetch_openid_config()
    jwks_uri = openid_config.get("jwks_uri")
    if not jwks_uri:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenID configuration missing jwks_uri",
        )

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(jwks_uri)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to load JWKS: {exc}",
        ) from exc


def _decode_token(token: str) -> Dict[str, Any]:
    jwks = _fetch_jwks().get("keys", [])
    if not jwks:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWKS does not contain signing keys",
        )

    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")

    selected_key = next((key for key in jwks if key.get("kid") == kid), None)
    if not selected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signing key not recognized",
        )

    algorithm = selected_key.get("alg", "RS256")
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(selected_key)

    options = {
        "verify_aud": bool(settings.OIDC_AUDIENCE),
        "require": ["exp", "iat", "sub"],
    }

    return jwt.decode(
        token,
        key=public_key,
        algorithms=[algorithm],
        audience=settings.OIDC_AUDIENCE or None,
        issuer=settings.OIDC_ISSUER_URL.rstrip("/") if settings.OIDC_ISSUER_URL else None,
        options=options,
    )


def _extract_scopes(claims: Dict[str, Any]) -> List[str]:
    if isinstance(claims.get("scope"), str):
        return [scope for scope in claims["scope"].split(" ") if scope]

    if isinstance(claims.get("scp"), list):
        return [str(scope) for scope in claims["scp"]]

    return []


async def get_current_auth_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthContext:
    """Validate Bearer JWT against configured OpenID Connect provider."""
    if not settings.AUTH_ENABLED:
        return AuthContext(
            subject="anonymous",
            scopes=[],
            audience=settings.OIDC_AUDIENCE,
            issuer=settings.OIDC_ISSUER_URL or "disabled",
            token={},
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = credentials.credentials

    try:
        claims = _decode_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        ) from exc

    exp = claims.get("exp")
    if exp is not None:
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        if expires_at < datetime.now(tz=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

    return AuthContext(
        subject=claims.get("sub", "unknown"),
        scopes=_extract_scopes(claims),
        audience=claims.get("aud") if isinstance(claims.get("aud"), str) else settings.OIDC_AUDIENCE,
        issuer=claims.get("iss", settings.OIDC_ISSUER_URL or ""),
        token=claims,
    )


def require_scopes(required_scopes: List[str]):
    """Build scope-based dependency checks for endpoints."""

    async def _scope_dependency(
        auth: AuthContext = Depends(get_current_auth_context),
    ) -> AuthContext:
        if not required_scopes or not settings.AUTH_ENABLED:
            return auth

        missing_scopes = [scope for scope in required_scopes if scope not in auth.scopes]
        if missing_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scopes: {', '.join(missing_scopes)}",
            )
        return auth

    return _scope_dependency
