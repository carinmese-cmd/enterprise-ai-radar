from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERIFICATION_PATH = ROOT / "config" / "enterprise_ai_source_verification_batch1.json"

ALLOWED_FEED_STATUS = {"verified", "not_found", "invalid", "blocked", "uncertain"}
ALLOWED_DUPLICATE_RISK = {"none", "low", "medium", "high"}
ALLOWED_ACCESS_METHOD = {
    "reuse_existing",
    "rss",
    "atom",
    "opml",
    "webpage_monitor",
    "github_release",
    "manual_review",
    "not_recommended",
}
ALLOWED_CONTENT_NOISE = {"low", "medium", "high"}
SENSITIVE_RE = re.compile(
    r"(api[_-]?key|token|cookie|password|passwd|secret|bearer\s+)",
    re.IGNORECASE,
)


def fail(path: Path, message: str) -> None:
    print(f"{path.name} invalid: {message}", file=sys.stderr)
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
    verification_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VERIFICATION_PATH
    if not verification_path.is_absolute():
        verification_path = ROOT / verification_path

    try:
        data = json.loads(verification_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(verification_path, f"file not found: {verification_path}")
    except json.JSONDecodeError as exc:
        fail(verification_path, f"JSON parse error: {exc}")

    sources = data.get("sources")
    if not isinstance(sources, list):
        fail(verification_path, "sources must be a list")
    if len(sources) != 8:
        fail(verification_path, f"sources must contain exactly 8 records, got {len(sources)}")

    ids = [source.get("id") for source in sources]
    if any(not source_id for source_id in ids):
        fail(verification_path, "every source must include id")
    duplicates = [source_id for source_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        fail(verification_path, f"duplicate ids: {', '.join(sorted(duplicates))}")

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
            fail(
                verification_path,
                f"{source.get('id', '<unknown>')} missing fields: {', '.join(missing)}",
            )
        if source["feed_status"] not in ALLOWED_FEED_STATUS:
            fail(verification_path, f"{source['id']} invalid feed_status: {source['feed_status']}")
        if source["duplicate_risk"] not in ALLOWED_DUPLICATE_RISK:
            fail(
                verification_path,
                f"{source['id']} invalid duplicate_risk: {source['duplicate_risk']}",
            )
        if source["recommended_access_method"] not in ALLOWED_ACCESS_METHOD:
            fail(
                verification_path,
                f"{source['id']} invalid recommended_access_method: "
                f"{source['recommended_access_method']}"
            )
        if "content_noise" in source and source["content_noise"] not in ALLOWED_CONTENT_NOISE:
            fail(verification_path, f"{source['id']} invalid content_noise: {source['content_noise']}")

    sensitive_hits = sorted({text for text in walk_strings(data) if SENSITIVE_RE.search(text)})
    if sensitive_hits:
        fail(verification_path, f"possible sensitive strings found: {sensitive_hits[:3]}")

    status_counts = Counter(source["feed_status"] for source in sources)
    method_counts = Counter(source["recommended_access_method"] for source in sources)
    print(f"{verification_path.name} OK")
    print(f"sources: {len(sources)}")
    print("feed_status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print("recommended_access_method:")
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count}")


if __name__ == "__main__":
    main()
