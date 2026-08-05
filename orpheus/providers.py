from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from .settings import Settings


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    model: str
    backend: str


class ReasoningProvider(Protocol):
    def generate(self, prompt: str) -> ProviderResponse: ...


class MockReasoningProvider:
    """Offline provider used to exercise orchestration without external calls."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def generate(self, prompt: str) -> ProviderResponse:
        excerpt = " ".join(prompt.split())[:240]
        return ProviderResponse(
            text=(
                "MOCK ANALYSIS — no model call was made. "
                f"Received mission context: {excerpt}"
            ),
            model="deterministic-mock",
            backend="mock",
        )


class GoogleGenAIProvider:
    """Gemini provider supporting API-key and Vertex AI authentication.

    Imports the Google SDK lazily so deterministic tests remain dependency-light.
    """

    def __init__(self, settings: Settings):
        errors = settings.validation_errors()
        if errors:
            raise RuntimeError("Invalid ORPHEUS configuration: " + "; ".join(errors))
        try:
            from google import genai
            from google.genai.types import HttpOptions
        except ImportError as exc:  # pragma: no cover - depends on optional package
            raise RuntimeError(
                'Install Google dependencies with: pip install -e ".[agent]"'
            ) from exc

        self.settings = settings
        if settings.llm_backend == "vertex_ai":
            self.client = genai.Client(
                vertexai=True,
                project=settings.google_cloud_project,
                location=settings.google_cloud_location,
                http_options=HttpOptions(api_version="v1"),
            )
        elif settings.llm_backend == "gemini_api":
            key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            self.client = genai.Client(api_key=key)
        else:  # pragma: no cover - guarded by factory
            raise RuntimeError("GoogleGenAIProvider requires a Google backend")

    def generate(self, prompt: str) -> ProviderResponse:
        response = self.client.models.generate_content(
            model=self.settings.model,
            contents=prompt,
        )
        return ProviderResponse(
            text=response.text or "",
            model=self.settings.model,
            backend=self.settings.llm_backend,
        )


def build_provider(settings: Settings | None = None) -> ReasoningProvider:
    settings = settings or Settings.from_env()
    if settings.llm_backend == "mock":
        return MockReasoningProvider(settings)
    return GoogleGenAIProvider(settings)
