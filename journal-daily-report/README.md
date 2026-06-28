# 学术期刊日报生成器

帮你追踪 Nature、Science、NEJM、JPSP 等 200+ 高影响力学术期刊的最新目录，或针对具体问题进行领域扫描。

## 功能

- **期刊追踪模式**：查看特定期刊最新一期的完整目录
- **领域扫描模式**：在指定期刊范围内搜索特定主题的文章

## 两种模式

### 模式 A：期刊追踪
> "Nature 最新一期发了什么？"

追踪你关注的期刊，查看每一期的完整目录。适合：
- 关注 Nature、Science 等综合顶刊，追踪科研前沿风向标
- 关注 JPSP、Psychological Bulletin 等学科顶刊，掌握领域动态
- 跟踪 Nature Mental Health 等新刊，了解新兴方向

### 模式 B：领域扫描
> "心理学期刊上有没有关于情绪调节的新研究？"

在你信任的高质量期刊中搜索特定主题。适合：
- 只关注高质量期刊的研究者
- 需要快速了解某主题在顶刊中的研究现状
- 准备文献综述或课题调研

## 数据源

本 skill 使用多个学术数据源，自动路由到最佳数据源：

| 数据源 | 优势领域 | 特点 |
|--------|---------|------|
| **OpenAlex** | 综合 | 覆盖最广，有影响力指标（2-year mean citedness） |
| **PubMed** | 医学/心理/生物 | 最权威，生物医学领域必用 |
| **Crossref** | 所有DOI注册期刊 | DOI元数据完整 |
| **Semantic Scholar** | AI/CS/工程 | AI领域覆盖好 |

## 支持的期刊

预置 **200+ 高影响力期刊**，覆盖 20+ 学科领域：

- **综合性顶刊**：Nature, Science, PNAS, Nature Communications...
- **医学**：NEJM, The Lancet, JAMA, BMJ, Nature Medicine...
- **心理学**：Nature Mental Health, Psychological Bulletin, JPSP...
- **神经科学**：Nature Neuroscience, Neuron, Journal of Neuroscience...
- **AI/CS**：Nature Machine Intelligence, IEEE TPAMI, JMLR...
- **物理学**：Physical Review Letters, Nature Physics...
- **化学**：JACS, Nature Chemistry, Angewandte Chemie...
- **生物学**：Nature Biotechnology, Nature Cell Biology...
- **经济学**：American Economic Review, QJE...
- **教育学**：Review of Educational Research...
- **环境科学**：Nature Climate Change, Nature Sustainability...
- **更多...**

完整列表见 `期刊目录.md`，用户可自行添加关注的期刊。

## 报告格式

每篇论文提供三层解读：

- **📝 中文摘要**：面向学者，3-5 句学术中文
- **💬 通俗解读**：面向非专业读者，2-3 句大白话
- **🔎 点评**：亮点 + 局限，各 1-2 句

## 支持平台

支持所有主流 agent 平台：
- AutoClaw（速度最快）
- Claude Code 搭配国产模型平替（内容质量最佳）
- Trae（完全免费）

## 文件说明

| 文件 | 用途 |
|------|------|
| `SKILL.md` | 主 prompt，导入到 AI 工具中使用 |
| `期刊目录.md` | 预置期刊列表，按学科分组，可自定义 |
| `使用指南.md` | 各平台操作步骤 |
| `README.md` | 项目说明（本文件） |

## 快速开始

详见 [使用指南](./使用指南.md)

## 与 arXiv 日报的区别

| 特性 | arXiv 日报 | 期刊日报 |
|------|-----------|---------|
| 数据来源 | arXiv 预印本 | 正式发表期刊 |
| 核心模式 | 按分类/关键词搜索 | 按期刊追踪 + 领域扫描 |
| 适用场景 | 跟踪最新预印本 | 跟踪正式发表的高影响力研究 |
| 精选策略 | 大海捞针式精选 | 期刊目录式全览 |

## License

MIT

## 作者

山野的云，清华大学心理学系博士生
