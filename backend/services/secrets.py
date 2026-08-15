"""Secret management abstraction for local env/Vault/cloud provider integrations."""
from __future__ import annotations

import os
from typing import Optional

from backend.config import settings


class SecretProvider:
    """Simple secret provider interface."""

    def get_secret(self, key: str) -> Optional[str]:
        raise NotImplementedError


class EnvironmentSecretProvider(SecretProvider):
    """Read secrets from process environment variables."""

    def get_secret(self, key: str) -> Optional[str]:
        return os.getenv(key)


class VaultSecretProvider(SecretProvider):
    """Placeholder Vault provider; can be wired with hvac in production."""

    def get_secret(self, key: str) -> Optional[str]:
        # Fallback mode for this project: namespaced env variables mimic vault path keys.
        return os.getenv(f"VAULT_{key}")


class SecretManager:
    """Select and query the configured secret backend."""

    def __init__(self) -> None:
        backend = settings.SECRET_BACKEND.lower()
        if backend == "vault":
            self.provider = VaultSecretProvider()
        else:
            self.provider = EnvironmentSecretProvider()

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.provider.get_secret(key) or default


secret_manager = SecretManager()
