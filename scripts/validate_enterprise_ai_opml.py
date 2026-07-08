from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


OPML_PATH = Path("feeds/enterprise-ai-v1.opml")
EXPECTED_FEED_COUNT = 4
FORBIDDEN_DUPLICATE_SOURCES = ("openai", "anthropic", "infoq")
SENSITIVE_PATTERN = re.compile(
    r"(api[_-]?key|token|cookie|password|passwd|secret|bearer\s+)",
    re.IGNORECASE,
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def feed_outlines(root: ET.Element) -> list[ET.Element]:
    feeds: list[ET.Element] = []
    for node in root.iter("outline"):
        if node.attrib.get("xmlUrl") or node.attrib.get("type") == "rss":
            feeds.append(node)
    return feeds


def main() -> None:
    if not OPML_PATH.exists():
        fail(f"missing OPML file: {OPML_PATH}")

    content = OPML_PATH.read_text(encoding="utf-8")
    if SENSITIVE_PATTERN.search(content):
        fail("OPML appears to contain sensitive information")

    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        fail(f"invalid OPML XML: {exc}")

    feeds = feed_outlines(root)
    if len(feeds) != EXPECTED_FEED_COUNT:
        fail(f"expected {EXPECTED_FEED_COUNT} feeds, found {len(feeds)}")

    urls: list[str] = []
    titles: list[str] = []
    for index, node in enumerate(feeds, start=1):
        xml_url = (node.attrib.get("xmlUrl") or "").strip()
        title = (node.attrib.get("title") or "").strip()
        text = (node.attrib.get("text") or "").strip()
        html_url = (node.attrib.get("htmlUrl") or "").strip()

        if not xml_url:
            fail(f"feed #{index} is missing xmlUrl")
        if not title:
            fail(f"feed #{index} is missing title")
        if not html_url:
            fail(f"feed #{index} is missing htmlUrl")

        combined = " ".join([text, title, xml_url, html_url]).lower()
        for forbidden in FORBIDDEN_DUPLICATE_SOURCES:
            if forbidden in combined:
                fail(f"feed #{index} contains duplicate existing source marker: {forbidden}")

        urls.append(xml_url)
        titles.append(title)

    if len(set(urls)) != len(urls):
        fail("xmlUrl values must be unique")

    print(f"OK: {OPML_PATH} contains {len(feeds)} verified enterprise AI RSS feeds")
    for title, url in zip(titles, urls):
        print(f"- {title}: {url}")


if __name__ == "__main__":
    main()
