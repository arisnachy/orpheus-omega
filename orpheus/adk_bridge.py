from __future__ import annotations

import asyncio
import importlib.util
import json
import re
from datetime import datetime, timezone
from typing import Any, AsyncIterator
from uuid import uuid4

from .settings import Settings

APP_NAME = "agent_app"
MAX_TEXT_LENGTH = 12_000
MAX_SERIALIZED_LENGTH = 24_000
IDENTIFIER_PATTERN = re.compile(r"[^a-zA-Z0-9_.:-]+")
GOOGLE_KEY_PATTERN = re.compile(r"\b(?:AIza|AQ\.)[A-Za-z0-9._-]{18,}\b")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[_ -]?key|authorization|bearer|token)\s*[:=]\s*([^\s,;]+)"
)


def adk_dependency_available() -> bool:
    """Return whether Google ADK can be imported without importing the agent app."""

    try:
        return importlib.util.find_spec("google.adk") is not None
    except (ImportError, ModuleNotFoundError, AttributeError, ValueError):
        return False


def _truncate(value: str, limit: int = MAX_TEXT_LENGTH) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 24] + "… [truncated]"


def _redact_runtime_text(value: Any, limit: int = 2_000) -> str:
    """Remove common credential shapes from diagnostic text before browser output."""

    message = _truncate(str(value or ""), limit)
    message = GOOGLE_KEY_PATTERN.sub("[redacted-key]", message)
    message = SECRET_ASSIGNMENT_PATTERN.sub(r"\1=[redacted]", message)
    return message


def _json_safe(value: Any, *, depth: int = 0) -> Any:
    """Convert ADK/Pydantic values into bounded JSON-safe data.

    Binary payloads are represented by metadata only. This avoids accidentally
    exposing artifacts or producing unbounded browser events.
    """

    if depth > 8:
        return "[maximum serialization depth reached]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _truncate(value)
    if isinstance(value, bytes):
        return {"binary_bytes": len(value)}
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, dict):
        return {
            _truncate(str(key), 180): _json_safe(item, depth=depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item, depth=depth + 1) for item in value]

    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            return _json_safe(model_dump(exclude_none=True), depth=depth + 1)
        except TypeError:
            return _json_safe(model_dump(), depth=depth + 1)

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return _json_safe(to_dict(), depth=depth + 1)

    return _truncate(str(value))


def _bounded_payload(value: Any) -> Any:
    safe = _json_safe(value)
    encoded = json.dumps(safe, ensure_ascii=False, default=str)
    if len(encoded) <= MAX_SERIALIZED_LENGTH:
        return safe
    return {
        "summary": _truncate(encoded, MAX_SERIALIZED_LENGTH),
        "truncated": True,
    }


def _iso_timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            pass
    return datetime.now(timezone.utc).isoformat()


def _sanitize_identifier(value: str | None, fallback: str) -> str:
    cleaned = IDENTIFIER_PATTERN.sub("-", (value or "").strip()).strip("-._:")
    return (cleaned or fallback)[:120]


def _exception_leaves(exc: BaseException, *, depth: int = 0) -> list[BaseException]:
    """Flatten ExceptionGroup/TaskGroup wrappers into concrete leaf failures."""

    if depth > 8:
        return [exc]
    nested = getattr(exc, "exceptions", None)
    if nested:
        leaves: list[BaseException] = []
        for child in nested:
            if isinstance(child, BaseException):
                leaves.extend(_exception_leaves(child, depth=depth + 1))
        return leaves or [exc]
    cause = getattr(exc, "__cause__", None)
    if isinstance(cause, BaseException) and cause is not exc:
        return _exception_leaves(cause, depth=depth + 1)
    return [exc]


def serialize_runtime_exception(exc: BaseException) -> dict[str, Any]:
    """Return a safe, actionable diagnosis for ADK and TaskGroup failures."""

    leaves = _exception_leaves(exc)
    details: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for leaf in leaves:
        item = {
            "type": type(leaf).__name__,
            "message": _redact_runtime_text(leaf),
        }
        signature = (item["type"], item["message"])
        if signature in seen:
            continue
        seen.add(signature)
        details.append(item)
        if len(details) >= 8:
            break

    combined = " ".join(
        f"{item['type']} {item['message']}" for item in details
    ).lower()
    classification = "runtime_error"
    retryable = False
    recovery = (
        "Revisa la causa concreta mostrada, conserva la sesión y vuelve a ejecutar "
        "después de corregir la configuración o herramienta indicada."
    )

    if any(token in combined for token in (
        "429",
        "resource_exhausted",
        "quota",
        "rate limit",
        "too many requests",
    )):
        classification = "quota_or_rate_limit"
        retryable = True
        recovery = (
            "Usa ORPHEUS_EXECUTION_PROFILE=free_safe, espera el período indicado por "
            "el proveedor y reintenta la misma sesión. No lances agentes en paralelo "
            "con una cuota gratuita limitada."
        )
    elif any(token in combined for token in (
        "401",
        "403",
        "unauthenticated",
        "permission_denied",
        "api key not valid",
        "invalid api key",
        "permission denied",
    )):
        classification = "authentication_or_permission"
        recovery = (
            "Revoca cualquier clave expuesta, crea una nueva y confirma que Gemini API "
            "esté habilitada para esa clave. No pegues la clave en el chat ni en GitHub."
        )
    elif any(token in combined for token in (
        "404",
        "model not found",
        "not found for api version",
        "unsupported model",
        "unknown model",
    )):
        classification = "model_configuration"
        recovery = (
            "Comprueba ORPHEUS_MODEL y usa un identificador disponible para tu cuenta "
            "y backend; reinicia el servidor después de cambiarlo."
        )
    elif any(token in combined for token in (
        "timeout",
        "timed out",
        "connection reset",
        "connection refused",
        "name resolution",
        "dns",
        "network",
        "ssl",
    )):
        classification = "network_or_timeout"
        retryable = True
        recovery = (
            "Comprueba la conexión, espera unos segundos y reintenta. La sesión queda "
            "identificada para que el fallo sea auditable."
        )
    elif any(token in combined for token in (
        "context length",
        "maximum context",
        "token limit",
        "max output",
    )):
        classification = "context_or_output_limit"
        recovery = (
            "Reduce el tamaño de la misión o de las salidas intermedias y vuelve a "
            "ejecutar sin eliminar la evidencia ya producida."
        )

    if not details:
        details = [{"type": type(exc).__name__, "message": "Fallo sin detalle público."}]

    first = details[0]
    if len(details) == 1:
        summary = first["message"] or first["type"]
    else:
        summary = (
            f"{len(details)} fallos internos detectados; causa principal: "
            f"{first['type']}: {first['message']}"
        )

    return {
        "error_code": classification,
        "error_type": type(exc).__name__,
        "error_message": _truncate(summary, 2_000),
        "error_details": details,
        "retryable": retryable,
        "recovery": recovery,
    }


def serialize_adk_event(event: Any, *, sequence: int) -> dict[str, Any]:
    """Create a browser-safe, auditable record from one Google ADK Event.

    Model reasoning parts marked as ``thought`` are never transmitted. The public
    trace records only their count, preserving observability without exposing
    private chain-of-thought content.
    """

    texts: list[str] = []
    thought_parts_count = 0
    tool_calls: list[dict[str, Any]] = []
    tool_results: list[dict[str, Any]] = []
    attachments: list[dict[str, Any]] = []

    content = getattr(event, "content", None)
    for part in list(getattr(content, "parts", None) or []):
        text = getattr(part, "text", None)
        is_thought = bool(getattr(part, "thought", False))
        if text and is_thought:
            thought_parts_count += 1
        elif text:
            texts.append(_truncate(str(text)))

        function_call = getattr(part, "function_call", None)
        if function_call is not None:
            tool_calls.append(
                {
                    "id": getattr(function_call, "id", None),
                    "name": getattr(function_call, "name", None) or "unknown_tool",
                    "args": _bounded_payload(getattr(function_call, "args", None)),
                }
            )

        function_response = getattr(part, "function_response", None)
        if function_response is not None:
            tool_results.append(
                {
                    "id": getattr(function_response, "id", None),
                    "name": getattr(function_response, "name", None) or "unknown_tool",
                    "response": _bounded_payload(
                        getattr(function_response, "response", None)
                    ),
                }
            )

        inline_data = getattr(part, "inline_data", None)
        if inline_data is not None:
            data = getattr(inline_data, "data", None)
            attachments.append(
                {
                    "kind": "inline_data",
                    "mime_type": getattr(inline_data, "mime_type", None),
                    "byte_length": len(data) if isinstance(data, bytes) else None,
                }
            )

        file_data = getattr(part, "file_data", None)
        if file_data is not None:
            attachments.append(
                {
                    "kind": "file_data",
                    "mime_type": getattr(file_data, "mime_type", None),
                    "uri_present": bool(getattr(file_data, "file_uri", None)),
                }
            )

    actions = getattr(event, "actions", None)
    state_delta = getattr(actions, "state_delta", None) if actions else None
    artifact_delta = getattr(actions, "artifact_delta", None) if actions else None

    try:
        is_final = bool(event.is_final_response())
    except (AttributeError, TypeError):
        is_final = False

    if tool_calls:
        kind = "tool_call"
    elif tool_results:
        kind = "tool_result"
    elif is_final:
        kind = "final"
    elif texts:
        kind = "model"
    elif state_delta:
        kind = "state"
    else:
        kind = "event"

    return {
        "sequence": sequence,
        "kind": kind,
        "id": getattr(event, "id", None),
        "invocation_id": getattr(event, "invocation_id", None),
        "branch": getattr(event, "branch", None),
        "author": getattr(event, "author", None) or "system",
        "timestamp": _iso_timestamp(getattr(event, "timestamp", None)),
        "is_final": is_final,
        "texts": texts,
        "thought_parts_count": thought_parts_count,
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "state_delta": _bounded_payload(state_delta) if state_delta else {},
        "artifact_delta": _bounded_payload(artifact_delta) if artifact_delta else {},
        "attachments": attachments,
        "error_code": getattr(event, "error_code", None),
        "error_message": _redact_runtime_text(
            getattr(event, "error_message", "") or ""
        ),
    }


class AdkRuntimeBridge:
    """Optional bridge from FastAPI to the real Google ADK Runner event stream.

    The bridge remains inert in the default credential-free mock mode. Imports of
    the ADK agent graph and creation of the Runner happen only on a configured run.
    """

    def __init__(self) -> None:
        self._runner: Any | None = None
        self._session_service: Any | None = None
        self._runtime_lock = asyncio.Lock()
        self._session_locks: dict[str, asyncio.Lock] = {}

    def readiness(self) -> dict[str, Any]:
        settings = Settings.from_env()
        available = adk_dependency_available()
        errors = list(settings.validation_errors())
        if not available:
            errors.append('Google ADK is not installed; install with pip install -e ".[agent]"')
        if settings.llm_backend == "mock":
            errors.append(
                "ORPHEUS_LLM_BACKEND is mock; configure gemini_api or vertex_ai "
                "for a real ADK run"
            )

        return {
            "ready": not errors,
            "dependency_available": available,
            "backend": settings.llm_backend,
            "model": settings.model,
            "runtime_mode": settings.runtime_mode,
            "execution_profile": settings.execution_profile,
            "squad_concurrency": (
                "sequential"
                if settings.execution_profile == "free_safe"
                else "parallel"
            ),
            "validation_errors": errors,
            "credentials_present": settings.public_summary()["credentials_present"],
            "stream_endpoint": "/adk/stream",
            "interface": "/adk",
            "persistence": "in_memory_session_service",
            "truth_boundary": (
                "This endpoint streams real ADK Runner events only when Gemini or "
                "Vertex AI is configured. It never simulates an ADK run in mock mode "
                "and never exposes model chain-of-thought content."
            ),
        }

    async def _ensure_runtime(self) -> tuple[Any, Any]:
        async with self._runtime_lock:
            if self._runner is not None and self._session_service is not None:
                return self._runner, self._session_service

            readiness = self.readiness()
            if not readiness["ready"]:
                raise RuntimeError("; ".join(readiness["validation_errors"]))

            from agent_app.agent import root_agent
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService

            self._session_service = InMemorySessionService()
            self._runner = Runner(
                agent=root_agent,
                app_name=APP_NAME,
                session_service=self._session_service,
            )
            return self._runner, self._session_service

    async def _ensure_session(
        self,
        session_service: Any,
        *,
        user_id: str,
        session_id: str,
    ) -> None:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )

    async def stream(
        self,
        goal: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        if not goal.strip():
            raise ValueError("A non-empty goal is required")

        runner, session_service = await self._ensure_runtime()
        settings = Settings.from_env()
        resolved_user_id = _sanitize_identifier(user_id, "orpheus-demo-user")
        resolved_session_id = _sanitize_identifier(
            session_id,
            f"orpheus-{uuid4().hex}",
        )
        session_key = f"{resolved_user_id}:{resolved_session_id}"
        session_lock = self._session_locks.setdefault(session_key, asyncio.Lock())

        yield {
            "sequence": 0,
            "kind": "session",
            "author": "ORPHEUS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": resolved_session_id,
            "user_id": resolved_user_id,
            "app_name": APP_NAME,
            "execution_profile": settings.execution_profile,
            "squad_concurrency": (
                "sequential"
                if settings.execution_profile == "free_safe"
                else "parallel"
            ),
            "message": "Real Google ADK execution started.",
        }

        async with session_lock:
            await self._ensure_session(
                session_service,
                user_id=resolved_user_id,
                session_id=resolved_session_id,
            )

            from google.genai import types

            content = types.Content(
                role="user",
                parts=[types.Part(text=_truncate(goal.strip(), 4_000))],
            )
            sequence = 0
            final_seen = False
            async for event in runner.run_async(
                user_id=resolved_user_id,
                session_id=resolved_session_id,
                new_message=content,
            ):
                sequence += 1
                record = serialize_adk_event(event, sequence=sequence)
                final_seen = final_seen or bool(record["is_final"])
                yield record

            yield {
                "sequence": sequence + 1,
                "kind": "complete",
                "author": "ORPHEUS",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": resolved_session_id,
                "event_count": sequence,
                "final_response_observed": final_seen,
                "message": "ADK invocation completed and all events were consumed.",
            }

    async def run(
        self,
        goal: str,
        *,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        records = [
            record
            async for record in self.stream(
                goal,
                user_id=user_id,
                session_id=session_id,
            )
        ]
        final_text = ""
        for record in records:
            if record.get("is_final") and record.get("texts"):
                final_text = "\n".join(record["texts"])
        session_record = records[0] if records else {}
        return {
            "session_id": session_record.get("session_id"),
            "event_count": max(len(records) - 2, 0),
            "final_text": final_text,
            "events": records,
        }


adk_runtime = AdkRuntimeBridge()
