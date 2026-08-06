import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from orpheus.tools import search_scholarly_evidence


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, *_args, **_kwargs):
        return json.dumps(self.payload).encode("utf-8")


class LiveResearchTests(unittest.TestCase):
    def test_crossref_results_are_bounded_and_auditable(self):
        payload = {
            "message": {
                "items": [
                    {
                        "DOI": "10.1000/example",
                        "title": ["Passive cooling for food preservation"],
                        "author": [
                            {"given": "Ada", "family": "Lovelace"},
                            {"given": "Grace", "family": "Hopper"},
                        ],
                        "published-online": {"date-parts": [[2026, 5, 1]]},
                        "container-title": ["Journal of Cooling"],
                        "type": "journal-article",
                        "URL": "https://doi.org/10.1000/example",
                        "is-referenced-by-count": 12,
                        "score": 88.1258,
                    }
                ]
            }
        }

        with patch("orpheus.tools.urlopen", return_value=FakeResponse(payload)) as mocked:
            result = search_scholarly_evidence(
                "passive cooling food preservation", limit=99
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["provider"], "Crossref REST API")
        self.assertEqual(result["result_count"], 1)
        self.assertIn("metadata", result["truth_boundary"])
        record = result["results"][0]
        self.assertEqual(record["title"], "Passive cooling for food preservation")
        self.assertEqual(record["year"], 2026)
        self.assertEqual(record["authors"], ["Ada Lovelace", "Grace Hopper"])
        self.assertEqual(record["doi"], "10.1000/example")
        self.assertEqual(record["url"], "https://doi.org/10.1000/example")
        self.assertEqual(record["relevance_score"], 88.126)

        request = mocked.call_args.args[0]
        self.assertIn("rows=8", request.full_url)
        self.assertIn("query.bibliographic=passive+cooling+food+preservation", request.full_url)

    def test_network_failure_is_evidence_not_success(self):
        with patch("orpheus.tools.urlopen", side_effect=URLError("offline")):
            result = search_scholarly_evidence("evaporative cooling", limit=3)

        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["results"], [])
        self.assertIn("must not", result["truth_boundary"])
        self.assertEqual(result["error_type"], "URLError")

    def test_invalid_query_is_rejected_before_network_access(self):
        with patch("orpheus.tools.urlopen") as mocked:
            with self.assertRaises(ValueError):
                search_scholarly_evidence("  ")
        mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
