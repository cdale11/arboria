"""Local shared-password authentication for the single-shop server."""

from __future__ import annotations

import base64
import getpass
import hashlib
import hmac
import json
import os
import secrets
import stat
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

COOKIE_NAME = "arboria_session"
CSRF_COOKIE_NAME = "arboria_csrf"
CSRF_HEADER_NAME = "x-arboria-csrf"
HASH_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60


class AuthConfigurationError(RuntimeError):
    """Raised when authentication cannot be safely initialized."""


@dataclass(frozen=True)
class Session:
    token: str
    csrf_token: str
    expires_at: int


def data_dir() -> Path:
    configured = os.environ.get("ARBORIA_DATA_DIR")
    if configured:
        return Path(configured).resolve()
    repo = os.environ.get("ARBORIA_REPO_ROOT")
    if repo:
        return Path(repo).resolve() / "var"
    return Path.cwd() / "var"


def auth_dir(root: Path | None = None) -> Path:
    return (root or data_dir()) / "auth"


def password_file(root: Path | None = None) -> Path:
    return auth_dir(root) / "auth.json"


def sessions_file(root: Path | None = None) -> Path:
    return auth_dir(root) / "sessions.json"


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data.encode("ascii"))


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(stat.S_IRWXU)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
    tmp.chmod(stat.S_IRUSR | stat.S_IWUSR)
    os.replace(tmp, path)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AuthConfigurationError(f"Invalid JSON object in {path}")
    return payload


def password_is_configured(root: Path | None = None) -> bool:
    return password_file(root).is_file()


def hash_password(password: str, salt: bytes | None = None) -> dict[str, Any]:
    if len(password) < 8:
        raise AuthConfigurationError("Arboria password must be at least 8 characters long.")
    salt = salt or secrets.token_bytes(32)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return {
        "schema_version": 1,
        "algorithm": HASH_ALGORITHM,
        "iterations": PBKDF2_ITERATIONS,
        "salt": _b64(salt),
        "digest": _b64(digest),
    }


def configure_password(password: str, root: Path | None = None) -> None:
    _atomic_write_json(password_file(root), hash_password(password))


def verify_password(password: str, root: Path | None = None) -> bool:
    path = password_file(root)
    if not path.exists():
        return False
    payload = _load_json(path)
    if payload.get("schema_version") != 1 or payload.get("algorithm") != HASH_ALGORITHM:
        raise AuthConfigurationError("Unsupported password hash format.")
    iterations = int(payload["iterations"])
    salt = _unb64(str(payload["salt"]))
    expected = _unb64(str(payload["digest"]))
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)


def _load_sessions(root: Path | None = None) -> dict[str, Any]:
    path = sessions_file(root)
    if not path.exists():
        return {"schema_version": 1, "sessions": {}}
    payload = _load_json(path)
    if payload.get("schema_version") != 1 or not isinstance(payload.get("sessions"), dict):
        raise AuthConfigurationError("Unsupported session store format.")
    return payload


def _token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(root: Path | None = None, now: int | None = None) -> Session:
    now = now or int(time.time())
    token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    expires_at = now + SESSION_TTL_SECONDS
    payload = _load_sessions(root)
    sessions = payload["sessions"]
    sessions[_token_digest(token)] = {
        "expires_at": expires_at,
        "created_at": now,
        "csrf_digest": _token_digest(csrf_token),
    }
    _atomic_write_json(sessions_file(root), payload)
    return Session(token=token, csrf_token=csrf_token, expires_at=expires_at)


def session_is_valid(token: str | None, root: Path | None = None, now: int | None = None) -> bool:
    if not token:
        return False
    now = now or int(time.time())
    payload = _load_sessions(root)
    record = payload["sessions"].get(_token_digest(token))
    if not isinstance(record, dict):
        return False
    expires_at = int(record.get("expires_at", 0))
    return expires_at > now


def destroy_session(token: str | None, root: Path | None = None) -> None:
    if not token:
        return
    payload = _load_sessions(root)
    payload["sessions"].pop(_token_digest(token), None)
    _atomic_write_json(sessions_file(root), payload)


def csrf_is_valid(
    session_token: str | None,
    csrf_token: str | None,
    root: Path | None = None,
    now: int | None = None,
) -> bool:
    if not session_token or not csrf_token:
        return False
    now = now or int(time.time())
    payload = _load_sessions(root)
    record = payload["sessions"].get(_token_digest(session_token))
    if not isinstance(record, dict):
        return False
    if int(record.get("expires_at", 0)) <= now:
        return False
    expected = str(record.get("csrf_digest", ""))
    return hmac.compare_digest(_token_digest(csrf_token), expected)


def ensure_password_configured(root: Path | None = None) -> None:
    if password_is_configured(root):
        return
    env_password = os.environ.get("ARBORIA_SETUP_PASSWORD")
    if env_password:
        configure_password(env_password, root)
        return
    if not os.isatty(0):
        raise AuthConfigurationError(
            "No Arboria password is configured. Run ./run.sh interactively once or set "
            "ARBORIA_SETUP_PASSWORD for noninteractive setup."
        )
    first = getpass.getpass("Create Arboria shared password: ")
    second = getpass.getpass("Confirm Arboria shared password: ")
    if first != second:
        raise AuthConfigurationError("Password confirmation did not match.")
    configure_password(first, root)
