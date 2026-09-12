# R1 authentication baseline evidence

Date: 2026-09-13. Scope: shared-password setup, session cookies, protected root page, auth status/login/logout endpoints, and launcher integration. This is not evidence that the game simulation, persistence, economy, companion, CSRF/origin hardening, rate limiting, or bounded command protocol exists.

## Implemented scope

- `run.sh` sets `ARBORIA_DATA_DIR` to repository `var/` by default and runs `python -m arboria.app.auth_setup` before starting Uvicorn.
- Interactive first run prompts for a shared password with confirmation. Noninteractive setup may use `ARBORIA_SETUP_PASSWORD`; missing credentials fail clearly.
- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes with 600,000 iterations in `var/auth/auth.json`.
- Session tokens are generated with `secrets.token_urlsafe`, stored only as SHA-256 digests in `var/auth/sessions.json`, and sent as HttpOnly SameSite cookies.
- Root frontend access shows a login page until authenticated.
- Public health endpoints remain available and intentionally reveal only coarse implementation status.

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

- `python -m pytest tests/unit` passed with 6 tests and the previously documented FastAPI/Starlette `TestClient` deprecation warning.
- `ruff check .` passed.
- `mypy src tests/unit` passed.
- `npm --prefix web run check` passed.
- `npm --prefix web run test` passed.
- `npm --prefix web run build` passed.
- `./run.sh` configured a temporary password in an isolated data directory, served `/health`, and the stored password file did not contain the plaintext password.

## Limitations

- Authentication protects the current root page and exposes login/status/logout behavior, but no real game state exists yet.
- CSRF/origin validation, login rate limiting, Secure-cookie HTTPS deployment behavior, process lock, command authorization, and owner-device command protocol remain incomplete R1 work.
- `ARBORIA_SETUP_PASSWORD` is an operational convenience for controlled local automation; do not pass real passwords in shell history for normal use.
- The auth/session JSON files are a baseline local implementation, not the final world persistence system.
