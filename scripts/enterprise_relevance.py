#!/usr/bin/env python3
"""Enterprise AI topic scoring layered on top of generic AI relevance."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOPIC_CONFIG_PATH = ROOT / "config" / "enterprise_focus_topics.json"
ENTERPRISE_RELEVANCE_THRESHOLD = 62
TOPIC_MIN_SCORE = 42

CONTENT_TYPES: dict[str, dict[str, Any]] = {
    "enterprise_case": {
        "label": "企业案例",
        "terms": [
            "case study", "customer story", "deployed", "implementation", "adoption",
            "rollout", "results", "reduced", "increased", "achieved",
            "客户案例", "项目落地", "上线", "实施", "应用效果", "降本", "提效", "自助率", "成功率",
        ],
        "score": 20,
    },
    "product_update": {
        "label": "产品更新",
        "terms": [
            "release", "release notes", "introduces", "launch", "new feature",
            "update", "now available", "发布", "上线", "上新", "新功能", "产品更新",
        ],
        "score": 8,
    },
    "technical_practice": {
        "label": "技术实践",
        "terms": [
            "architecture", "integration", "workflow", "tutorial", "engineering",
            "production", "reference architecture", "架构", "集成", "工作流", "技术实践", "生产环境",
        ],
        "score": 12,
    },
    "research_report": {
        "label": "研究报告",
        "terms": ["report", "survey", "research", "index", "white paper", "study", "报告", "调研", "白皮书", "研究"],
        "score": 10,
    },
    "methodology_evaluation": {
        "label": "方法与评估",
        "terms": ["framework", "evaluation", "benchmark", "methodology", "governance", "roi", "assessment", "方法论", "评估", "治理", "指标体系"],
        "score": 10,
    },
}

CONTENT_TYPE_ORDER = [
    "enterprise_case",
    "technical_practice",
    "methodology_evaluation",
    "research_report",
    "product_update",
]

GENERIC_TOPIC_TERMS = {
    "ai", "agent", "service", "customer", "experience", "support", "enterprise",
    "platform", "solution", "automation", "assistant", "conversation", "voice",
}

BUSINESS_EVIDENCE_TERMS = [
    "enterprise customer", "customer case", "customer story", "case study", "business process", "workflow",
    "deployment", "rollout", "production", "system integration", "permission", "governance",
    "roi", "crm", "hr", "hcm", "customer service", "contact center", "knowledge base",
    "企业客户", "客户案例", "业务流程", "系统集成", "部署上线", "生产环境", "权限治理",
    "组织实施", "应用指标", "工作流", "企业知识", "客服", "人力资源", "智能客服", "企业知识库",
]

AI_CONTEXT_TERMS = [
    "ai", "agent", "llm", "model", "copilot", "genai", "prompt", "rag",
    "人工智能", "智能体", "大模型", "模型", "智能客服", "生成式AI",
]

NOISE_TERMS = [
    "funding", "valuation", "raised", "series a", "series b", "ipo", "acquired",
    "融资", "估值", "上市", "收购",
    "game", "gaming", "娱乐", "明星", "consumer app", "photo app",
    "leaderboard", "跑分", "benchmark only",
    "视频生成", "图像生成", "数字人视频", "ai video", "image generation",
    "seo", "geo", "网站优化", "搜索排名", "广告创意",
]

PURE_MODEL_TERMS = ["benchmark", "leaderboard", "arena", "eval result", "跑分", "榜单"]
NEGATED_ENTERPRISE_TERMS = ["no enterprise", "no deployment details", "without enterprise", "without deployment", "没有企业", "没有落地"]
ENTERPRISE_DEPTH_TERMS = [
    "architecture", "integration", "production", "deployment", "rollout", "observability",
    "permission", "security", "cost", "roi", "accuracy", "resolution rate", "case study",
    "架构", "集成", "生产环境", "上线", "权限", "安全", "成本", "投入产出", "准确率", "解决率",
]
AUTHORITY_TERMS = ["nist ai", "owasp", "mckinsey", "deloitte", "caict", "信通院", "state of ai"]


def _load_topics() -> list[dict[str, Any]]:
    payload = json.loads(TOPIC_CONFIG_PATH.read_text(encoding="utf-8"))
    topics = payload.get("topics")
    if not isinstance(topics, list):
        raise ValueError("enterprise_focus_topics.json must contain a topics list")
    return topics


TOPICS = _load_topics()
TOPIC_BY_ID = {str(topic["id"]): topic for topic in TOPICS}


def _record_values(record: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    parts: list[str] = []
    for key in keys:
        value = record.get(key)
        if value:
            parts.append(str(value))
    return parts


def _content_text_for(record: dict[str, Any]) -> str:
    parts = _record_values(
        record,
        (
            "title",
            "title_zh",
            "title_en",
            "title_original",
            "summary",
            "description",
            "content",
            "excerpt",
        ),
    )
    for key in ("ai_signals", "tags"):
        values = record.get(key)
        if isinstance(values, list):
            parts.extend(str(v) for v in values if v)
    return " ".join(parts).lower()


def _source_text_for(record: dict[str, Any]) -> str:
    return " ".join(_record_values(record, ("source", "site_name", "site_id", "author"))).lower()


def _contains(text: str, term: str) -> bool:
    needle = str(term or "").strip().lower()
    if not needle:
        return False
    if re.fullmatch(r"[a-z0-9_+\-./ ]+", needle):
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", text))
    return needle in text


def _matched(text: str, terms: list[str]) -> list[str]:
    seen: list[str] = []
    for term in terms:
        if _contains(text, term) and term not in seen:
            seen.append(term)
    return seen


def _has_ai_context(text: str) -> bool:
    return bool(_matched(text, AI_CONTEXT_TERMS))


def _has_business_evidence(text: str) -> bool:
    return bool(_matched(text, BUSINESS_EVIDENCE_TERMS))


def _topic_has_sufficient_evidence(topic_id: str, strong: list[str], support: list[str], content_text: str) -> bool:
    strong_non_generic = [term for term in strong if term.strip().lower() not in GENERIC_TOPIC_TERMS]
    support_non_generic = [term for term in support if term.strip().lower() not in GENERIC_TOPIC_TERMS]
    has_ai_context = _has_ai_context(content_text)

    if topic_id == "hr_ai":
        hr_core = _matched(content_text, ["hr", "hcm", "human resources", "employee service", "hr service delivery", "payroll", "benefits", "talent management", "人力资源", "员工服务", "薪酬", "假勤", "人才管理"])
        recruiting_only = bool(_matched(content_text, ["recruiting", "招聘"])) and not hr_core
        return bool(strong_non_generic) and has_ai_context and not recruiting_only

    if topic_id == "sales_marketing_ai":
        sales_core = _matched(content_text, ["crm", "sales agent", "salesforce", "agentforce", "lead qualification", "account planning", "customer insight", "sales prospect", "revenue operations", "商机", "销售助手", "客户分析", "案例匹配", "拜访准备", "市场拓展", "市拓"])
        generic_only = bool(_matched(content_text, ["sales", "opportunity", "bid", "revenue"])) and not sales_core
        return bool(strong_non_generic) and has_ai_context and not generic_only

    if topic_id in {"intelligent_customer_service", "enterprise_knowledge_rag"}:
        return bool(strong_non_generic) and has_ai_context

    if topic_id == "evaluation_governance":
        authority = _matched(content_text, ["nist ai", "owasp", "genai security", "ai risk", "ai governance"])
        return bool(authority) or (bool(strong_non_generic) and has_ai_context)

    if topic_id == "implementation_path":
        implementation_context = _matched(
            content_text,
            [
                "enterprise customer", "enterprise deployment", "business process",
                "system integration", "production", "production environment",
                "企业客户", "业务流程", "系统集成", "生产环境", "组织实施", "流程改造", "企业",
            ],
        )
        return bool(strong_non_generic) and bool(implementation_context)

    if topic_id == "model_platform_selection":
        selection_core = _matched(
            content_text,
            [
                "模型选型", "平台选型", "大模型选型", "私有化部署", "多模型路由",
                "模型成本", "agent platform", "ai platform", "model selection",
                "model comparison", "private deployment", "model routing",
                "control plane", "foundry",
            ],
        )
        return bool(selection_core) and has_ai_context

    if topic_id == "enterprise_strategy":
        return bool(strong_non_generic) or (len(support_non_generic) >= 2 and has_ai_context)

    return bool(strong_non_generic)


def score_topic(record: dict[str, Any], topic: dict[str, Any], content_text: str, source_text: str) -> dict[str, Any]:
    strong_terms = list(topic.get("strong_terms") or [])
    support_terms = list(topic.get("support_terms") or [])
    related_sources = list(topic.get("related_sources") or [])
    negative_terms = list(topic.get("negative_terms") or [])

    strong = _matched(content_text, strong_terms)
    support = _matched(content_text, support_terms)
    source_hits = _matched(source_text, related_sources)
    negative = _matched(content_text, negative_terms)

    if not _topic_has_sufficient_evidence(str(topic["id"]), strong, support, content_text):
        return {
            "id": topic["id"],
            "label": topic["label"],
            "score": 0,
            "matched_terms": support[:6],
            "strong_terms": strong[:4],
            "source_terms": source_hits[:3],
        }

    score = int(topic.get("base_weight") or 15)
    score += 24 + min(18, len(strong) * 6)
    if support:
        score += min(14, len(support) * 4)
    if source_hits and strong:
        score += 3
    if negative:
        score -= min(30, 14 + len(negative) * 6)

    return {
        "id": topic["id"],
        "label": topic["label"],
        "score": max(0, score),
        "matched_terms": support[:6],
        "strong_terms": strong[:4],
        "source_terms": source_hits[:3],
    }


def detect_content_type(record: dict[str, Any], text: str) -> tuple[str, list[str], int]:
    best_type = "general_news"
    best_terms: list[str] = []
    best_score = 0
    for content_type in CONTENT_TYPE_ORDER:
        cfg = CONTENT_TYPES[content_type]
        terms = _matched(text, cfg["terms"])
        if not terms:
            continue
        if content_type == "enterprise_case":
            case_anchor = _matched(text, ["case study", "customer story", "客户案例", "项目落地"])
            implementation_anchor = _matched(text, ["deployed", "implementation", "adoption", "rollout", "实施"])
            result_anchor = _matched(text, ["results", "reduced", "increased", "achieved", "应用效果", "降本", "提效", "自助率", "成功率"])
            if not (case_anchor or (implementation_anchor and result_anchor)):
                continue
        score = int(cfg["score"]) + min(8, len(terms) * 2)
        if score > best_score:
            best_type = content_type
            best_terms = terms[:5]
            best_score = score
    return best_type, best_terms, best_score


def score_enterprise_relevance(record: dict[str, Any]) -> dict[str, Any]:
    content_text = _content_text_for(record)
    source_text = _source_text_for(record)
    topic_scores = [score_topic(record, topic, content_text, source_text) for topic in TOPICS]
    matched_topics = [topic for topic in topic_scores if topic["score"] >= TOPIC_MIN_SCORE]
    matched_topics.sort(key=lambda item: item["score"], reverse=True)

    primary = matched_topics[0] if matched_topics else None
    content_type, content_terms, content_score = detect_content_type(record, content_text)

    score = 0
    reasons: list[str] = []
    if primary:
        score += min(64, primary["score"])
        reasons.append(f"主题命中：{primary['label']}")
        if primary.get("strong_terms"):
            score += 8
    if len(matched_topics) >= 2:
        score += min(10, (len(matched_topics) - 1) * 4)
        reasons.append("命中多个企业业务主题")
    if content_score and (primary or _has_business_evidence(content_text)):
        score += content_score
        reasons.append(f"内容类型：{CONTENT_TYPES.get(content_type, {}).get('label', '一般资讯')}")
        if content_type == "enterprise_case":
            score += 46 if not primary else 12

    depth_terms = _matched(content_text, ENTERPRISE_DEPTH_TERMS)
    if depth_terms and (primary or _has_business_evidence(content_text)):
        score += min(18, 8 + len(depth_terms) * 3)
        reasons.append("包含实施、架构、指标或结果信号")

    authority_terms = _matched(content_text + " " + source_text, AUTHORITY_TERMS)
    if authority_terms and (primary or _has_ai_context(content_text)):
        score += 8
        reasons.append("权威研究或治理来源")

    ai_score = float(record.get("ai_score") or 0)
    if ai_score >= 0.85 and primary:
        score += 3

    noise = _matched(content_text, NOISE_TERMS)
    if noise:
        penalty = 26 + min(24, len(noise) * 6)
        if not _has_business_evidence(content_text):
            penalty += 14
        score -= penalty
        reasons.append("泛科技、融资、消费或内容生成噪声降权")

    pure_model = _matched(content_text, PURE_MODEL_TERMS)
    negated_enterprise = _matched(content_text, NEGATED_ENTERPRISE_TERMS)
    if negated_enterprise:
        score -= 35
        reasons.append("明确缺少企业落地信息")
    if pure_model and not _has_business_evidence(content_text) and content_type != "methodology_evaluation":
        score -= 24
        reasons.append("纯模型跑分或榜单信号降权")

    if not primary and not _has_business_evidence(content_text):
        score = min(score, 40)

    score = max(0, min(100, int(round(score))))
    topics = [topic["id"] for topic in matched_topics]
    primary_id = primary["id"] if primary else None

    return {
        "score": score,
        "primary_topic": primary_id,
        "topics": topics,
        "content_type": content_type,
        "reason": "；".join(reasons[:4]) if reasons else "未命中明确企业AI业务场景",
        "is_relevant": score >= ENTERPRISE_RELEVANCE_THRESHOLD,
        "matched_terms": {
            "topic": (primary or {}).get("matched_terms", []),
            "strong": (primary or {}).get("strong_terms", []),
            "source": (primary or {}).get("source_terms", []),
            "content_type": content_terms,
            "depth": depth_terms[:5],
            "noise": noise[:5],
        },
    }


def add_enterprise_relevance_fields(record: dict[str, Any]) -> dict[str, Any]:
    relevance = score_enterprise_relevance(record)
    out = dict(record)
    out["enterprise_score"] = relevance["score"]
    out["enterprise_primary_topic"] = relevance["primary_topic"]
    out["enterprise_topics"] = relevance["topics"]
    out["enterprise_content_type"] = relevance["content_type"]
    out["enterprise_reason"] = relevance["reason"]
    out["enterprise_is_relevant"] = relevance["is_relevant"]
    out["enterprise_matched_terms"] = relevance["matched_terms"]
    return out


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value)
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def enterprise_freshness_score(item: dict[str, Any], now: datetime) -> int:
    published = _parse_time(item.get("published_at") or item.get("latest_at") or item.get("first_seen_at"))
    if not published:
        return 35
    age_hours = max(0, (now.astimezone(timezone.utc) - published).total_seconds() / 3600)
    return max(0, min(100, round(100 * math.pow(0.5, age_hours / 72))))


def enterprise_headline_score(item: dict[str, Any], now: datetime) -> int:
    enterprise = int(item.get("enterprise_score") or 0)
    content_type = str(item.get("enterprise_content_type") or "general_news")
    depth = 100 if content_type == "enterprise_case" else 78 if content_type in {"technical_practice", "methodology_evaluation"} else 60
    source_rank = int(item.get("source_tier_rank") or 6)
    source = max(30, 100 - source_rank * 10)
    freshness = enterprise_freshness_score(item, now)
    novelty = 72
    if item.get("enterprise_is_relevant"):
        novelty += 8
    score = enterprise * 0.45 + depth * 0.2 + source * 0.15 + freshness * 0.1 + novelty * 0.1
    return max(0, min(100, round(score)))


def select_enterprise_headlines(
    items: list[dict[str, Any]],
    now: datetime,
    *,
    limit: int = 10,
    max_per_source: int = 2,
    max_per_topic: int = 3,
) -> list[dict[str, Any]]:
    candidates = [
        item for item in items
        if int(item.get("enterprise_score") or 0) >= ENTERPRISE_RELEVANCE_THRESHOLD
        and item.get("enterprise_primary_topic")
    ]
    candidates.sort(key=lambda item: (enterprise_headline_score(item, now), int(item.get("enterprise_score") or 0), _parse_time(item.get("published_at")) or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)

    picked: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}
    topic_counts: dict[str, int] = {}
    seen_titles: set[str] = set()

    def can_pick(item: dict[str, Any], strict: bool) -> bool:
        title = re.sub(r"\s+", " ", str(item.get("title") or item.get("title_zh") or "")).strip().lower()
        if title and title in seen_titles:
            return False
        source = str(item.get("source") or item.get("site_name") or item.get("site_id") or "")
        topic = str(item.get("enterprise_primary_topic") or "")
        if strict and source_counts.get(source, 0) >= max_per_source:
            return False
        if strict and topic_counts.get(topic, 0) >= max_per_topic:
            return False
        return True

    for strict in (True, False):
        for item in candidates:
            if len(picked) >= limit:
                break
            source = str(item.get("source") or item.get("site_name") or item.get("site_id") or "")
            if source_counts.get(source, 0) >= max_per_source:
                continue
            if not can_pick(item, strict):
                continue
            title = re.sub(r"\s+", " ", str(item.get("title") or item.get("title_zh") or "")).strip().lower()
            topic = str(item.get("enterprise_primary_topic") or "")
            if title:
                seen_titles.add(title)
            source_counts[source] = source_counts.get(source, 0) + 1
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            picked.append(item)
        if len(picked) >= limit:
            break
    return picked
