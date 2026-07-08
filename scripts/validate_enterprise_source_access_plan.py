from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACCESS_PLAN_PATH = ROOT / "config" / "enterprise_ai_source_access_plan_v1.json"
SOURCE_PATH = ROOT / "config" / "enterprise_ai_sources.json"

ALLOWED_ACCESS_METHOD = {
    "reuse_existing",
    "rss",
    "atom",
    "webpage_monitor",
    "github_release",
    "manual_review",
    "not_recommended",
}
ALLOWED_IMPLEMENTATION_PHASE = {
    "phase_1_existing_and_feed",
    "phase_2_webpage_monitor",
    "phase_3_manual_report_pool",
}
ALLOWED_TIME_WINDOWS = {24, 72, 168, 720}
SENSITIVE_RE = re.compile(
    r"(api[_-]?key|token|cookie|password|passwd|secret|bearer\s+)",
    re.IGNORECASE,
)


def fail(message: str) -> None:
    print(f"enterprise_ai_source_access_plan_v1.json invalid: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"JSON parse error in {path.name}: {exc}")


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
    access_plan = load_json(ACCESS_PLAN_PATH)
    source_config = load_json(SOURCE_PATH)
    sources = access_plan.get("sources")
    candidates = source_config.get("sources")

    if not isinstance(sources, list):
        fail("sources must be a list")
    if len(sources) != 24:
        fail(f"sources must contain exactly 24 records, got {len(sources)}")
    if not isinstance(candidates, list):
        fail("candidate sources must be a list")

    candidate_ids = {source.get("id") for source in candidates}
    ids = [source.get("id") for source in sources]
    if any(not source_id for source_id in ids):
        fail("every source must include id")
    duplicates = [source_id for source_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        fail(f"duplicate ids: {', '.join(sorted(duplicates))}")
    missing_candidates = sorted(set(ids) - candidate_ids)
    if missing_candidates:
        fail(f"source ids not found in candidate config: {', '.join(missing_candidates)}")
    missing_plan = sorted(candidate_ids - set(ids))
    if missing_plan:
        fail(f"candidate ids missing from access plan: {', '.join(missing_plan)}")

    required = {
        "id",
        "name",
        "category",
        "priority",
        "recommended_access_method",
        "verified_official_url",
        "verified_feed_url",
        "time_window_hours",
        "existing_project_coverage",
        "duplicate_risk",
        "content_noise",
        "evidence_level",
        "enabled_in_v1",
        "target_section",
        "implementation_phase",
        "notes",
    }

    for source in sources:
        missing = sorted(required - source.keys())
        if missing:
            fail(f"{source.get('id', '<unknown>')} missing fields: {', '.join(missing)}")
        method = source["recommended_access_method"]
        if method not in ALLOWED_ACCESS_METHOD:
            fail(f"{source['id']} invalid recommended_access_method: {method}")
        phase = source["implementation_phase"]
        if phase not in ALLOWED_IMPLEMENTATION_PHASE:
            fail(f"{source['id']} invalid implementation_phase: {phase}")
        if source["time_window_hours"] not in ALLOWED_TIME_WINDOWS:
            fail(f"{source['id']} invalid time_window_hours: {source['time_window_hours']}")
        if source["enabled_in_v1"] is not False:
            fail(f"{source['id']} enabled_in_v1 must be false")
        if method in {"rss", "atom"} and not source["verified_feed_url"]:
            fail(f"{source['id']} {method} source must include verified_feed_url")

    sensitive_hits = sorted({text for text in walk_strings(access_plan) if SENSITIVE_RE.search(text)})
    if sensitive_hits:
        fail(f"possible sensitive strings found: {sensitive_hits[:3]}")

    method_counts = Counter(source["recommended_access_method"] for source in sources)
    window_counts = Counter(source["time_window_hours"] for source in sources)
    print("enterprise_ai_source_access_plan_v1.json OK")
    print(f"sources: {len(sources)}")
    print("recommended_access_method:")
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count}")
    print("time_window_hours:")
    for window, count in sorted(window_counts.items()):
        print(f"  {window}: {count}")


if __name__ == "__main__":
    main()
