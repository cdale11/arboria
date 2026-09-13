"""Minimal HTTP server for the current Arboria launcher/auth baseline."""

from __future__ import annotations

import os
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from arboria.sim.clock import (
    ClockState,
    ClockValidationError,
    SimulationClock,
    clock_status_payload,
)
from arboria.sim.world_loop import WorldLoop, WorldLoopState

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
from .checkpoints import CheckpointWriter
from .commands import (
    CommandEnvelope,
    CommandService,
    CommandValidationError,
    Receipt,
    parse_envelope,
)
from .metadata import MetadataStore, WorldMetadata
from .process_lock import DataDirectoryLock

MAX_FAILED_LOGINS = 5
LOGIN_WINDOW_SECONDS = 15 * 60
MAX_STREAM_MESSAGE_BYTES = 4096
MAX_SAVE_NAME_LENGTH = 80


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
    checkpoint_writer = CheckpointWriter(lock.root)
    world_metadata: WorldMetadata | None = None
    clock = SimulationClock()
    world_loop = WorldLoop()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        nonlocal clock, world_loop, world_metadata
        lock.acquire()
        try:
            world_metadata = metadata_store.initialize_for_process_start()
            clock = SimulationClock.from_state(world_metadata.clock)
            world_loop = WorldLoop(world_metadata.loop)
            yield
        finally:
            if world_metadata is not None:
                metadata_store.save_clock(clock.state())
                metadata_store.save_loop(world_loop.state())
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

    def receipt_payload(receipt: Receipt) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "command_id": receipt.command_id,
            "actor": receipt.actor,
            "kind": receipt.kind,
            "status": receipt.status,
            "created_unix_s": receipt.created_unix_s,
        }
        if receipt.reason is not None:
            payload["reason"] = receipt.reason
        if receipt.result is not None:
            payload["result"] = receipt.result
        return payload

    def apply_command(envelope: CommandEnvelope) -> dict[str, Any]:
        if envelope.kind == "clock.pause":
            if envelope.payload:
                raise CommandValidationError("clock.pause payload must be empty")
            payload = clock_status_payload(clock.pause())
            clock_state = clock.state()
            metadata_store.save_clock(clock_state)
            metadata_store.save_loop(world_loop.drain(clock_state))
            return {"clock": payload}
        if envelope.kind == "clock.resume":
            if envelope.payload:
                raise CommandValidationError("clock.resume payload must be empty")
            payload = clock_status_payload(clock.resume())
            clock_state = clock.state()
            metadata_store.save_clock(clock_state)
            metadata_store.save_loop(world_loop.drain(clock_state))
            return {"clock": payload}
        if envelope.kind == "clock.set_speed":
            if set(envelope.payload) != {"speed"}:
                raise CommandValidationError("clock.set_speed requires only speed")
            try:
                speed = float(envelope.payload["speed"])
                status = clock.set_speed(speed)
            except (TypeError, ValueError, ClockValidationError) as exc:
                raise CommandValidationError(str(exc)) from exc
            clock_state = clock.state()
            metadata_store.save_clock(clock_state)
            metadata_store.save_loop(world_loop.drain(clock_state))
            return {"clock": clock_status_payload(status)}
        raise CommandValidationError("unknown command kind")

    def save_clock_status() -> dict[str, float | int | bool]:
        require_world_metadata()
        status = clock.status()
        clock_state = clock.state()
        metadata_store.save_clock(clock_state)
        metadata_store.save_loop(world_loop.drain(clock_state))
        return clock_status_payload(status)

    def loop_payload(loop: WorldLoopState) -> dict[str, int | float]:
        return {
            "sim_tick": loop.sim_tick,
            "world_revision": loop.world_revision,
            "consumed_sim_time_seconds": loop.consumed_sim_time_seconds,
            "base_tick_seconds": 300,
        }

    def create_checkpoint_payload() -> dict[str, Any]:
        nonlocal world_metadata
        metadata = require_world_metadata()
        clock_state = clock.state()
        loop_state = world_loop.drain(clock_state)
        metadata_store.save_clock(clock_state)
        metadata_store.save_loop(loop_state)
        record, manifest = checkpoint_writer.create(
            metadata=metadata,
            clock=clock_state,
            loop=loop_state,
            parent_checkpoint_id=metadata.active_checkpoint_id,
            receipt_count=metadata_store.receipt_count(),
        )
        metadata_store.register_checkpoint(
            checkpoint_id=record.checkpoint_id,
            parent_checkpoint_id=record.parent_checkpoint_id,
            sim_tick=record.sim_tick,
            world_revision=record.world_revision,
            created_unix_s=record.created_unix_s,
            manifest_hash=record.manifest_hash,
            status=record.status,
        )
        world_metadata = metadata_store.load()
        return {
            "checkpoint_id": record.checkpoint_id,
            "parent_checkpoint_id": record.parent_checkpoint_id,
            "sim_tick": record.sim_tick,
            "world_revision": record.world_revision,
            "created_unix_s": record.created_unix_s,
            "manifest_hash": record.manifest_hash,
            "status": record.status,
            "manifest": manifest,
        }

    def snapshot_payloads() -> list[dict[str, Any]]:
        return [
            {
                "name": snapshot.name,
                "checkpoint_id": snapshot.checkpoint_id,
                "created_unix_s": snapshot.created_unix_s,
                "protected": snapshot.protected,
            }
            for snapshot in metadata_store.list_snapshots()
        ]

    def validate_save_name(value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError("save name must be a string")
        name = value.strip()
        if not name or len(name) > MAX_SAVE_NAME_LENGTH or "/" in name or "\\" in name:
            raise ValueError("save name must be 1-80 characters without path separators")
        return name

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

    def websocket_is_authenticated(websocket: WebSocket) -> bool:
        return session_is_valid(websocket.cookies.get(COOKIE_NAME))

    def websocket_origin_is_allowed(websocket: WebSocket) -> bool:
        host = websocket.headers.get("host", "")
        origin = websocket.headers.get("origin")
        if origin is None:
            return True
        return origin in {f"http://{host}", f"https://{host}"}

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
                "stream_protocol": True,
                "checkpoint_layout": True,
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
        loop = world_loop.drain(clock.state())
        metadata_store.save_loop(loop)
        return JSONResponse(
            {
                "world_id": metadata.world_id,
                "timeline_id": metadata.timeline_id,
                "schema_version": metadata.schema_version,
                "request_epoch": metadata.request_epoch,
                "active_checkpoint_id": metadata.active_checkpoint_id,
                **loop_payload(loop),
            }
        )

    @app.post("/api/v1/saves/checkpoint")
    def create_checkpoint(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        return JSONResponse(create_checkpoint_payload())

    @app.get("/api/v1/saves")
    def list_saves(request: Request) -> Response:
        if not is_authenticated(request):
            return JSONResponse({"detail": "authentication required"}, status_code=401)
        return JSONResponse({"snapshots": snapshot_payloads()})

    @app.post("/api/v1/saves/named")
    async def create_named_save(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        payload = await request.json()
        if not isinstance(payload, dict):
            return JSONResponse({"detail": "invalid payload"}, status_code=400)
        try:
            name = validate_save_name(payload.get("name"))
        except ValueError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)
        checkpoint = create_checkpoint_payload()
        metadata_store.name_snapshot(
            name=name,
            checkpoint_id=str(checkpoint["checkpoint_id"]),
            created_unix_s=int(checkpoint["created_unix_s"]),
            protected=True,
        )
        snapshot = {
            "name": name,
            "checkpoint_id": checkpoint["checkpoint_id"],
            "created_unix_s": checkpoint["created_unix_s"],
            "protected": True,
        }
        return JSONResponse({"snapshot": snapshot, "checkpoint": checkpoint})

    @app.post("/api/v1/saves/restore")
    async def restore_save(request: Request) -> Response:
        nonlocal clock, world_loop, world_metadata
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        payload = await request.json()
        if not isinstance(payload, dict):
            return JSONResponse({"detail": "invalid payload"}, status_code=400)
        checkpoint_id = payload.get("checkpoint_id")
        name = payload.get("name")
        if isinstance(name, str):
            snapshot = metadata_store.snapshot_by_name(name)
            if snapshot is None:
                return JSONResponse({"detail": "unknown save name"}, status_code=404)
            checkpoint_id = snapshot.checkpoint_id
        if not isinstance(checkpoint_id, str):
            return JSONResponse({"detail": "checkpoint_id or name is required"}, status_code=400)
        try:
            manifest, state = checkpoint_writer.load(checkpoint_id)
            clock_state = state["clock"]
            loop_state = state["loop"]
            restored_clock = SimulationClock.from_state(
                ClockState(
                    sim_time_seconds=float(clock_state["sim_time_seconds"]),
                    speed=float(clock_state["speed"]),
                    paused=bool(clock_state["paused"]),
                )
            )
            restored_loop_state = WorldLoopState(
                sim_tick=int(loop_state["sim_tick"]),
                world_revision=int(loop_state["world_revision"]),
                consumed_sim_time_seconds=float(loop_state["consumed_sim_time_seconds"]),
            )
        except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)
        clock_state = restored_clock.state()
        world_metadata = metadata_store.restore_checkpoint(
            checkpoint_id=checkpoint_id,
            clock=clock_state,
            loop=restored_loop_state,
        )
        clock = restored_clock
        world_loop = WorldLoop(restored_loop_state)
        return JSONResponse(
            {
                "restored": True,
                "checkpoint_id": checkpoint_id,
                "manifest": manifest,
                "world": {
                    "world_id": world_metadata.world_id,
                    "timeline_id": world_metadata.timeline_id,
                    "request_epoch": world_metadata.request_epoch,
                    "active_checkpoint_id": world_metadata.active_checkpoint_id,
                    **loop_payload(world_metadata.loop),
                },
                "clock": clock_status_payload(clock.status()),
            }
        )

    @app.post("/api/v1/commands")
    async def submit_command(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        try:
            envelope = parse_envelope(await request.json())
        except CommandValidationError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=400)
        metadata = require_world_metadata()
        service = CommandService(
            world_id=metadata.world_id,
            timeline_id=metadata.timeline_id,
            request_epoch=metadata.request_epoch,
            save_receipt=metadata_store.save_receipt,
            find_receipt=metadata_store.find_receipt,
        )
        receipt = service.submit(envelope, apply_command)
        return JSONResponse(receipt_payload(receipt))

    @app.websocket("/api/v1/stream")
    async def stream(websocket: WebSocket) -> None:
        if not websocket_is_authenticated(websocket) or not websocket_origin_is_allowed(websocket):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await websocket.accept()
        metadata = require_world_metadata()
        loop = world_loop.drain(clock.state())
        metadata_store.save_loop(loop)
        await websocket.send_json(
            {
                "schema_version": 1,
                "world_id": metadata.world_id,
                "timeline_id": metadata.timeline_id,
                "revision": loop.world_revision,
                "base_revision": loop.world_revision,
                "kind": "snapshot",
                "payload": {
                    "request_epoch": metadata.request_epoch,
                    "clock": save_clock_status(),
                    "loop": loop_payload(world_loop.state()),
                },
            }
        )
        try:
            while True:
                message = await websocket.receive_text()
                if len(message.encode("utf-8")) > MAX_STREAM_MESSAGE_BYTES:
                    await websocket.close(code=status.WS_1009_MESSAGE_TOO_BIG)
                    return
                if message == '{"kind":"ping"}':
                    loop = world_loop.drain(clock.state())
                    metadata_store.save_loop(loop)
                    await websocket.send_json(
                        {
                            "schema_version": 1,
                            "world_id": metadata.world_id,
                            "timeline_id": metadata.timeline_id,
                            "revision": loop.world_revision,
                            "base_revision": loop.world_revision,
                            "kind": "pong",
                            "payload": {},
                        }
                    )
                else:
                    await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                    return
        except WebSocketDisconnect:
            return

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
        clock_state = clock.state()
        metadata_store.save_clock(clock_state)
        metadata_store.save_loop(world_loop.drain(clock_state))
        return JSONResponse(payload)

    @app.post("/api/v1/clock/resume")
    def resume_clock(request: Request) -> Response:
        rejection = require_auth_and_csrf(request)
        if rejection is not None:
            return rejection
        require_world_metadata()
        payload = clock_status_payload(clock.resume())
        clock_state = clock.state()
        metadata_store.save_clock(clock_state)
        metadata_store.save_loop(world_loop.drain(clock_state))
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
        clock_state = clock.state()
        metadata_store.save_clock(clock_state)
        metadata_store.save_loop(world_loop.drain(clock_state))
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
