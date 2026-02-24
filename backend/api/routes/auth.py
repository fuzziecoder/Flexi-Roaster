"""Authentication routes for local JWT and optional enterprise IAM metadata."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.api.security import TokenRequest, create_access_token, authenticate_user
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", summary="Issue JWT access token")
async def issue_token(payload: TokenRequest):
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return create_access_token(user)


@router.get("/oidc/keycloak/config", summary="Keycloak OIDC metadata")
async def keycloak_config():
    """Expose configured Keycloak values for enterprise IAM integration."""
    return {
        "enabled": settings.KEYCLOAK_ENABLED,
        "issuer": settings.KEYCLOAK_ISSUER,
        "client_id": settings.KEYCLOAK_CLIENT_ID,
        "authorize_url": f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/auth" if settings.KEYCLOAK_ISSUER else None,
        "token_url": f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/token" if settings.KEYCLOAK_ISSUER else None,
    }
