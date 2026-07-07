#!/usr/bin/env python3
"""Validate enterprise source coverage mapping without network access."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CONFIG_PATH = ROOT / "config" / "enterprise_ai_sources.json"
MAPPING_PATH = ROOT / "config" / "enterprise_ai_source_mapping.json"

ALLOWED_COVERAGE_STATUSES = {
    "existing_exact",
    "existing_partial",
    "adapter_available",
    "opml_ready",
    "not_covered",
    "manual_only",
}
REQUIRED_MAPPING_KEYS = {
    "id",
    "name",
    "coverage_status",
    "existing_source_name",
    "existing_source_location",
    "existing_source_type",
    "existing_url_or_feed",
    "current_enabled_status",
    "duplicate_risk",
    "recommended_next_action",
    "notes",
}
SENSITIVE_PATTERN = re.compile(
    r"(api[_ -]?key|token|cookie|password|passwd|bearer|authorization|client[_ -]?secret|access[_ -]?key|私钥|密钥|密码|令牌|凭证)",
    re.IGNORECASE,
)
ALLOWED_SECURITY_TEXT = {
    "Cookie",
    "Token",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read {path.name}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path.name} must contain a JSON object")
    return payload


def contains_sensitive_value(value: Any) -> bool:
    if isinstance(value, str):
        match = SENSITIVE_PATTERN.search(value)
        if not match:
            return False
        return match.group(0) not in ALLOWED_SECURITY_TEXT
    if isinstance(value, list):
        return any(contains_sensitive_value(item) for item in value)
    if isinstance(value, dict):
        return any(contains_sensitive_value(item) for item in value.values())
    return False


def main() -> int:
    source_payload = load_json(SOURCE_CONFIG_PATH)
    mapping_payload = load_json(MAPPING_PATH)

    source_ids = [item.get("id") for item in source_payload.get("sources", []) if isinstance(item, dict)]
    if len(source_ids) != 24 or len(set(source_ids)) != 24:
        fail("source config must contain 24 unique ids before validating mappings")

    if mapping_payload.get("version") != "1.0":
        fail("mapping version must be 1.0")
    if mapping_payload.get("description") != "企业AI候选信源与原项目现有信源覆盖对照":
        fail("mapping description mismatch")

    mappings = mapping_payload.get("mappings")
    if not isinstance(mappings, list):
        fail("mappings must be a list")
    if len(mappings) != 24:
        fail(f"mappings must contain exactly 24 items, got {len(mappings)}")

    mapping_ids: list[str] = []
    status_counts: Counter[str] = Counter()
    for index, mapping in enumerate(mappings, start=1):
        if not isinstance(mapping, dict):
            fail(f"mapping #{index} must be an object")
        missing = REQUIRED_MAPPING_KEYS - set(mapping)
        extra = set(mapping) - REQUIRED_MAPPING_KEYS
        if missing:
            fail(f"mapping #{index} missing keys: {sorted(missing)}")
        if extra:
            fail(f"mapping #{index} has unexpected keys: {sorted(extra)}")

        mapping_id = mapping["id"]
        mapping_ids.append(mapping_id)
        if mapping_id not in source_ids:
            fail(f"mapping id not found in source config: {mapping_id}")

        status = mapping["coverage_status"]
        if status not in ALLOWED_COVERAGE_STATUSES:
            fail(f"mapping {mapping_id} has invalid coverage_status: {status}")
        status_counts[status] += 1

        if not isinstance(mapping["recommended_next_action"], str) or not mapping["recommended_next_action"].strip():
            fail(f"mapping {mapping_id} must include recommended_next_action")
        if not isinstance(mapping["notes"], str) or not mapping["notes"].strip():
            fail(f"mapping {mapping_id} must include notes")
        if mapping["duplicate_risk"] not in {"low", "medium", "high"}:
            fail(f"mapping {mapping_id} duplicate_risk must be low, medium, or high")
        if contains_sensitive_value(mapping):
            fail(f"mapping {mapping_id} appears to contain sensitive text")

    duplicated = sorted({mapping_id for mapping_id in mapping_ids if mapping_ids.count(mapping_id) > 1})
    if duplicated:
        fail(f"duplicated mapping ids: {duplicated}")
    missing_ids = sorted(set(source_ids) - set(mapping_ids))
    if missing_ids:
        fail(f"source ids missing from mapping: {missing_ids}")

    print("enterprise_ai_source_mapping.json OK")
    print(f"mappings: {len(mappings)}")
    print("coverage_status:")
    for status in sorted(ALLOWED_COVERAGE_STATUSES):
        print(f"  {status}: {status_counts.get(status, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
