# 企业AI信源联网核验报告：第一批

核验时间：2026-07-07

## 一、核验方法

本批只核验 8 个公开页面和公开 Feed，不登录账号，不使用 Cookie，不使用密钥或付费接口，不绕过访问限制。

核验动作包括：

- 请求候选官方页面，记录 HTTP 状态码、跳转后的最终地址和页面可访问性。
- 检查页面 HTML 中是否存在 RSS、Atom、`application/rss+xml`、`application/atom+xml`、`rel="alternate"` 或明确的 feed 链接。
- 仅验证页面明示链接或原项目已经配置过的公开 Feed。
- 使用 XML 解析确认 Feed 是否为有效 RSS/Atom、是否至少包含 1 条内容、是否能解析标题和链接。
- 对照 `config/enterprise_ai_source_mapping.json` 判断原项目覆盖关系和重复抓取风险。

## 二、结果总览

| 信源 | 页面状态 | Feed状态 | 现有覆盖 | 重复风险 | 推荐方式 | 结论 |
|---|---|---|---|---|---|---|
| OpenAI News | 403，脚本客户端被拒；RSS 可访问 | verified | existing_exact | high | reuse_existing | 复用原项目 OpenAI RSS，不新增企业源 |
| Anthropic Newsroom | 200 | not_found | existing_exact | high | reuse_existing | 复用原项目 Anthropic 页面适配器 |
| Google Cloud AI & Machine Learning Blog | 200 | not_found | existing_partial | medium | webpage_monitor | 未发现公开 Feed，建议后续做网页监控核验 |
| Microsoft 365 Copilot Release Notes | 200 | not_found | existing_partial | medium | webpage_monitor | Microsoft 现有 Feed 过宽，不等同于 Copilot Release Notes |
| InfoQ AI | 200 | uncertain | existing_partial | high | reuse_existing | 全站 Feed 有效但不是 AI 主题专属，先复用现有覆盖并做去重 |
| DeepSeek API News | 200 | not_found | existing_partial | low | webpage_monitor | 原候选 `/news` 已确认 404；官方 API 文档 Change Log 为 `/updates`，未发现 RSS/Atom |
| Azure AI Foundry Blog | 200 | verified | opml_ready | low | rss | 页面明示 RSS 可用，适合进入后续 OPML/默认源评估 |
| Workday AI | 200 | not_found | opml_ready | low | webpage_monitor | 未发现公开 Feed，建议网页监控或人工复核 |

## 三、已确认可用 Feed

- OpenAI News：`https://openai.com/news/rss.xml`
- Azure AI Foundry Blog：`https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=azure-ai-foundry-blog`

说明：InfoQ 的 `https://www.infoq.cn/feed` 是有效公开 Feed，但它是全站 Feed，不是本批候选的 AI 主题页专属 Feed，因此本批标记为 `uncertain`，不计入已确认可用的候选栏目 Feed。

## 四、没有 Feed 但适合网页监控的来源

- Google Cloud AI & Machine Learning Blog
- Microsoft 365 Copilot Release Notes
- Workday AI

这三类页面均可公开访问，但本批未发现页面声明的 RSS/Atom Feed。后续如果进入自动化，应优先做小范围网页监控原型，确认页面是否有稳定时间戳、标题链接和可重复解析结构。

## 五、建议复用原项目现有配置的来源

- OpenAI News：原项目已有官方 RSS，重复接入风险高。
- Anthropic Newsroom：原项目已有同 URL 页面适配器，重复接入风险高。
- InfoQ AI：原项目已有 InfoQ 全站 Feed，单独接入 AI 主题页前需要先做重叠评估。

## 六、不建议首版自动接入的来源

- 本批暂无。DeepSeek 原候选 URL 当前返回 404，但已确认官方 API 文档 Change Log 为 `https://api-docs.deepseek.com/updates`；因未发现 RSS/Atom，首版不直接启用生产抓取，应先做网页监控稳定性验证。

## 七、重复抓取风险

高风险：

- OpenAI News
- Anthropic Newsroom
- InfoQ AI

中风险：

- Google Cloud AI & Machine Learning Blog
- Microsoft 365 Copilot Release Notes

低风险：

- DeepSeek API News
- Azure AI Foundry Blog
- Workday AI

## 八、下一步建议

1. 第一优先复用 OpenAI、Anthropic、InfoQ 的现有覆盖，不新增重复源。
2. 将 Azure AI Foundry Blog 放入下一批候选接入评估，先用 OPML 或独立测试源验证噪声和去重。
3. 对 Google Cloud AI Blog、Microsoft 365 Copilot Release Notes、Workday AI 做网页结构稳定性核验。
4. 对 DeepSeek 官方 API Change Log 做网页结构稳定性核验，确认标题、日期和链接是否可稳定抽取。
5. 在生产配置启用任何新源之前，先运行来源重叠检查，避免把同一厂商的广义新闻、产品博客和 release notes 重复推给前端。
