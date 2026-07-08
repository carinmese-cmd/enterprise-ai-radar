#!/usr/bin/env python3
"""Validate the enterprise AI source inventory config without network access."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "enterprise_ai_sources.json"

REQUIRED_TOP_KEYS = {"version", "description", "sources"}
REQUIRED_SOURCE_KEYS = {
    "id",
    "name",
    "category",
    "focus_topics",
    "source_type",
    "priority",
    "content_value",
    "automation_level",
    "evidence_level",
    "official_url",
    "feed_url",
    "feed_status",
    "verification_status",
    "enabled",
    "time_window_hours",
    "notes",
}
ALLOWED_CONTENT_VALUES = {"S", "A", "B", "C"}
ALLOWED_AUTOMATION_LEVELS = {"L1", "L2", "L3"}
ALLOWED_EVIDENCE_LEVELS = {"A", "B", "C", "D"}
ALLOWED_TIME_WINDOWS = {24, 72, 168, 720}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_source_shape(source: dict[str, Any], index: int) -> None:
    missing = REQUIRED_SOURCE_KEYS - set(source)
    extra = set(source) - REQUIRED_SOURCE_KEYS
    if missing:
        fail(f"source #{index} missing keys: {sorted(missing)}")
    if extra:
        fail(f"source #{index} has unexpected keys: {sorted(extra)}")

    source_id = source["id"]
    if not isinstance(source_id, str) or not source_id:
        fail(f"source #{index} id must be a non-empty string")
    if not all(ch.islower() or ch == "_" for ch in source_id):
        fail(f"source #{index} id must use lowercase letters and underscores: {source_id}")

    if not isinstance(source["name"], str) or not source["name"]:
        fail(f"source {source_id} name must be a non-empty string")
    if not isinstance(source["category"], str) or not source["category"]:
        fail(f"source {source_id} category must be a non-empty string")
    if not isinstance(source["focus_topics"], list) or not source["focus_topics"]:
        fail(f"source {source_id} focus_topics must be a non-empty list")
    if not all(isinstance(topic, str) and topic for topic in source["focus_topics"]):
        fail(f"source {source_id} focus_topics must contain only non-empty strings")
    if not isinstance(source["source_type"], str) or not source["source_type"]:
        fail(f"source {source_id} source_type must be a non-empty string")
    if source["content_value"] not in ALLOWED_CONTENT_VALUES:
        fail(f"source {source_id} content_value must be one of {sorted(ALLOWED_CONTENT_VALUES)}")
    if source["automation_level"] not in ALLOWED_AUTOMATION_LEVELS:
        fail(f"source {source_id} automation_level must be one of {sorted(ALLOWED_AUTOMATION_LEVELS)}")
    if source["evidence_level"] not in ALLOWED_EVIDENCE_LEVELS:
        fail(f"source {source_id} evidence_level must be one of {sorted(ALLOWED_EVIDENCE_LEVELS)}")
    if not isinstance(source["official_url"], str) or not source["official_url"].startswith("https://"):
        fail(f"source {source_id} official_url must be an https URL")
    if not isinstance(source["notes"], str) or not source["notes"]:
        fail(f"source {source_id} notes must be a non-empty string")
    if source["time_window_hours"] not in ALLOWED_TIME_WINDOWS:
        fail(f"source {source_id} time_window_hours must be one of {sorted(ALLOWED_TIME_WINDOWS)}")


def main() -> int:
    try:
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read JSON: {exc}")

    missing_top = REQUIRED_TOP_KEYS - set(payload)
    if missing_top:
        fail(f"missing top-level keys: {sorted(missing_top)}")
    if payload.get("version") != "1.0":
        fail("version must be 1.0")
    if payload.get("description") != "企业AI落地雷达V1候选信源":
        fail("description mismatch")

    sources = payload.get("sources")
    if not isinstance(sources, list):
        fail("sources must be a list")
    if len(sources) != 24:
        fail(f"sources must contain exactly 24 items, got {len(sources)}")

    ids: list[str] = []
    categories: Counter[str] = Counter()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            fail(f"source #{index} must be an object")
        validate_source_shape(source, index)
        ids.append(source["id"])
        categories[source["category"]] += 1

        if source["priority"] != "P0":
            fail(f"source {source['id']} priority must be P0")
        if source["enabled"] is not False:
            fail(f"source {source['id']} enabled must be false")
        if source["feed_status"] != "pending_verification":
            fail(f"source {source['id']} feed_status must be pending_verification")
        if source["feed_url"] is not None:
            fail(f"source {source['id']} feed_url must be null")
        if source["verification_status"] != "pending":
            fail(f"source {source['id']} verification_status must be pending")

    duplicated = sorted({source_id for source_id in ids if ids.count(source_id) > 1})
    if duplicated:
        fail(f"duplicated ids: {duplicated}")

    print("enterprise_ai_sources.json OK")
    print(f"sources: {len(sources)}")
    print("categories:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
