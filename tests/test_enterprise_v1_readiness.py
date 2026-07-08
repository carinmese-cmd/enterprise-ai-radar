import json
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_enterprise_topic_config_contains_eight_topics():
    payload = load_json("config/enterprise_focus_topics.json")
    topics = payload["topics"]
    assert len(topics) == 8
    assert {topic["id"] for topic in topics} == {
        "enterprise_strategy",
        "implementation_path",
        "hr_ai",
        "sales_marketing_ai",
        "intelligent_customer_service",
        "enterprise_knowledge_rag",
        "model_platform_selection",
        "evaluation_governance",
    }


def test_enterprise_opml_contains_exactly_four_public_feeds():
    tree = ET.parse(ROOT / "feeds/enterprise-ai-v1.opml")
    feeds = [
        outline
        for outline in tree.getroot().iter("outline")
        if outline.attrib.get("xmlUrl")
    ]
    assert len(feeds) == 4
    titles = {feed.attrib.get("title") or feed.attrib.get("text") for feed in feeds}
    assert titles == {
        "Azure AI Foundry Blog",
        "Salesforce Blog / Agentforce",
        "Intercom AI & ML",
        "OWASP GenAI Security Project",
    }


def test_v1_source_access_plan_enables_only_phase_one_sources():
    plan = load_json("config/enterprise_ai_source_access_plan_v1.json")
    enabled = {source["name"] for source in plan["sources"] if source["enabled_in_v1"]}
    assert enabled == {
        "OpenAI News",
        "Anthropic Newsroom",
        "Azure AI Foundry Blog",
        "Salesforce Blog / Agentforce",
        "Intercom AI & ML",
        "InfoQ AI",
        "OWASP GenAI Security Project",
    }
    assert len(enabled) == 7
    assert sum(1 for source in plan["sources"] if not source["enabled_in_v1"]) == 17


def test_v1_source_access_plan_method_counts_unchanged():
    plan = load_json("config/enterprise_ai_source_access_plan_v1.json")
    counts = {}
    for source in plan["sources"]:
        counts[source["recommended_access_method"]] = counts.get(source["recommended_access_method"], 0) + 1
    assert counts["reuse_existing"] == 3
    assert counts["rss"] == 4
    assert counts["webpage_monitor"] == 14
    assert counts["manual_review"] == 3


def test_frontend_keeps_legacy_json_fallbacks():
    app_js = (ROOT / "assets/app.js").read_text(encoding="utf-8")
    assert 'item.enterprise_primary_topic || "unclassified"' in app_js
    assert 'Array.isArray(item.enterprise_topics)' in app_js
    assert 'if (state.activeSection !== "hot") return new Set();' in app_js


def test_workflow_uses_public_enterprise_opml_without_paid_sources():
    workflow = (ROOT / ".github/workflows/update-news.yml").read_text(encoding="utf-8")
    assert "feeds/enterprise-ai-v1.opml" in workflow
    assert "--rss-opml feeds/runtime.opml" in workflow
    assert 'RSS_MAX_FEEDS: ${{ vars.RSS_MAX_FEEDS || 20 }}' in workflow
    assert 'EMAIL_DIGEST_ENABLED: "0"' in workflow
    assert 'X_API_ENABLED: "0"' in workflow
    assert 'SOCIALDATA_ENABLED: "0"' in workflow
    assert 'TIKHUB_ENABLED: "0"' in workflow
