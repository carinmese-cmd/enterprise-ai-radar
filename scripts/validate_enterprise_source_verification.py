from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFICATION_PATH = ROOT / "config" / "enterprise_ai_source_verification_batch1.json"

ALLOWED_FEED_STATUS = {"verified", "not_found", "invalid", "blocked", "uncertain"}
ALLOWED_DUPLICATE_RISK = {"none", "low", "medium", "high"}
ALLOWED_ACCESS_METHOD = {
    "reuse_existing",
    "rss",
    "atom",
    "opml",
    "webpage_monitor",
    "manual_review",
    "not_recommended",
}
SENSITIVE_RE = re.compile(
    r"(api[_-]?key|token|cookie|password|passwd|secret|bearer\s+)",
    re.IGNORECASE,
)


def fail(message: str) -> None:
    print(f"enterprise_ai_source_verification_batch1.json invalid: {message}", file=sys.stderr)
    raise SystemExit(1)


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)


def main() -> None:
    try:
        data = json.loads(VERIFICATION_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {VERIFICATION_PATH}")
    except json.JSONDecodeError as exc:
        fail(f"JSON parse error: {exc}")

    sources = data.get("sources")
    if not isinstance(sources, list):
        fail("sources must be a list")
    if len(sources) != 8:
        fail(f"sources must contain exactly 8 records, got {len(sources)}")

    ids = [source.get("id") for source in sources]
    if any(not source_id for source_id in ids):
        fail("every source must include id")
    duplicates = [source_id for source_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        fail(f"duplicate ids: {', '.join(sorted(duplicates))}")

    required = {
        "id",
        "name",
        "official_url",
        "page_status",
        "http_status",
        "final_url",
        "feed_discovery_method",
        "discovered_feed_url",
        "feed_type",
        "feed_status",
        "entry_count",
        "latest_entry_at",
        "sample_titles",
        "existing_project_coverage",
        "duplicate_risk",
        "recommended_access_method",
        "verification_notes",
    }

    for source in sources:
        missing = sorted(required - source.keys())
        if missing:
            fail(f"{source.get('id', '<unknown>')} missing fields: {', '.join(missing)}")
        if source["feed_status"] not in ALLOWED_FEED_STATUS:
            fail(f"{source['id']} invalid feed_status: {source['feed_status']}")
        if source["duplicate_risk"] not in ALLOWED_DUPLICATE_RISK:
            fail(f"{source['id']} invalid duplicate_risk: {source['duplicate_risk']}")
        if source["recommended_access_method"] not in ALLOWED_ACCESS_METHOD:
            fail(
                f"{source['id']} invalid recommended_access_method: "
                f"{source['recommended_access_method']}"
            )

    sensitive_hits = sorted({text for text in walk_strings(data) if SENSITIVE_RE.search(text)})
    if sensitive_hits:
        fail(f"possible sensitive strings found: {sensitive_hits[:3]}")

    status_counts = Counter(source["feed_status"] for source in sources)
    method_counts = Counter(source["recommended_access_method"] for source in sources)
    print("enterprise_ai_source_verification_batch1.json OK")
    print(f"sources: {len(sources)}")
    print("feed_status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print("recommended_access_method:")
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count}")


if __name__ == "__main__":
    main()
