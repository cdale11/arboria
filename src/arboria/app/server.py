"""Minimal HTTP server for the current Arboria launcher/auth baseline."""

from __future__ import annotations

import os
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from arboria.sim.clock import ClockValidationError, SimulationClock, clock_status_payload

from .auth import (
    COOKIE_NAME,
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_TTL_SECONDS,
    create_session,
    csrf_is_valid,
    destroy_session,
    session_is_valid,
    verify_password,
)
from .metadata import MetadataStore, WorldMetadata
from .process_lock import DataDirectoryLock

MAX_FAILED_LOGINS = 5
LOGIN_WINDOW_SECONDS = 15 * 60


def _repo_root() -> Path:
    configured = os.environ.get("ARBORIA_REPO_ROOT")
    if configured:
        return Path(configured).resolve()
    return Path(__file__).resolve().parents[3]


def _static_dir() -> Path:
    configured = os.environ.get("ARBORIA_STATIC_DIR")
    if configured:
        return Path(configured).resolve()
    return _repo_root() / "web" / "dist"


def _request_origin(request: Request) -> str:
    return f"{request.url.scheme}://{request.headers.get('host', '')}"


def _origin_is_allowed(request: Request) -> bool:
    expected = _request_origin(request)
    origin = request.headers.get("origin")
    if origin is not None:
        return origin == expected
    referer = request.headers.get("referer")
    return referer is None or referer.startswith(expected + "/")


def create_app() -> FastAPI:
    lock = DataDirectoryLock()
    metadata_store = MetadataStore(lock.root)
    world_metadata: WorldMetadata | None = None
    clock = SimulationClock()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        nonlocal clock, world_metadata
        lock.acquire()
        try:
            world_metadata = metadata_store.initialize_for_process_start()
            clock = SimulationClock.from_state(world_metadata.clock)
            yield
        finally:
            if world_metadata is not None:
                metadata_store.save_clock(clock.state())
            lock.release()

    app = FastAPI(
        title="Arboria",
        summary="Persistent plant simulation game server",
        version="0.1.0",
        lifespan=lifespan,
    )
    static_dir = _static_dir()
    failed_logins: dict[str, list[float]] = {}

    def require_world_metadata() -> WorldMetadata:
        nonlocal world_metadata
        if world_metadata is None:
            world_metadata = metadata_store.initialize_for_process_start()
        return world_metadata

    def save_clock_status() -> dict[str, float | int | bool]:
        require_world_metadata()
        status = clock.status()
        metadata_store.save_clock(clock.state())
        return clock_status_payload(status)

    @app.middleware("http")
    async def reject_cross_origin_mutations(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.method not in {"GET", "HEAD", "OPTIONS"} and not _origin_is_allowed(request):
            return JSONResponse(
                {"detail": "cross-origin mutation rejected"},
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return await call_next(request)

    def is_authenticated(request: Request) -> bool:
        return session_is_valid(request.cookies.get(COOKIE_NAME))

    def client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",", maxsplit=1)[0].strip()
        return request.client.host if request.client else "unknown"

    def login_is_limited(request: Request) -> bool:
        now = time.time()
        key = client_key(request)
        attempts = [
            entry for entry in failed_logins.get(key, []) if now - entry < LOGIN_WINDOW_SECONDS
        ]
        failed_logins[key] = attempts
        return len(attempts) >= MAX_FAILED_LOGINS

    def record_failed_login(request: Request) -> None:
        key = client_key(request)
        failed_logins.setdefault(key, []).append(time.time())

    def csrf_is_authenticated(request: Request) -> bool:
        return csrf_is_valid(
            request.cookies.get(COOKIE_NAME),
            request.headers.get(CSRF_HEADER_NAME),
        )

    def login_page() -> HTMLResponse:
        return HTMLResponse(
            """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Arboria Login</title></head>
  <body>
    <main>
      <h1>Arboria</h1>
      <p>Shared password required. The plant simulation is not implemented yet.</p>
      <form method="post" action="/api/v1/auth/login">
        <label>
          Password
          <input name="password" type="password" autocomplete="current-password">
        </label>
        <button type="submit">Enter</button>
      </form>
    </main>
  </body>
</html>"""
        )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "phase": "r1-world-metadata-baseline",
            "implemented": {
                "server": True,
                "static_frontend": static_dir.exists(),
                "authentication": True,
                "process_lock": True,
                "world_metadata": True,
                "simulation_clock": True,
                "simulation": False,
                "persistence": False,
                "companion": False,
            },
        }

    @app.get("/api/v1/health")
    def api_health() -> dict[str, Any]:
        return health()

    @app.get("/api/v1/auth/status")
    def auth_status(request: Request) -> dict[str, bool]:
        return {"authenticated": is_authenticated(request)}

    @app.get("/api/v1/world")
    def world_status(request: Request) -> Response:
        if not is_authenticated(request):
            return JSONResponse({"detail": "authentication required"}, status_code=401)
        metadata = require_world_metadata()
        return JSONResponse(
            {
                "world_id": metadata.world_id,
                "timeline_id": metadata.timeline_id,
                "schema_version": metadata.schema_version,
            }
        )

    def require_auth_and_csrf(request: Request) -> JSONResponse | None:
        if not is_authenticated(request):
            return JSONResponse({"detail": "authentication required"}, status_code=401)
        if not csrf_is_authenticated(request):
            return JSONResponse(
                {"detail": "invalid csrf token"}, status_code=status.HTTP_403_FORBIDDEN
            )
        return None

    @app.post("/api/v1/auth/login")
    async def login(request: Request) -> Response:
        if login_is_limited(request):
            return JSONResponse(
                {"detail": "too many failed login attempts"},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        content_type = request.headers.get("content-type", "")
        password = ""
        wants_json = content_type.startswith("application/json")
        if wants_json:
            payload = await request.json()
            if isinstance(payload, dict):
                password = str(payload.get("password", ""))
        else:
            form = await request.form()
            password = str(form.get("password", ""))
        if not verify_password(password):
            record_failed_login(request)
            return JSONResponse(
                {"detail": "invalid password"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        session = create_session()
        if wants_json:
            response: Response = JSONResponse(
                {"authenticated": True, "expires_at": session.expires_at}
            )
        else:
            response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            COOKIE_NAME,
            session.token,
            httponly=True,
            samesite="lax",
            max_age=SESSION_TTL_SECONDS,
        )
        response.set_cookie(
            CSRF_COOKIE_NAME,
            session.csrf_token,
            httponly=False,
            samesite="lax",
            max_age=SESSION_TTL_SECONDS,
        )
        return response

    @app.post("/api/v1/auth/logout")
    def logout(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        destroy_session(request.cookies.get(COOKIE_NAME))
        response = JSONResponse({"authenticated": False})
        response.delete_cookie(COOKIE_NAME)
        response.delete_cookie(CSRF_COOKIE_NAME)
        return response

    @app.get("/api/v1/clock")
    def get_clock(request: Request) -> Response:
        if not is_authenticated(request):
            return JSONResponse({"detail": "authentication required"}, status_code=401)
        return JSONResponse(save_clock_status())

    @app.post("/api/v1/clock/pause")
    def pause_clock(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        require_world_metadata()
        payload = clock_status_payload(clock.pause())
        metadata_store.save_clock(clock.state())
        return JSONResponse(payload)

    @app.post("/api/v1/clock/resume")
    def resume_clock(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        require_world_metadata()
        payload = clock_status_payload(clock.resume())
        metadata_store.save_clock(clock.state())
        return JSONResponse(payload)

    @app.post("/api/v1/clock/speed")
    async def set_clock_speed(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        require_world_metadata()
        payload = await request.json()
        if not isinstance(payload, dict):
            return JSONResponse({"detail": "invalid payload"}, status_code=400)
        try:
            speed = float(payload["speed"])
            next_status = clock.set_speed(speed)
        except (KeyError, TypeError, ValueError, ClockValidationError) as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)
        metadata_store.save_clock(clock.state())
        return JSONResponse(clock_status_payload(next_status))

    if static_dir.exists():
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/", response_model=None)
        def index(request: Request) -> Response:
            if not is_authenticated(request):
                return login_page()
            return FileResponse(static_dir / "index.html")

    else:

        @app.get("/", response_model=None)
        def missing_frontend(request: Request) -> Response:
            if not is_authenticated(request):
                return login_page()
            return JSONResponse(
                {
                    "status": "not_ready",
                    "message": (
                        "Browser assets are not built. Run ./run.sh from the repository root."
                    ),
                },
                status_code=503,
            )

    return app


app = create_app()
