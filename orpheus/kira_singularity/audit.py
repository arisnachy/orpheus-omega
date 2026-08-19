from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class Receipt:
    seq: int
    event: str
    payload: dict[str, Any]
    previous_hash: str
    hash: str
    created_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "event": self.event,
            "payload": self.payload,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "created_at": self.created_at,
        }


class AuditLedger:
    def __init__(self) -> None:
        self._items: list[Receipt] = []

    def append(self, event: str, payload: dict[str, Any]) -> Receipt:
        seq = len(self._items) + 1
        previous_hash = self._items[-1].hash if self._items else "GENESIS"
        created_at = datetime.now(timezone.utc).isoformat()
        canonical = json.dumps(
            {
                "seq": seq,
                "event": event,
                "payload": payload,
                "previous_hash": previous_hash,
                "created_at": created_at,
            },
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        receipt = Receipt(seq, event, payload, previous_hash, digest, created_at)
        self._items.append(receipt)
        return receipt

    def export(self) -> tuple[dict[str, Any], ...]:
        return tuple(item.as_dict() for item in self._items)

    def verify_chain(self) -> bool:
        previous = "GENESIS"
        for expected_seq, item in enumerate(self._items, start=1):
            if item.seq != expected_seq or item.previous_hash != previous:
                return False
            canonical = json.dumps(
                {
                    "seq": item.seq,
                    "event": item.event,
                    "payload": item.payload,
                    "previous_hash": item.previous_hash,
                    "created_at": item.created_at,
                },
                sort_keys=True,
                separators=(",", ":"),
                default=str,
            )
            if hashlib.sha256(canonical.encode("utf-8")).hexdigest() != item.hash:
                return False
            previous = item.hash
        return True
