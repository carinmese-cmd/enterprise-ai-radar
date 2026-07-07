# 企业AI雷达首版信源台账

## 当前状态说明

本台账记录企业AI落地雷达V1的24个P0候选信源。它们目前只是候选清单，不参与生产抓取，不改变现有AI News Radar的抓取逻辑、评分逻辑、页面展示或GitHub Actions。

当前机器可读配置位于 `config/enterprise_ai_sources.json`。所有候选源均保持：

- `enabled: false`
- `feed_url: null`
- `feed_status: pending_verification`
- `verification_status: pending`

## 24个P0信源分类汇总

| 分类 | 数量 | 信源 |
| --- | ---: | --- |
| 模型与基础平台 | 10 | OpenAI News, Anthropic Newsroom, Google Cloud AI & Machine Learning Blog, Microsoft 365 Copilot Release Notes, Azure AI Foundry Blog, DeepSeek API News, 阿里云百炼 Model Studio, 腾讯云智能体开发平台 ADP, 火山引擎方舟 Ark, 华为云 AgentArts |
| 人力资源与员工服务 | 2 | Workday AI, ServiceNow AI |
| 市场拓展与销售 | 2 | Salesforce Blog / Agentforce, HubSpot AI |
| 智能客服与人机协同 | 2 | Zendesk AI Blog, Intercom AI & ML |
| 企业知识库与RAG | 2 | Glean Blog, Atlassian AI / Rovo |
| 企业AI战略与研究 | 4 | McKinsey State of AI, Deloitte State of AI in the Enterprise, 中国信通院专题报告, InfoQ AI |
| AI应用评估与治理 | 2 | NIST AI Risk Management Framework, OWASP GenAI Security Project |

## 每类信源的用途

### 模型与基础平台

用于确认模型、API、Agent平台、RAG、评测、治理、价格、上下文、权限、连接器和企业部署能力变化。这类来源承担基础事实和技术选型输入。

### 人力资源与员工服务

用于观察HR Agent、员工服务、假勤、薪酬、人才管理、工作流和服务台场景。这类来源承担企业AI业务场景输入。

### 市场拓展与销售

用于观察CRM、营销、销售助手、客户数据、客服Agent和销售/营销自动化效果。这类来源帮助判断市场拓展与销售AI的产品能力和案例信号。

### 智能客服与人机协同

用于观察AI客服、人工兜底、解决率、质量评估、内容设计和系统操作能力。这类来源直接服务客户服务场景和人机协同设计。

### 企业知识库与RAG

用于观察企业搜索、知识图谱、权限、知识连接、工作流和Agent能力。这类来源服务企业知识库、RAG和智能体建设。

### 企业AI战略与研究

用于观察企业采用、组织机制、规模化路径、投资重点、治理挑战、国内路线和行业研究。这类来源更适合进入30天深度池。

### AI应用评估与治理

用于观察AI风险管理、安全治理、提示词注入、数据泄露、过度授权和Agent安全。这类来源为企业AI应用评估、权限控制和安全治理提供依据。

## feed_url为空的原因

当前阶段不猜测、不虚构RSS地址，也不因为网页看起来可能存在Feed就直接写入。

所有 `feed_url` 统一为 `null`，表示后续需要逐项核验是否存在稳定RSS、Atom、公开Feed、Changelog、Release、结构化页面或可维护的网页监控方式。

## enabled为false的原因

所有 `enabled` 统一为 `false`，因为这些来源尚未完成以下核验：

1. 是否有稳定、公开、可长期维护的入口。
2. 是否有可用发布时间或可靠排序。
3. 是否需要Cookie、Token、付费接口或账号登录。
4. 是否会产生过多噪声。
5. 是否能映射到企业AI落地雷达的栏目、证据等级和时间窗口。
6. 是否适合进入生产抓取，还是只适合人工补充或半自动处理。

## 后续核验步骤

1. 逐项打开官方入口，确认页面是否可公开访问。
2. 查找官方RSS、Atom、Changelog、Release或结构化更新页。
3. 不使用猜测的RSS地址；所有Feed必须实测可读。
4. 记录更新时间、发布时间字段、标题质量、正文摘要和来源稳定性。
5. 判断自动化等级：L1、L2或L3。
6. 判断证据等级：A、B、C或D。
7. 判断噪声类型和必要过滤词。
8. 小样本运行离线或临时探测，确认不会污染现有数据池。
9. 通过评审后再把 `feed_url`、`feed_status`、`verification_status` 和 `enabled` 调整到可接入状态。

## 接入前限制

核验完成前，不能直接接入生产抓取。

当前配置只能作为企业AI雷达首版信源台账和后续核验任务清单，不应被现有 `scripts/update_news.py` 自动读取或生产使用。

## 社交平台后续配置

微信公众号、小红书和抖音暂时不写入 `config/enterprise_ai_sources.json`。

后续应使用独立配置管理社交平台来源，并区分：

1. 公众号深度案例源
2. 小红书产品体验和早期弱信号
3. 抖音产品演示、访谈和会议现场
4. 人工提交、付费API、授权接口和临时案例

社交平台内容不能未经验证直接作为正式事实依据，也不能在公开仓库保存Cookie、Token、私人订阅、邮箱正文或付费订阅内容。
