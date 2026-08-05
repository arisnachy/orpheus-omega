from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.main import adk_readiness
from orpheus.adk_bridge import AdkRuntimeBridge, serialize_adk_event


class FakeEvent:
    def __init__(
        self,
        *,
        author: str,
        parts: list[SimpleNamespace],
        final: bool = False,
        sequence_id: str = "event-1",
        state_delta: dict | None = None,
    ) -> None:
        self.author = author
        self.content = SimpleNamespace(parts=parts)
        self.id = sequence_id
        self.invocation_id = "invocation-1"
        self.branch = None
        self.timestamp = 1_780_000_000.0
        self.actions = SimpleNamespace(
            state_delta=state_delta or {},
            artifact_delta={},
        )
        self.error_code = None
        self.error_message = None
        self._final = final

    def is_final_response(self) -> bool:
        return self._final


class FakeSessionService:
    def __init__(self) -> None:
        self.session = None
        self.created = 0

    async def get_session(self, **_: object):
        return self.session

    async def create_session(self, **kwargs: object):
        self.created += 1
        self.session = SimpleNamespace(**kwargs)
        return self.session


class FakeRunner:
    def __init__(self, events: list[FakeEvent]) -> None:
        self.events = events
        self.calls: list[dict] = []

    async def run_async(self, **kwargs: object):
        self.calls.append(kwargs)
        for event in self.events:
            yield event


class EventSerializationTests(unittest.TestCase):
    def test_tool_call_is_bounded_and_structured(self):
        call = SimpleNamespace(id="call-1", name="evaluate_candidate", args={"x": 1})
        part = SimpleNamespace(
            text=None,
            thought=False,
            function_call=call,
            function_response=None,
            inline_data=None,
            file_data=None,
        )
        record = serialize_adk_event(
            FakeEvent(author="spark", parts=[part]),
            sequence=4,
        )

        self.assertEqual(record["kind"], "tool_call")
        self.assertEqual(record["sequence"], 4)
        self.assertEqual(record["author"], "spark")
        self.assertEqual(record["tool_calls"][0]["name"], "evaluate_candidate")
        self.assertEqual(record["tool_calls"][0]["args"], {"x": 1})

    def test_binary_content_is_never_exposed(self):
        inline_data = SimpleNamespace(mime_type="image/png", data=b"secret-bytes")
        part = SimpleNamespace(
            text=None,
            thought=False,
            function_call=None,
            function_response=None,
            inline_data=inline_data,
            file_data=None,
        )
        record = serialize_adk_event(
            FakeEvent(author="echo", parts=[part]),
            sequence=1,
        )

        self.assertEqual(record["attachments"][0]["byte_length"], 12)
        self.assertNotIn("secret-bytes", str(record))

    def test_file_uri_is_reduced_to_presence_metadata(self):
        file_data = SimpleNamespace(
            mime_type="application/pdf",
            file_uri="gs://private-bucket/sensitive-file.pdf",
        )
        part = SimpleNamespace(
            text=None,
            thought=False,
            function_call=None,
            function_response=None,
            inline_data=None,
            file_data=file_data,
        )
        record = serialize_adk_event(
            FakeEvent(author="echo", parts=[part]),
            sequence=2,
        )

        self.assertEqual(record["attachments"][0]["uri_present"], True)
        self.assertNotIn("private-bucket", str(record))

    def test_private_thought_text_is_never_transmitted(self):
        part = SimpleNamespace(
            text="private reasoning that must not be exposed",
            thought=True,
            function_call=None,
            function_response=None,
            inline_data=None,
            file_data=None,
        )
        record = serialize_adk_event(
            FakeEvent(author="vega", parts=[part]),
            sequence=3,
        )

        self.assertEqual(record["thought_parts_count"], 1)
        self.assertEqual(record["texts"], [])
        self.assertNotIn("private reasoning", str(record))
        self.assertNotIn("thoughts", record)

    def test_final_text_is_marked_as_final(self):
        part = SimpleNamespace(
            text="Decisión final basada en evidencia.",
            thought=False,
            function_call=None,
            function_response=None,
            inline_data=None,
            file_data=None,
        )
        record = serialize_adk_event(
            FakeEvent(author="kira", parts=[part], final=True),
            sequence=9,
        )

        self.assertEqual(record["kind"], "final")
        self.assertTrue(record["is_final"])
        self.assertEqual(record["texts"], ["Decisión final basada en evidencia."])


class BridgeRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_consumes_all_events_after_final_marker(self):
        text_part = SimpleNamespace(
            text="Respuesta de KIRA",
            thought=False,
            function_call=None,
            function_response=None,
            inline_data=None,
            file_data=None,
        )
        state_part = SimpleNamespace(
            text=None,
            thought=False,
            function_call=None,
            function_response=None,
            inline_data=None,
            file_data=None,
        )
        events = [
            FakeEvent(author="kira", parts=[text_part], final=True, sequence_id="final"),
            FakeEvent(
                author="orpheus_omega",
                parts=[state_part],
                sequence_id="callback-tail",
                state_delta={"audit_complete": True},
            ),
        ]
        bridge = AdkRuntimeBridge()
        bridge._runner = FakeRunner(events)
        bridge._session_service = FakeSessionService()

        records = [
            record
            async for record in bridge.stream(
                "A measurable mission",
                user_id="demo user",
            )
        ]

        self.assertEqual([record["kind"] for record in records], [
            "session",
            "final",
            "state",
            "complete",
        ])
        self.assertEqual(records[-1]["event_count"], 2)
        self.assertTrue(records[-1]["final_response_observed"])
        self.assertEqual(bridge._session_service.created, 1)
        self.assertEqual(len(bridge._runner.calls), 1)

    async def test_run_returns_final_text_and_auditable_events(self):
        part = SimpleNamespace(
            text="Resultado verificable",
            thought=False,
            function_call=None,
            function_response=None,
            inline_data=None,
            file_data=None,
        )
        bridge = AdkRuntimeBridge()
        bridge._runner = FakeRunner([
            FakeEvent(author="kira", parts=[part], final=True),
        ])
        bridge._session_service = FakeSessionService()

        result = await bridge.run("Mission")

        self.assertEqual(result["final_text"], "Resultado verificable")
        self.assertEqual(result["event_count"], 1)
        self.assertEqual(result["events"][-1]["kind"], "complete")


class ReadinessTests(unittest.TestCase):
    def test_default_mock_mode_refuses_to_fake_a_real_adk_run(self):
        with patch.dict(os.environ, {}, clear=True):
            state = adk_readiness()

        self.assertFalse(state["ready"])
        self.assertEqual(state["backend"], "mock")
        self.assertTrue(
            any("mock" in error.lower() for error in state["validation_errors"])
        )
        self.assertIn("never simulates", state["truth_boundary"])
        self.assertIn("never exposes", state["truth_boundary"])


if __name__ == "__main__":
    unittest.main()
