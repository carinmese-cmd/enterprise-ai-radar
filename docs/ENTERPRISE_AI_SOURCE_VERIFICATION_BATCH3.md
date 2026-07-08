# 企业AI信源联网核验报告：第三批

核验时间：2026-07-08

## 一、核验方法

本批只核验 8 个公开官方页面和页面明示的公开 Feed，不登录账号，不使用 Cookie，不使用 API Key、Token 或付费接口，不绕过访问限制，也不批量扫描网站路径。

核验动作包括：

- 请求候选官方页面，记录 HTTP 状态码、跳转后的最终地址和页面状态。
- 检查页面是否为真实内容页、报告页、项目页、错误页或访问受限页。
- 检查页面 HTML 中是否存在 RSS、Atom、`application/rss+xml`、`application/atom+xml` 或 `rel="alternate"`。
- 仅验证页面明示的公开 Feed。
- 对低频研究、标准和报告类来源，判断其是否应进入 30 天报告池或治理专题，而不是 24 小时新闻排序。

## 二、结果总览

| 信源 | 最终官方入口 | 页面状态 | Feed状态 | 更新频率 | 内容噪声 | 现有覆盖 | 重复风险 | 推荐方式 | 推荐时间窗口 | P0是否保留 | 结论 |
|---|---|---|---|---|---|---|---|---|---:|---|---|
| Zendesk AI Blog | `https://www.zendesk.com/blog/tag/ai/` | 200，原分类页跳转到 AI tag 页 | not_found | weekly | medium | opml_ready | low | webpage_monitor | 72 | 是 | 可监控 AI 客服、AI Agent、Copilot 与质量管理内容 |
| Intercom AI & ML | `https://www.intercom.com/blog/category/ai-ml/` | 200，AI 分类博客页 | verified | weekly | low | opml_ready | low | rss | 72 | 是 | 分类 RSS 有效，内容高度匹配客服与销售 Agent |
| Atlassian AI / Rovo | `https://www.atlassian.com/blog` | 200，候选 AI URL 跳转到综合博客 | invalid | weekly | medium | opml_ready | low | webpage_monitor | 72 | 是 | Feed 声明返回 HTML，需监控 AI/Rovo 区块而非综合博客 RSS |
| McKinsey State of AI | `https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai` | 脚本客户端超时 | uncertain | low_frequency | low | manual_only | low | manual_review | 720 | 是 | 低频高价值研究源，进入深度报告流程 |
| Deloitte State of AI in the Enterprise | `https://www.deloitte.com/us/en/what-we-do/capabilities/applied-artificial-intelligence/content/state-of-ai-in-the-enterprise.html` | 200，报告页 | not_found | low_frequency | low | manual_only | low | manual_review | 720 | 是 | 企业 AI 采用与治理报告，适合深度报告，不参与日常热点排序 |
| 中国信通院专题报告 | `https://www.caict.ac.cn/kxyj/qwfb/ztbg/` | 412，脚本客户端访问受限 | blocked | low_frequency | low | manual_only | low | manual_review | 720 | 是 | 进入“国内政策、标准与深度报告”栏目，不参与 24 小时热点排序 |
| NIST AI RMF | `https://www.nist.gov/itl/ai-risk-management-framework` | 200，治理框架页 | not_found | low_frequency | low | manual_only | low | webpage_monitor | 720 | 是 | 稳定治理参考页，适合治理专题和低频网页监控 |
| OWASP GenAI Security Project | `https://genai.owasp.org/` | 200，项目页 | verified | irregular | low | adapter_available | low | rss | 168 | 是 | RSS 有效，适合治理、安全与 Agent 风险专题 |

## 三、已确认的有效 Feed

- Intercom AI & Automation Category Feed：`https://www.intercom.com/blog/category/ai-ml/feed/`
- OWASP GenAI Security Project Feed：`https://genai.owasp.org/feed/`

Atlassian 页面声明了 `https://www.atlassian.com/blog/feed`，但本次请求返回 HTML 页面，无法解析为 RSS，因此标记为 `invalid`，不作为有效 Feed。

## 四、适合网页监控的来源

- Zendesk AI Blog
- Atlassian AI / Rovo
- NIST AI Risk Management Framework

Zendesk 和 Atlassian 适合 72 小时窗口；NIST 是低频治理参考源，适合 720 小时窗口。

## 五、适合 GitHub Release 的来源

本批没有来源推荐 `github_release`。OWASP 当前官方项目页已提供 RSS，优先使用 RSS，而不是另行转向 GitHub Release。

## 六、需要人工审核的来源

- McKinsey State of AI
- Deloitte State of AI in the Enterprise
- 中国信通院专题报告

这些来源更像报告、白皮书或政策研究材料，适合人工摘要、证据归档和深度报告，不应直接进入 24 小时新闻排序。McKinsey 进入“深度报告”栏目；中国信通院进入“国内政策、标准与深度报告”栏目。

## 七、低频高价值来源

- McKinsey State of AI
- Deloitte State of AI in the Enterprise
- 中国信通院专题报告
- NIST AI Risk Management Framework

建议统一进入 30 天报告池或治理专题。

## 八、内容噪声较高的来源

本批没有 `high` 噪声来源。

中等噪声来源：

- Zendesk AI Blog
- Atlassian AI / Rovo

低噪声来源：

- Intercom AI & ML
- McKinsey State of AI
- Deloitte State of AI in the Enterprise
- 中国信通院专题报告
- NIST AI RMF
- OWASP GenAI Security Project

## 九、原项目已有覆盖的来源

本批没有原项目完整覆盖的来源。

- `opml_ready`：Zendesk AI Blog、Intercom AI & ML、Atlassian AI / Rovo
- `manual_only`：McKinsey、Deloitte、中国信通院、NIST
- `adapter_available`：OWASP GenAI Security Project

## 十、重复抓取风险

本批没有高重复风险来源。后续如果同时接入 Atlassian 综合博客和 Rovo/AI 专题页面，需要做重叠检查。

## 十一、最终推荐方式

- Zendesk AI Blog：`webpage_monitor`
- Intercom AI & ML：`rss`
- Atlassian AI / Rovo：`webpage_monitor`
- McKinsey State of AI：`manual_review`
- Deloitte State of AI in the Enterprise：`manual_review`
- 中国信通院专题报告：`manual_review`
- NIST AI RMF：`webpage_monitor`
- OWASP GenAI Security Project：`rss`

## 十二、是否仍建议保留 P0

建议保留 P0：

- Zendesk AI Blog
- Intercom AI & ML
- Atlassian AI / Rovo
- McKinsey State of AI
- Deloitte State of AI in the Enterprise
- 中国信通院专题报告
- NIST AI RMF
- OWASP GenAI Security Project

说明：McKinsey、Deloitte、信通院和 NIST 的 P0 含义是高价值战略、报告或治理源，不代表进入 24 小时热点排序。

## 十三、推荐时间窗口

- 72 小时：Zendesk、Intercom、Atlassian
- 168 小时：OWASP GenAI Security Project
- 720 小时：McKinsey、Deloitte、中国信通院、NIST
