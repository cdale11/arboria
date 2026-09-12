"""Minimal HTTP server for the current Arboria launcher/auth baseline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .auth import (
    COOKIE_NAME,
    SESSION_TTL_SECONDS,
    create_session,
    destroy_session,
    session_is_valid,
    verify_password,
)


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


def create_app() -> FastAPI:
    app = FastAPI(
        title="Arboria",
        summary="Persistent plant simulation game server",
        version="0.1.0",
    )
    static_dir = _static_dir()

    def is_authenticated(request: Request) -> bool:
        return session_is_valid(request.cookies.get(COOKIE_NAME))

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
            "phase": "r1-auth-baseline",
            "implemented": {
                "server": True,
                "static_frontend": static_dir.exists(),
                "authentication": True,
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

    @app.post("/api/v1/auth/login")
    async def login(request: Request) -> Response:
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
        return response

    @app.post("/api/v1/auth/logout")
    def logout(request: Request) -> Response:
        destroy_session(request.cookies.get(COOKIE_NAME))
        response = JSONResponse({"authenticated": False})
        response.delete_cookie(COOKIE_NAME)
        return response

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
