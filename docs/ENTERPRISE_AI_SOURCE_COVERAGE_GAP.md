# 企业AI候选信源覆盖对照与缺口分析

## 1. 当前原项目信源机制概览

原项目的信源机制以 `scripts/update_news.py` 为核心，主要包括：

1. 内置官方AI来源：`OFFICIAL_AI_FEEDS` 和 `fetch_official_ai_updates()`，覆盖 OpenAI News、Google DeepMind、Google AI Blog、Hugging Face、GitHub AI/Changelog、OpenAI Skills，以及 Anthropic News 页面适配器。
2. 内置精选媒体和聚合源：`CURATED_AI_MEDIA_FEEDS`、AI Breakfast、Follow Builders、TechURLs、Buzzing、Iris、BestBlogs、TopHub、Zeli、Hacker News Algolia、AI HubToday、AIbase、AI HOT、NewsNow。
3. 通用OPML/RSS接入：`fetch_opml_rss()` 可读取 `feeds/follow.opml`，GitHub Actions 支持通过 `FOLLOW_OPML_B64` 注入私有OPML。
4. 高级源框架：AgentMail、X API、SocialData、TikHub 均为可选高级源，默认不应启用。
5. 测试覆盖：`tests/test_topic_filter.py` 覆盖 Anthropic、OpenAI Codex Changelog、AI HOT、AI HubToday、OPML和高级源默认关闭等行为。

本次分析只对照本地代码、配置、文档和测试，不访问互联网，不验证任何新的RSS地址。

## 2. 24个候选信源覆盖统计

| 覆盖状态 | 数量 | 说明 |
| --- | ---: | --- |
| existing_exact | 2 | 原项目已有完全对应或同URL来源 |
| existing_partial | 4 | 原项目有相关来源，但地址、栏目或内容范围不同 |
| adapter_available | 6 | 原项目已有静态页/自定义抓取器模式，但该信源未配置 |
| opml_ready | 8 | 适合先核验Feed后通过OPML观察，但当前未配置 |
| not_covered | 0 | 本轮没有使用该状态；多数未覆盖源仍可走OPML、适配器或人工路径 |
| manual_only | 4 | 更适合报告、治理框架或低频人工/半自动处理 |

## 3. 已完整覆盖的信源

1. OpenAI News
   - 依据：`scripts/update_news.py:83`、`feeds/follow.example.opml:9`、`docs/SOURCE_COVERAGE.md:68`
   - 风险：重复抓取风险高。已有内置RSS和示例OPML，后续不要直接新增同源抓取。

2. Anthropic Newsroom
   - 依据：`scripts/update_news.py:1417`、`scripts/update_news.py:1453`、`scripts/update_news.py:1692`、`tests/test_topic_filter.py:285`
   - 风险：重复抓取风险高。已有同URL页面适配器。

## 4. 部分覆盖的信源

1. Google Cloud AI & Machine Learning Blog
   - 原项目覆盖 Google DeepMind 和 Google AI Blog，但未覆盖 Google Cloud AI & Machine Learning Blog。
   - 依据：`scripts/update_news.py:88`、`scripts/update_news.py:93`、`docs/SOURCE_COVERAGE.md:70`

2. Microsoft 365 Copilot Release Notes
   - 原项目示例OPML有 Microsoft AI Blog，但不是 Microsoft 365 Copilot Release Notes。
   - 依据：`feeds/follow.example.opml:37`、`docs/SOURCE_COVERAGE.md:194`

3. DeepSeek API News
   - 原项目有 DeepSeek 关键词和讨论源搜索，但没有官方 DeepSeek API News 源。
   - 依据：`scripts/update_news.py:193`、`scripts/update_news.py:215`、`scripts/ai_relevance.py:26`

4. InfoQ AI
   - 原项目示例OPML有 broad InfoQ CN feed 和 replacement rule，但不是 `/topic/AI`。
   - 依据：`feeds/follow.example.opml:53`、`scripts/update_news.py:53`、`docs/SOURCE_COVERAGE.md:196`

## 5. 可通过OPML接入的信源

这些来源当前没有配置，但项目已有通用OPML能力。下一步只能核验是否存在稳定公开Feed，不能猜测Feed地址。

1. Azure AI Foundry Blog
2. Workday AI
3. ServiceNow AI
4. Salesforce Blog / Agentforce
5. Zendesk AI Blog
6. Intercom AI & ML
7. Glean Blog
8. Atlassian AI / Rovo

依据：`scripts/update_news.py:2506`、`docs/SOURCE_COVERAGE.md:40`、`.github/workflows/update-news.yml:43`

## 6. 需要新增网页适配器的信源

这些来源更像产品页、专题页或项目页。若核验后没有稳定Feed，但页面公开、结构稳定、带时间信息，才考虑新增适配器。

1. 阿里云百炼 Model Studio
2. 腾讯云智能体开发平台 ADP
3. 火山引擎方舟 Ark
4. 华为云 AgentArts
5. HubSpot AI
6. OWASP GenAI Security Project

依据：项目文档明确支持通过 `fetch_*` 新增公共JSON/静态页适配器，见 `docs/SOURCE_COVERAGE.md:44`、`docs/SOURCE_COVERAGE.md:47`、`docs/SOURCE_COVERAGE.md:242`。

## 7. 只能人工或半自动处理的信源

这些来源属于报告、框架、治理或低频深度资料。V1应先走30天池和人工复核，不应直接接入24小时生产抓取。

1. McKinsey State of AI
2. Deloitte State of AI in the Enterprise
3. 中国信通院专题报告
4. NIST AI Risk Management Framework

依据：`docs/ENTERPRISE_AI_SOURCE_PLAN.md` 已将报告、白皮书、治理文件和深度研究放入30天池，并将PDF、会议、视频和临时案例列为人工补充路径。

## 8. 可能重复抓取的风险

高风险：

1. OpenAI News
   - 已有内置RSS和示例OPML。
2. Anthropic Newsroom
   - 已有同URL页面适配器。
3. InfoQ AI
   - 已有 broad InfoQ CN feed，如果再加入AI topic，可能重复。

中风险：

1. Google Cloud AI & Machine Learning Blog
   - 可能与 Google AI Blog、DeepMind 或聚合源发生主题重叠。
2. Microsoft 365 Copilot Release Notes
   - 可能与 Microsoft AI Blog、GitHub Changelog 或聚合源发生主题重叠。

其余候选源当前没有明显本地重复抓取风险，但接入前仍需做 Source Overlap Check。

## 9. 建议的后续核验批次

### 第一批：原项目已覆盖或疑似覆盖的官方源

1. OpenAI News
2. Anthropic Newsroom
3. Google Cloud AI & Machine Learning Blog
4. Microsoft 365 Copilot Release Notes
5. InfoQ AI

目标：确认复用、去重和企业栏目映射，不急于新增抓取。

### 第二批：可能存在RSS或Atom的官方博客

1. Azure AI Foundry Blog
2. Workday AI
3. ServiceNow AI
4. Salesforce Blog / Agentforce
5. Zendesk AI Blog
6. Intercom AI & ML
7. Glean Blog
8. Atlassian AI / Rovo

目标：只核验官方Feed，不猜测地址；通过临时OPML观察样本质量。

### 第三批：只有产品页、报告页或专题页的来源

1. DeepSeek API News
2. HubSpot AI
3. McKinsey State of AI
4. Deloitte State of AI in the Enterprise
5. NIST AI Risk Management Framework
6. OWASP GenAI Security Project

目标：判断是否有稳定发布时间、是否适合30天池或人工复核。

### 第四批：国内平台和需要半自动接入的来源

1. 阿里云百炼 Model Studio
2. 腾讯云智能体开发平台 ADP
3. 火山引擎方舟 Ark
4. 华为云 AgentArts
5. 中国信通院专题报告

目标：优先寻找官方公告、文档更新、案例页或报告列表；不依赖Cookie、Token或非公开接口。
