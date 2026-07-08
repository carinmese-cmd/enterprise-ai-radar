# 企业AI雷达V1第一阶段本地接入验证

## 1. 本次验证范围

验证时间：2026-07-08

本次只验证第一阶段7个信源的本地接入可行性，不启用生产抓取，不修改 GitHub Actions，不写入现有 `data` 目录。

复用原项目现有信源：

| 信源 | 处理方式 | 说明 |
| --- | --- | --- |
| OpenAI News | reuse_existing | 原项目已有官方来源覆盖，本次不写入企业AI OPML，避免重复抓取。 |
| Anthropic Newsroom | reuse_existing | 原项目已有官方来源覆盖，本次不写入企业AI OPML，避免重复抓取。 |
| InfoQ AI | reuse_existing | 原项目已有 InfoQ 相关来源覆盖，本次不写入企业AI OPML，避免重复抓取。 |

新增已验证 RSS：

| 信源 | RSS | 方向 |
| --- | --- | --- |
| Azure AI Foundry Blog | `https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=azure-ai-foundry-blog` | 模型、Agent、RAG、评测与治理 |
| Salesforce Blog / Agentforce | `https://www.salesforce.com/blog/feed/` | CRM、销售、客服、Agentforce |
| Intercom AI & ML | `https://www.intercom.com/blog/category/ai-ml/feed/` | AI客服、客户体验、人机协同 |
| OWASP GenAI Security Project | `https://genai.owasp.org/feed/` | GenAI安全、治理与风险 |

## 2. 现有 OPML 机制确认

项目当前已支持通过 `scripts/update_news.py --rss-opml <path> --rss-max-feeds <n>` 读取 OPML 中的 RSS。

OPML RSS 进入流水线后的来源字段：

| 字段 | 当前值 |
| --- | --- |
| `site_id` | `opmlrss` |
| `site_name` | `OPML RSS` |
| `source` | OPML 中每个 feed 的 `title` |
| `meta.feed_url` | 实际 RSS URL |
| `meta.feed_home` | OPML 中的 `htmlUrl` |

GitHub Actions 当前使用 `feeds/follow.opml`，该文件由 `FOLLOW_OPML_B64` secret 或 `feeds/follow.example.opml` 准备。本次没有修改工作流。

`feeds/follow.opml` 已在 `.gitignore` 中忽略。本次新增的是公开企业AI专用 OPML：`feeds/enterprise-ai-v1.opml`。

去重发生在所有来源抓取并进入时间窗口后：

1. 先生成全量窗口内容。
2. 再进行 AI 相关性筛选。
3. 对 AI 内容执行标题/URL 去重和近似标题抑制。
4. 再进行故事合并。

## 3. OPML 文件结构

`feeds/enterprise-ai-v1.opml` 只包含4个新增 RSS，没有包含 OpenAI、Anthropic 或 InfoQ。

分组如下：

| 分组 | Feed |
| --- | --- |
| 模型与技术平台 | Azure AI Foundry Blog |
| 市场拓展与销售 | Salesforce Blog / Agentforce |
| 智能客服 | Intercom AI & ML |
| 治理与安全 | OWASP GenAI Security Project |

离线校验结果：通过。OPML 可解析，正好4个 Feed，`xmlUrl` 唯一，无敏感信息。

## 4. RSS 联网读取结果

| 信源 | HTTP状态 | Feed条目数 | 最近7天条数 | 最新时间 | 内容匹配 |
| --- | ---: | ---: | ---: | --- | --- |
| Azure AI Foundry Blog | 200 | 20 | 2 | 2026-07-02 14:00:00 UTC | 匹配，聚焦 Foundry、Agent、企业控制面与评测 |
| Salesforce Blog / Agentforce | 200 | 10 | 10 | 2026-07-07 23:04:18 UTC | 部分匹配，包含 Agentforce/AI，也混有CRM、安全和经营主题 |
| Intercom AI & ML | 200 | 10 | 1 | 2026-07-01 16:44:49 UTC | 匹配，聚焦 AI 客服、客户体验和知识管理 |
| OWASP GenAI Security Project | 200 | 10 | 0 | 2026-05-14 01:05:44 UTC | 匹配但低频，适合治理安全专题，不适合按24小时热点判断 |

最近内容样本：

| 信源 | 样本标题 |
| --- | --- |
| Azure AI Foundry Blog | Introducing Kimi K2.7 Code in Microsoft Foundry |
| Azure AI Foundry Blog | Foundry Control Plane and Agent 365: Two Control Planes Walk Into an Enterprise |
| Azure AI Foundry Blog | Agent-to-Agent Communication: Connecting Foundry and LangGraph Agents via A2A |
| Salesforce Blog / Agentforce | Does Your Company Have an AI Accountability Problem? |
| Salesforce Blog / Agentforce | Selling With AI Agents? Here's What You Need to Know |
| Salesforce Blog / Agentforce | Your AI Agents, Any Cloud: Building the Agentic Enterprise with Agentforce and Amazon Agentcore |
| Intercom AI & ML | How to measure the customer experience as AI scales |
| OWASP GenAI Security Project | Memory Is a Feature. It Is Also an Attack Surface |

## 5. 完整流水线验证

执行方式：

```powershell
python scripts/update_news.py --output-dir .tmp/enterprise-ai-phase1-data --window-hours 168 --rss-opml feeds/enterprise-ai-v1.opml --rss-max-feeds 10
```

运行成功，并只写入临时目录 `.tmp/enterprise-ai-phase1-data`。

生成结果摘要：

| 指标 | 数量 |
| --- | ---: |
| OPML Feed 数 | 4 |
| OPML 成功 Feed 数 | 4 |
| OPML Feed 总抓取条目 | 50 |
| 168小时全量候选池 | 4585 |
| AI相关性筛选前 | 4585 |
| AI相关性筛选后、去重前 | 593 |
| AI相关性筛选后、去重后 | 566 |
| 全量模式去重后 | 4311 |
| 故事合并后 | 532 |
| 合并事件 | 34 |

4个新增 RSS 在168小时窗口内的结果：

| 信源 | 168小时窗口条数 | 进入AI池条数 | 全量去重后条数 | 说明 |
| --- | ---: | ---: | ---: | --- |
| Azure AI Foundry Blog | 3 | 3 | 3 | 全部通过 AI 相关性筛选 |
| Salesforce Blog / Agentforce | 10 | 4 | 10 | Feed 偏综合，6条未进入 AI 池 |
| Intercom AI & ML | 1 | 1 | 1 | 通过 AI 相关性筛选 |
| OWASP GenAI Security Project | 0 | 0 | 0 | Feed 有效，但最近7天无更新 |

## 6. 去重与重复风险

本次未发现新增 OPML 内容与现有 OpenAI、Anthropic、InfoQ 来源发生标题重复。

本次未发现同一文章因 URL 参数不同造成的 OPML 内重复。

当前 OPML RSS 的 Feed URL 没有发生替换，`source-status` 中4个 Feed 均为 `ok: true`，没有失败、跳过或零条 Feed。

## 7. 相关性筛选与内容噪声

| 信源 | 内容噪声 | 观察 |
| --- | --- | --- |
| Azure AI Foundry Blog | 低 | 与企业 AI 平台、Agent 和模型能力高度相关。 |
| Salesforce Blog / Agentforce | 中 | 综合博客包含部分非AI或弱AI内容，但 AI/Agentforce 内容价值高。 |
| Intercom AI & ML | 低 | 聚焦 AI 客服和客户体验，栏目匹配度高。 |
| OWASP GenAI Security Project | 低 | 内容高度匹配治理安全，但更新频率低。 |

没有发现中文乱码。Salesforce 标题中存在英文弯引号，属于正常字符。

## 8. 当前发现的问题

1. Salesforce 综合 Feed 噪声中等，正式接入后建议继续依赖 AI 相关性筛选，并在企业AI标签阶段重点识别 Agentforce、CRM、Sales、Service、Customer 等关键词。
2. OWASP GenAI Security Project 更新频率低，不适合按24小时热点判断；应进入治理安全栏目，并使用168小时或更长窗口。
3. 当前 OPML RSS 统一使用 `site_id=opmlrss`，正式接入后如果需要更细的来源统计，需要在后续阶段评估是否扩展来源元数据，但本阶段不修改抓取逻辑。

## 9. 是否适合进入正式接入

| 信源 | 建议 |
| --- | --- |
| Azure AI Foundry Blog | 建议进入正式自动更新 |
| Salesforce Blog / Agentforce | 建议进入正式自动更新，但保留噪声监控 |
| Intercom AI & ML | 建议进入正式自动更新 |
| OWASP GenAI Security Project | 建议进入正式自动更新，但不参与24小时热点判断 |

## 10. 下一步建议

1. 保持本次 OPML 文件作为公开、可审计的企业AI第一阶段 RSS 清单。
2. 下一阶段再决定是否把 `feeds/enterprise-ai-v1.opml` 接入正式更新流程。
3. 正式接入前不要重复添加 OpenAI、Anthropic 和 InfoQ。
4. 后续改造评分与标签时，应补充企业AI场景标签，避免企业落地案例被泛AI新闻规则低估。
