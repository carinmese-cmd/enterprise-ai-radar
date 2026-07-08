# 企业AI信源联网核验报告：第二批

核验时间：2026-07-07

## 一、核验方法

本批只核验 8 个公开官方页面和页面明示的公开 Feed，不登录账号，不使用 Cookie，不使用 API Key、Token 或付费接口，不绕过访问限制，也不批量扫描网站路径。

核验动作包括：

- 请求候选官方页面，记录 HTTP 状态码、跳转后的最终地址和页面状态。
- 检查页面是否为真实内容页，还是错误页、登录页、纯产品介绍页或 JavaScript 壳。
- 检查页面 HTML 中是否存在 RSS、Atom、`application/rss+xml`、`application/atom+xml` 或 `rel="alternate"`。
- 仅验证页面明示或官方页面明确链接出的公开 Feed。
- 对中文云厂商，补充查看同一官方域名下由页面明示的文档、产品动态、客户案例、新闻报道或公告入口。
- 对英文 SaaS 厂商，检查博客或产品页是否过宽，并记录内容噪声。

## 二、结果总览

| 信源 | 最终官方入口 | 页面状态 | Feed状态 | 内容噪声 | 现有覆盖 | 重复风险 | 推荐方式 | P0是否保留 | 结论 |
|---|---|---|---|---|---|---|---|---|---|
| 阿里云百炼 Model Studio | `https://www.alibabacloud.com/help/en/model-studio/model-release-notes` | 200，官方 Release Notes 可访问；原产品页落到 notfound | not_found | low | adapter_available | low | webpage_monitor | 是 | 原入口需替换；Release Notes 聚焦模型、API、价格和上下文变化 |
| 腾讯云智能体开发平台 ADP | `https://cloud.tencent.com/product/adp` | 200，产品页含动态和客户案例 | not_found | medium | adapter_available | low | webpage_monitor | 是 | 可监控产品动态和案例块，避免抓取营销区 |
| 火山引擎方舟 Ark | `https://www.volcengine.com/docs/82379/1159177` | 200，官方产品更新公告可访问；产品页脚本端只见 JavaScript 壳 | not_found | medium | adapter_available | low | webpage_monitor | 是 | 原产品页不适合作为主入口；产品更新公告更稳定 |
| 华为云 AgentArts | `https://www.huaweicloud.com/product/agentarts.html` | 200，产品页含案例、新闻报道、服务公告入口 | not_found | medium | adapter_available | low | webpage_monitor | 是 | 可做网页监控，但应定位公告/案例，不抓营销首屏 |
| ServiceNow AI | `https://www.servicenow.com/docs/r/release-notes/now-assist-rn-landing.html` | 200，官方 Now Assist and agentic AI release notes 可访问；原 AI 博客仍超时 | not_found | low | opml_ready | low | webpage_monitor | 是 | Release Notes 比博客专题更适合作为稳定企业 AI 产品更新源 |
| Salesforce Blog / Agentforce | `https://www.salesforce.com/blog/` | 200，跳转到带参数博客页 | verified | medium | opml_ready | low | rss | 是 | RSS 有效，AI/Agentforce 密度较高，但需过滤泛营销内容 |
| HubSpot AI | `https://www.hubspot.com/spotlight` | 200，官方 Product Updates / Spotlight 可访问，含 Breeze、Agent、Sales Hub、Service Hub 更新 | uncertain | medium | adapter_available | low | webpage_monitor | 是 | 案例 RSS 有效但过宽，优先监控 Spotlight |
| Glean Blog | `https://www.glean.com/blog` | 200，带日期博客列表 | not_found | low | opml_ready | low | webpage_monitor | 是 | 高匹配企业 AI/RAG/Agent，适合网页监控 |

## 三、已确认的有效 Feed

- Salesforce Blog：`https://www.salesforce.com/blog/feed/`

补充说明：HubSpot Case Studies 的 `https://www.hubspot.com/case-studies/rss.xml` 是有效 RSS，但它是宽泛客户案例 Feed，不是 HubSpot AI 或 Breeze AI 专属 Feed，本批标记为 `uncertain`，不建议直接作为首版自动源。

## 四、适合网页监控的来源

- 腾讯云智能体开发平台 ADP
- 阿里云百炼 Model Studio
- 火山引擎方舟 Ark
- 华为云 AgentArts
- ServiceNow AI
- HubSpot AI / Breeze AI Product Updates
- Glean Blog

这些页面没有发现可直接接入的专属 RSS/Atom，但页面中存在较稳定的产品动态、客户案例、产品更新或带日期文章列表。

## 五、产品首页不适合、但找到更合适官方栏目的来源

- 阿里云百炼 Model Studio：原 `https://www.alibabacloud.com/en/product/model-studio` 落到官方 notfound，官方 Release Notes `https://www.alibabacloud.com/help/en/model-studio/model-release-notes` 可访问并持续记录模型、API、价格和上下文能力变化。
- 火山引擎方舟 Ark：产品页脚本端只返回 JavaScript 壳，官方文档下的产品更新公告 `https://www.volcengine.com/docs/82379/1159177` 更适合作为长期监控入口。
- HubSpot AI：产品页更像 Breeze AI 总入口，页面明示的 `https://www.hubspot.com/spotlight` 更适合跟踪产品更新，但仍未发现专属 Feed。
- ServiceNow AI：原博客专题页当前环境下仍超时，官方 Now Assist and agentic AI Release Notes 更稳定。

## 六、内容噪声较高的来源

中等噪声来源：

- 腾讯云智能体开发平台 ADP
- 火山引擎方舟 Ark
- 华为云 AgentArts
- Salesforce Blog / Agentforce
- HubSpot AI

低噪声来源：

- 阿里云百炼 Model Studio
- ServiceNow AI
- Glean Blog

## 七、原项目已有覆盖的来源

本批 8 个来源均没有被原项目完整覆盖。覆盖状态延续上一轮映射：

- `adapter_available`：阿里云百炼、腾讯 ADP、火山方舟、华为 AgentArts、HubSpot AI
- `opml_ready`：ServiceNow AI、Salesforce Blog / Agentforce、Glean Blog

## 八、重复抓取风险

本批没有高重复风险来源。Salesforce、HubSpot 与 Glean 后续如果同时接入博客、案例和产品更新页，可能产生主题内重复，需要在正式接入前做来源重叠检查。

## 九、最终推荐方式

- 阿里云百炼 Model Studio：`webpage_monitor`
- 腾讯云智能体开发平台 ADP：`webpage_monitor`
- 火山引擎方舟 Ark：`webpage_monitor`
- 华为云 AgentArts：`webpage_monitor`
- ServiceNow AI：`webpage_monitor`
- Salesforce Blog / Agentforce：`rss`
- HubSpot AI：`webpage_monitor`
- Glean Blog：`webpage_monitor`

## 十、是否仍建议保留为 P0

建议保留 P0：

- 阿里云百炼 Model Studio
- 腾讯云智能体开发平台 ADP
- 火山引擎方舟 Ark
- 华为云 AgentArts
- ServiceNow AI
- Salesforce Blog / Agentforce
- HubSpot AI
- Glean Blog

本批不建议降为 P1。此前需要复核的阿里云、火山和 ServiceNow 均已找到更合适的官方更新入口。

## 十一、后续建议

1. 不要把阿里云、火山、HubSpot 的当前产品首页直接启用为生产抓取源，优先使用本批补充核验得到的更新类入口。
2. Salesforce 可进入下一步 RSS 重叠检查，但必须加 AI/Agentforce/CRM 主题过滤。
3. Glean Blog 是本批最适合网页监控的来源，建议优先验证网页结构稳定性。
4. 腾讯 ADP 和华为 AgentArts 应分别锁定产品动态、服务公告、客户案例区域，避免抓取营销首屏。
5. ServiceNow 原 AI 博客专题页可后续重试，但首版可优先验证 Now Assist and agentic AI Release Notes 的网页结构稳定性。
