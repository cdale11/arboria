"""CLI entry point for first-run password setup."""

from __future__ import annotations

from .auth import AuthConfigurationError, ensure_password_configured


def main() -> int:
    try:
        ensure_password_configured()
    except AuthConfigurationError as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
