from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime configuration loaded exclusively from environment variables.

    Secrets are never included in ``public_summary`` or readiness responses.
    ``execution_profile`` controls orchestration pressure, not which specialists
    exist. ``free_safe`` preserves the complete 18-agent workflow but runs squad
    members sequentially to avoid burst concurrency on local/free Gemini access.
    """

    runtime_mode: str = "local"
    llm_backend: str = "mock"
    model: str = "gemini-3.6-flash"
    execution_profile: str = "parallel"
    google_cloud_project: str | None = None
    google_cloud_location: str = "global"
    firestore_enabled: bool = False
    firestore_collection: str = "orpheus_missions"
    pubsub_enabled: bool = False
    pubsub_topic: str = "orpheus-mission-events"
    storage_enabled: bool = False
    storage_bucket: str | None = None
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        runtime_mode = os.getenv("ORPHEUS_RUNTIME_MODE", "local").strip().lower()
        llm_backend = os.getenv("ORPHEUS_LLM_BACKEND", "mock").strip().lower()
        profile_default = (
            "free_safe"
            if runtime_mode == "local" and llm_backend == "gemini_api"
            else "parallel"
        )
        execution_profile = os.getenv(
            "ORPHEUS_EXECUTION_PROFILE", profile_default
        ).strip().lower()

        return cls(
            runtime_mode=runtime_mode,
            llm_backend=llm_backend,
            model=os.getenv("ORPHEUS_MODEL", "gemini-3.6-flash").strip(),
            execution_profile=execution_profile,
            google_cloud_project=(os.getenv("GOOGLE_CLOUD_PROJECT") or None),
            google_cloud_location=os.getenv("GOOGLE_CLOUD_LOCATION", "global").strip(),
            firestore_enabled=_as_bool(os.getenv("ORPHEUS_FIRESTORE_ENABLED")),
            firestore_collection=os.getenv(
                "ORPHEUS_FIRESTORE_COLLECTION", "orpheus_missions"
            ).strip(),
            pubsub_enabled=_as_bool(os.getenv("ORPHEUS_PUBSUB_ENABLED")),
            pubsub_topic=os.getenv(
                "ORPHEUS_PUBSUB_TOPIC", "orpheus-mission-events"
            ).strip(),
            storage_enabled=_as_bool(os.getenv("ORPHEUS_STORAGE_ENABLED")),
            storage_bucket=(os.getenv("ORPHEUS_STORAGE_BUCKET") or None),
            log_level=os.getenv("ORPHEUS_LOG_LEVEL", "INFO").strip().upper(),
        )

    def validation_errors(self) -> list[str]:
        errors: list[str] = []
        if self.runtime_mode not in {"local", "google_cloud"}:
            errors.append("ORPHEUS_RUNTIME_MODE must be local or google_cloud")
        if self.llm_backend not in {"mock", "gemini_api", "vertex_ai"}:
            errors.append(
                "ORPHEUS_LLM_BACKEND must be mock, gemini_api, or vertex_ai"
            )
        if self.execution_profile not in {"free_safe", "parallel"}:
            errors.append(
                "ORPHEUS_EXECUTION_PROFILE must be free_safe or parallel"
            )
        if not self.model:
            errors.append("ORPHEUS_MODEL is required")
        if self.llm_backend == "gemini_api" and not (
            os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        ):
            errors.append("GEMINI_API_KEY or GOOGLE_API_KEY is required")
        if self.llm_backend == "vertex_ai":
            if not self.google_cloud_project:
                errors.append("GOOGLE_CLOUD_PROJECT is required for Vertex AI")
            if not self.google_cloud_location:
                errors.append("GOOGLE_CLOUD_LOCATION is required for Vertex AI")
        if self.runtime_mode == "google_cloud" and self.llm_backend == "mock":
            errors.append("google_cloud mode cannot use the mock LLM backend")
        if self.storage_enabled and not self.storage_bucket:
            errors.append("ORPHEUS_STORAGE_BUCKET is required when storage is enabled")
        return errors

    @property
    def ready(self) -> bool:
        return not self.validation_errors()

    def public_summary(self) -> dict[str, Any]:
        data = asdict(self)
        data["ready"] = self.ready
        data["validation_errors"] = self.validation_errors()
        data["credentials_present"] = {
            "gemini_api_key": bool(
                os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            ),
            "vertex_project": bool(self.google_cloud_project),
        }
        data["execution_behavior"] = {
            "all_specialists_enabled": True,
            "squad_concurrency": (
                "sequential" if self.execution_profile == "free_safe" else "parallel"
            ),
            "purpose": (
                "avoid local/free-tier burst failures"
                if self.execution_profile == "free_safe"
                else "maximize cloud throughput"
            ),
        }
        return data
