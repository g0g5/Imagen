"""Encrypted local provider credential storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from imagen.errors import ConfigError

OPENROUTER_PROVIDER = "openrouter"

_CONFIG_DIR_MODE = 0o700
_SECRET_FILE_MODE = 0o600
_KEYS_FILENAME = "keys"
_ENCRYPTION_KEY_FILENAME = ".encryption_key"


def get_config_dir() -> Path:
    return Path.home() / ".config" / "imagen"


def get_keys_file() -> Path:
    return get_config_dir() / _KEYS_FILENAME


def get_encryption_key_file() -> Path:
    return get_config_dir() / _ENCRYPTION_KEY_FILENAME


def save_api_key(provider: str, api_key: str) -> None:
    credentials = _read_credentials()
    credentials[provider] = {"api_key": api_key}
    _write_credentials(credentials)


def load_api_key(provider: str) -> str | None:
    credentials = _read_credentials()
    provider_credentials = credentials.get(provider)
    if not isinstance(provider_credentials, dict):
        return None

    api_key = provider_credentials.get("api_key")
    if not isinstance(api_key, str):
        return None

    api_key = api_key.strip()
    return api_key or None


def _read_credentials() -> dict[str, Any]:
    keys_file = get_keys_file()
    if not keys_file.exists():
        return {}
    if keys_file.is_dir():
        raise ConfigError(f"Credential store path is a directory: {keys_file}")

    token = keys_file.read_bytes()
    if not token:
        return {}

    try:
        plaintext = _get_fernet().decrypt(token)
        data = json.loads(plaintext.decode("utf-8"))
    except (InvalidToken, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigError(
            "Saved credentials could not be read. Run `imagen auth` to reconfigure."
        ) from exc

    if not isinstance(data, dict):
        raise ConfigError(
            "Saved credentials have an invalid format. Run `imagen auth` to reconfigure."
        )
    return data


def _write_credentials(credentials: dict[str, Any]) -> None:
    _ensure_config_dir()
    plaintext = json.dumps(credentials, sort_keys=True).encode("utf-8")
    token = _get_fernet().encrypt(plaintext)
    keys_file = get_keys_file()
    keys_file.write_bytes(token)
    keys_file.chmod(_SECRET_FILE_MODE)


def _get_fernet() -> Fernet:
    try:
        return Fernet(_get_or_create_encryption_key())
    except ValueError as exc:
        raise ConfigError(
            "Saved credential encryption key could not be read. "
            "Run `imagen auth` to reconfigure."
        ) from exc


def _get_or_create_encryption_key() -> bytes:
    _ensure_config_dir()
    key_file = get_encryption_key_file()
    if key_file.exists():
        if key_file.is_dir():
            raise ConfigError(f"Encryption key path is a directory: {key_file}")
        return key_file.read_bytes().strip()

    key = Fernet.generate_key()
    key_file.write_bytes(key)
    key_file.chmod(_SECRET_FILE_MODE)
    return key


def _ensure_config_dir() -> None:
    config_dir = get_config_dir()
    if config_dir.exists() and not config_dir.is_dir():
        raise ConfigError(f"Config path is not a directory: {config_dir}")
    config_dir.mkdir(parents=True, exist_ok=True)
    config_dir.chmod(_CONFIG_DIR_MODE)
