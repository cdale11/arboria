"""Minimal HTTP server for the current Arboria launcher baseline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


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

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "phase": "r1-launcher-baseline",
            "implemented": {
                "server": True,
                "static_frontend": static_dir.exists(),
                "authentication": False,
                "simulation": False,
                "persistence": False,
                "companion": False,
            },
        }

    @app.get("/api/v1/health")
    def api_health() -> dict[str, Any]:
        return health()

    if static_dir.exists():
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        @app.get("/")
        def index() -> FileResponse:
            return FileResponse(static_dir / "index.html")

    else:

        @app.get("/")
        def missing_frontend() -> JSONResponse:
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
