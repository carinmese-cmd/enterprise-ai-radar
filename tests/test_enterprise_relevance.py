from datetime import datetime, timezone

from scripts.enterprise_relevance import (
    add_enterprise_relevance_fields,
    score_enterprise_relevance,
    select_enterprise_headlines,
)


def rec(title, source="Test Source", **extra):
    data = {
        "title": title,
        "source": source,
        "site_name": source,
        "site_id": "opmlrss",
        "published_at": "2026-07-08T08:00:00Z",
        "ai_score": 0.9,
        "ai_label": "ai_general",
    }
    data.update(extra)
    return data


def test_hr_ai_classification():
    result = score_enterprise_relevance(rec("Workday employee service AI agent for HR Service Delivery and payroll"))
    assert result["primary_topic"] == "hr_ai"
    assert result["score"] >= 60


def test_sales_marketing_ai_classification():
    result = score_enterprise_relevance(rec("Agentforce sales agent improves CRM lead qualification and account planning"))
    assert result["primary_topic"] == "sales_marketing_ai"
    assert result["is_relevant"] is True


def test_intelligent_customer_service_classification():
    result = score_enterprise_relevance(rec("AI customer support agent improves ticket resolution rate and self-service deflection"))
    assert result["primary_topic"] == "intelligent_customer_service"
    assert result["is_relevant"] is True


def test_enterprise_knowledge_base_classification():
    result = score_enterprise_relevance(rec("Enterprise knowledge base RAG adds permission filtering and citation grounding"))
    assert result["primary_topic"] == "enterprise_knowledge_rag"
    assert result["is_relevant"] is True


def test_enterprise_case_detection():
    result = score_enterprise_relevance(rec("Customer story: Batteries Plus deployed 10 AI agents and increased sales results"))
    assert result["content_type"] == "enterprise_case"
    assert result["score"] >= 70


def test_pure_model_benchmark_is_downweighted():
    result = score_enterprise_relevance(rec("New model tops benchmark leaderboard with no enterprise deployment details"))
    assert result["score"] < 60
    assert result["is_relevant"] is False


def test_funding_news_is_downweighted():
    result = score_enterprise_relevance(rec("AI startup raised Series B funding at higher valuation"))
    assert result["score"] < 60
    assert result["is_relevant"] is False


def test_select_enterprise_headlines_caps_same_source():
    items = [
        add_enterprise_relevance_fields(rec(f"Agentforce sales agent CRM rollout case study {i}", source="Salesforce Blog / Agentforce"))
        for i in range(5)
    ]
    items += [
        add_enterprise_relevance_fields(rec("Intercom customer support agent improves resolution rate", source="Intercom AI & ML")),
        add_enterprise_relevance_fields(rec("Enterprise RAG knowledge base with permission filtering", source="Glean Blog")),
    ]
    picked = select_enterprise_headlines(items, datetime(2026, 7, 8, tzinfo=timezone.utc), limit=5, max_per_source=2)
    assert sum(1 for item in picked if item["source"] == "Salesforce Blog / Agentforce") <= 2


def test_select_enterprise_headlines_covers_three_topics_when_available():
    items = [
        add_enterprise_relevance_fields(rec("Agentforce sales agent CRM rollout case study", source="Salesforce")),
        add_enterprise_relevance_fields(rec("Intercom customer support agent improves resolution rate", source="Intercom")),
        add_enterprise_relevance_fields(rec("Enterprise RAG knowledge base with permission filtering", source="Glean")),
        add_enterprise_relevance_fields(rec("Workday employee service HR payroll assistant", source="Workday")),
    ]
    picked = select_enterprise_headlines(items, datetime(2026, 7, 8, tzinfo=timezone.utc), limit=4)
    assert len({item["enterprise_primary_topic"] for item in picked}) >= 3


def test_added_fields_preserve_ai_json_compatibility():
    out = add_enterprise_relevance_fields(rec("AI governance evaluation framework for enterprise rollout"))
    assert out["ai_score"] == 0.9
    assert out["ai_label"] == "ai_general"
    assert "enterprise_score" in out
    assert "enterprise_primary_topic" in out
    assert "enterprise_topics" in out
    assert "enterprise_content_type" in out
    assert "enterprise_reason" in out
    assert "enterprise_is_relevant" in out


def test_seo_agent_is_not_customer_service():
    result = score_enterprise_relevance(rec("Claude Fable 5 自主优化 AIHOT 网站 SEO/GEO 全记录"))
    assert result["primary_topic"] != "intelligent_customer_service"
    assert "intelligent_customer_service" not in result["topics"]


def test_ai_video_is_not_customer_service():
    result = score_enterprise_relevance(rec("AI视频没有真人感的问题，Seedance 2.0跑出来的假人比较"))
    assert result["primary_topic"] != "intelligent_customer_service"
    assert "intelligent_customer_service" not in result["topics"]


def test_image_generation_model_release_is_not_customer_service():
    result = score_enterprise_relevance(rec("New image generation model release improves prompt adherence"))
    assert result["primary_topic"] != "intelligent_customer_service"
    assert "intelligent_customer_service" not in result["topics"]


def test_generic_code_agent_is_not_customer_service():
    result = score_enterprise_relevance(rec("General code agent automates pull request generation for developers"))
    assert result["primary_topic"] != "intelligent_customer_service"
    assert "intelligent_customer_service" not in result["topics"]


def test_customer_service_ticket_handoff_positive():
    result = score_enterprise_relevance(rec("客服Agent自动处理工单并在失败时转人工"))
    assert result["primary_topic"] == "intelligent_customer_service"
    assert result["is_relevant"] is True


def test_contact_center_agent_assist_positive():
    result = score_enterprise_relevance(rec("Contact center agent assist reduces handling time"))
    assert result["primary_topic"] == "intelligent_customer_service"
    assert result["is_relevant"] is True


def test_customer_service_self_service_resolution_positive():
    result = score_enterprise_relevance(rec("AI customer service improves self-service resolution rate"))
    assert result["primary_topic"] == "intelligent_customer_service"
    assert result["is_relevant"] is True


def test_human_agent_customer_service_collaboration_positive():
    result = score_enterprise_relevance(rec("智能客服与人工坐席协同处理复杂问题"))
    assert result["primary_topic"] == "intelligent_customer_service"
    assert result["is_relevant"] is True


def test_hr_content_does_not_fall_into_customer_service():
    result = score_enterprise_relevance(rec("Workday AI HR Service Delivery improves employee service and payroll workflows"))
    assert result["primary_topic"] == "hr_ai"
    assert "intelligent_customer_service" not in result["topics"]


def test_crm_sales_content_does_not_fall_into_customer_service():
    result = score_enterprise_relevance(rec("Agentforce sales agent improves CRM lead qualification and account planning"))
    assert result["primary_topic"] == "sales_marketing_ai"
    assert "intelligent_customer_service" not in result["topics"]


def test_rag_support_word_does_not_fall_into_customer_service():
    result = score_enterprise_relevance(rec("Enterprise RAG knowledge base adds permission filtering to support internal policy search"))
    assert result["primary_topic"] == "enterprise_knowledge_rag"
    assert "intelligent_customer_service" not in result["topics"]


def test_primary_topic_can_be_none_without_strong_evidence():
    result = score_enterprise_relevance(rec("AI assistant improves general productivity with automation and better experience"))
    assert result["primary_topic"] is None
    assert result["topics"] == []
    assert result["is_relevant"] is False
