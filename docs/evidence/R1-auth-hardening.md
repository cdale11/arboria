# R1 authentication hardening evidence

Date: 2026-09-13. Scope: CSRF tokens, same-origin rejection for unsafe requests, and failed-login throttling for the current authenticated server baseline. This is not evidence that simulation, persistence, economy, companion behavior, WebSocket command authorization, or public-internet deployment security exists.

## Implemented scope

- Login creates a random session token and a random CSRF token.
- Session tokens and CSRF tokens are stored only as SHA-256 digests in the local JSON session store.
- The session cookie is HttpOnly and SameSite `lax`.
- The CSRF cookie is SameSite `lax` and readable by client code for use in the `X-Arboria-CSRF` header.
- Authenticated logout requires a valid session cookie and matching CSRF header.
- Unsafe HTTP methods reject mismatched `Origin` or `Referer` headers.
- Failed logins are rate-limited in memory after five failures from the same client address within a 15-minute window.

## Commands run

```bash
python -m pytest tests/unit
ruff check .
mypy src tests/unit
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run check
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run test
PATH="$CONDA_PREFIX/bin:$PATH" npm --prefix web run build
ARBORIA_HOST=127.0.0.1 ARBORIA_PORT=8767 ARBORIA_DATA_DIR=<tmp> \
  ARBORIA_SETUP_PASSWORD=<temporary> ./run.sh
python health probe against http://127.0.0.1:8767/health
```

## Results

- `python -m pytest tests/unit` passed with 8 tests and the previously documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- `./run.sh` configured a temporary password in an isolated data directory and served `/health` with authentication marked implemented.

## Limitations

- Rate limiting is in-memory and resets on process restart; it is sufficient only for the local baseline.
- CSRF protection currently covers implemented authenticated unsafe routes. Future command/WebSocket routes need the same security review when added.
- Secure cookies are not used on the current LAN HTTP baseline.
- Session storage remains a baseline JSON implementation, not the final world persistence system.
