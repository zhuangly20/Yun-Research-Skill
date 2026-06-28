---
name: journal-daily-report
description: 生成学术期刊目录日报或针对具体问题进行领域扫描。当用户提到"期刊日报"、"Nature最新"、"Science最新"、"期刊追踪"、"最新一期"、"journal daily"、"论文速递"、"帮我看看Nature最近发了什么"、"心理学期刊有什么新文章"、"在XX期刊找关于XX的文章"等涉及期刊/论文检索的问题时自动触发。支持 Nature、Science、NEJM、JPSP 等 200+ 高影响力期刊，用户可自定义关注期刊列表。
---

# 学术期刊日报生成器

## 触发判断

触发后，首先判断用户请求属于以下哪种模式：

### 模式 A：期刊追踪模式
用户想查看**特定期刊**最新一期的完整目录。

**触发示例：**
- "Nature 最新一期发了什么"
- "帮我看看 Science 最近的文章"
- "JPSP 最新目录"
- "NEJM 这周有什么新文章"
- "心理学期刊最近有什么"（使用学科组）

**特征：** 用户关注的是**期刊本身**，想看它最近发了什么。

### 模式 B：领域扫描模式
用户有一个**具体问题或主题**，想在指定的期刊范围内搜索相关文章。

**触发示例：**
- "Nature 上有没有关于 AI+教育的文章"
- "心理学期刊最近有没有关于情绪调节的研究"
- "在 Nature 和 Science 上找关于气候变化的论文"
- "JPSP 最近有没有关于社会认知的文章"

**特征：** 用户关注的是**某个主题**，但只在你信任的高质量期刊里找。

---

## 工作流程

### 第一步：判断模式 & 呈现期刊确认单（触发后立即呈现）

> ⛔ **STOP POINT — 展示确认单后必须停止，等待用户回复"确认"或"开始"后才能进入第二步。禁止在用户确认前执行任何 API 调用。**

**1. 判断模式：** 根据上述规则，判断当前请求是「模式 A」还是「模式 B」。

**2. 确定期刊范围：**
- 模式 A：用户指定的期刊，或学科组内的所有期刊
- 模式 B：用户指定的期刊范围，默认使用学科组

**3. 呈现期刊确认表：**

```
📋 期刊日报参数确认

📢 请求模式：{模式 A：期刊追踪 / 模式 B：领域扫描}
🎯 检索主题：{仅模式 B 显示}

📰 目标期刊：
1. {期刊名} (IF: {影响力指标})
2. {期刊名} (IF: {影响力指标})
3. {期刊名} (IF: {影响力指标})
...

📅 时间范围：<默认值>
🔢 每期文章数上限：<默认值>
📁 输出位置：<默认值>

如需修改期刊列表，直接告诉我；没问题的话回复"确认"或"开始"。
```

> ⛔ **再次强调：必须等到用户确认后才能开始搜索。不要在同一条回复中既展示确认单又执行搜索。**

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 时间范围 | 最近 7 天（模式 A）/ 最近 30 天（模式 B） | 支持：最近3天、最近一周、最近一个月、具体日期范围 |
| 每期文章数上限 | 20 | 模式 A 展示每刊最多 N 篇文章 |
| 输出位置 | 桌面 期刊日报/ | 支持任意路径，自动创建目录 |

**期刊选择规则：**
- 用户直接指定期刊名 → 使用指定期刊
- 用户提到学科组（如"心理学期刊"）→ 使用 `期刊目录.md` 中对应学科组的所有期刊
- 用户未指定 → 询问用户要查看哪些期刊或学科组

**关于影响力指标（IF）的展示：**
- 优先使用 OpenAlex 的 **2-year mean citedness**（类似影响因子）
- 如果 OpenAlex 无数据，展示引用数或标注"暂无"
- 用户可要求隐藏影响力指标

---

### 第二步：获取期刊数据（确认后执行）

根据期刊的数据源配置，使用对应的 API 获取最新文章列表。

#### 数据源路由策略

```
用户请求
   │
   ├─ 期刊配置为 PubMed 主数据源 ──→ PubMed API
   │
   ├─ 期刊配置为 Semantic Scholar ──→ Semantic Scholar API
   │
   ├─ 期刊配置为 Crossref ──→ Crossref API
   │
   └─ 默认（OpenAlex） ──→ OpenAlex API
```

#### API 调用方式

**1. OpenAlex API（默认，综合 + 影响力指标）**

```
# 按 ISSN 查询，按出版日期排序
GET https://api.openalex.org/works
  ?filter=primary_location.source.issn:{ISSN},from_publication_date:{起始日期}
  &sort=publication_date:desc
  &per_page=50
  &select=id,title,authorships,publication_date,doi,primary_location,cited_by_count
```

示例（Nature, ISSN: 0028-0836）：
```
https://api.openalex.org/works?filter=primary_location.source.issn:0028-0836,from_publication_date:2024-06-01&sort=publication_date:desc&per_page=20
```

**2. PubMed API（医学/心理/生物）**

```
# Step 1: 搜索获取 PMID 列表
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
  ?db=pubmed
  &term="{期刊名}"[journal] AND {起始日期}:{结束日期}[pdat]
  &retmax=50
  &sort=pub_date
  &retmode=json

# Step 2: 获取文章详情
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
  ?db=pubmed
  &id={PMID1},{PMID2},...
  &retmode=xml
  &rettype=abstract
```

示例（NEJM）：
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="N Engl J Med"[journal] AND 2024/06/01:2024/06/30[pdat]&retmax=20&sort=pub_date&retmode=json
```

**3. Crossref API（DOI 元数据）**

```
# 按 ISSN 查询，按出版日期排序
GET https://api.crossref.org/works
  ?filter=issn:{ISSN},from-pub-date:{起始日期}
  &sort=published
  &order=desc
  &rows=50
  &select=DOI,title,author,published-print,published-online,volume,issue
```

示例：
```
https://api.crossref.org/works?filter=issn:0028-0836,from-pub-date:2024-06-01&sort=published&order=desc&rows=20
```

**4. Semantic Scholar API（AI/CS）**

```
# 按期刊名搜索
GET https://api.semanticscholar.org/graph/v1/paper/search
  ?venue={期刊名}
  &year={年份}
  &fieldsOfStudy=Computer Science
  &fields=title,authors,year,venue,citationCount,abstract
  &limit=50
```

示例：
```
https://api.semanticscholar.org/graph/v1/paper/search?venue=Nature&year=2024&fields=title,authors,year,venue,citationCount,abstract&limit=20
```

#### ⚙️ 工程注意事项（避坑）

> 这些是反复踩过的坑，按此执行可避免无效返工：

1. **只取元信息，不读全文：** 本 skill 全程只使用 API 返回的 title / abstract / authors / publication_date，**绝不下载或解析 PDF、不读图片、不递归任何子链接**。
2. **用脚本解析，别把 JSON/XML 灌进上下文：** 把多次查询的结果存成文件，用脚本解析 + 去重（按 DOI 或标题），只把**精炼后的结果**带回上下文。一次查询可能含 50+ 篇，原始 JSON 极占 token。
3. **编码统一 UTF-8：** Windows 控制台默认 GBK，直接 `print` 含特殊字符会报错。**所有文件读写显式加 `encoding='utf-8'`，中间结果写入文件而非 print。**
4. **临时文件用原生绝对路径：** Git Bash 的 `/tmp` 与 Windows Python 看到的路径不一致，跨工具传递文件时用脚本所在环境的原生绝对路径。
5. **合并脚本，减少中间文件：** 把搜索、解析、去重、筛选合并为一个 Python 脚本，一次运行输出最终需要的数据。避免写多个脚本产生大量中间文件。
6. **API 限流处理：**
   - PubMed：无 API key 时 3次/秒，有 key 时 10次/秒
   - OpenAlex：100,000 次/天，建议加 `mailto` 参数
   - Crossref：加入 polite pool（加 `mailto` 参数）可提高速率
   - Semantic Scholar：100 次/5分钟
7. **降级策略：** 主数据源失败时，自动切换到备用数据源重试。

#### 🔧 推荐的 Pipeline 结构（省 token）

目标：**从搜索到报告，最多 3 步操作**。

```
Step 1: 运行 pipeline 脚本（一次执行完成全部数据处理）
  输入：期刊列表、日期范围、数据源配置
  输出：
    - final_papers.json — 所有文章（含标题、作者、摘要、DOI、引用数）
    - stats.json — 统计概览（每刊文章数、总文章数）

Step 2: 读取 final_papers.json + stats.json（两个精简文件）

Step 3: 写报告
```

---

### 第三步：生成报告

按以下结构生成报告并保存为 .md 文件。

#### 🎨 语言风格要求（全局生效）

报告中有两类写作任务，面向不同读者：

---

**📝 中文摘要（面向学者）**

> 目标读者：同领域或相邻领域的研究者。

**写作原则：**
- **干净的学术中文**：不是机翻，是地道的学术中文
- **术语保留，首次注释**：专业术语直接使用，第一次出现时括号中给出简明解释
  - ✅ "采用纵向追踪设计（longitudinal design，即对同一批被试进行多次测量）"
  - ❌ 不要为了通俗把术语替换成大白话

**禁止的机翻八股（必须改写）：**
- "本文提出了一种基于 XXX 的框架" → 改为 "作者提出 XXX"
- "本文旨在探索……的可能性" → 改为 "本研究考察了……"
- "研究结果表明" → 改为 "结果发现"
- "具有重要意义" → 说清楚具体有什么意义

**长度：** 3-5 句，覆盖核心信息点（问题→方法→结果→结论）

---

**💬 通俗解读（面向非专业读者）**

> 目标读者：对这个方向感兴趣但不是该领域专家的人。

**写作原则：**
- **说清三件事**：解决什么问题？怎么做的？发现了什么？
- **可以用类比**，但类比要准确、不误导
- **术语必须解释**：用人话说清楚
  - ✅ "采用双盲实验（就是参与者和实验员都不知道谁被分到了实验组）"

**长度：** 2-3 句

---

**🔎 点评（亮点 + 局限）**

- 💡 **亮点（1-2 句）：** 这篇论文最突出的贡献是什么？
- ⚠️ **局限（1-2 句）：** 最大的一个问题是什么？

---

**去冗余规则（全局生效）：**
1. 每句话必须有信息增量
2. 同一术语只在第一次出现时解释
3. 点评中的信息不要重复中文摘要已经说过的内容
4. 禁止空洞修饰词（"开创性的""革命性的"）

---

#### 📄 模式 A 报告结构（期刊追踪）

```markdown
# 📰 期刊日报 — {期刊名}

📅 时间范围：{起始日期} ~ {结束日期}
📊 文章数量：{N} 篇
⏰ 生成时间：{当前时间}
📈 影响力指标：{2-year mean citedness}

---

## 📑 最新文章目录

### 1. {英文标题}
- **🏷️ 中文标题：** {中文翻译}
- **👤 作者：** {第一作者 et al.}
- **📅 发表日期：** {日期}
- **🔗 DOI：** {DOI链接}
- **📊 引用数：** {被引次数}

**📝 中文摘要：**
{3-5 句，学术中文}

**💬 通俗解读：**
{2-3 句，给非本领域读者看}

**🔎 点评：**
- 💡 **亮点：** {1-2 句}
- ⚠️ **局限：** {1-2 句}

---

### 2. {下一篇论文}
...

---

## ⭐ 推荐阅读

### 🌟 {论文标题}
{2-3 句：为什么这篇最值得花时间读}

### 🌟 {论文标题}
{2-3 句}

### 🌟 {论文标题}
{2-3 句}
```

#### 📄 模式 B 报告结构（领域扫描）

```markdown
# 🔍 领域扫描报告 — {用户的检索主题}

📅 时间范围：{起始日期} ~ {结束日期}
📰 检索期刊：{期刊列表}
🔍 检索关键词：{实际使用的关键词}
📊 检索结果：{N} 篇相关文章
⏰ 生成时间：{当前时间}

---

## 📊 概览

{2-4 句话。重点呈现研究趋势，用论文作为证据}

---

## 📑 相关文章（{N} 篇）

### 1. {英文标题}
- **🏷️ 中文标题：** {中文翻译}
- **👤 作者：** {第一作者 et al.}
- **📰 发表期刊：** {期刊名}
- **📅 发表日期：** {日期}
- **🔗 DOI：** {DOI链接}

**📝 中文摘要：**
{3-5 句，学术中文}

**💬 通俗解读：**
{2-3 句}

**🔎 点评：**
- 💡 **亮点：** {1-2 句}
- ⚠️ **局限：** {1-2 句}

---

（重复直到所有论文展示完毕）

## ⭐ 精读推荐

### 🌟 {论文标题}
{2-3 句：为什么这篇最值得花时间读}
```

---

### 第四步：保存文件

1. 确保输出目录存在（不存在则创建）
2. 文件名格式：
   - 模式 A：`期刊日报_{期刊名}_{日期}.md`
   - 模式 B：`领域扫描_{主题}_{日期}.md`
3. 保存后告知用户文件路径

### 第五步：对话框内摘要推送

**模式 A 摘要格式：**
```
✅ 期刊日报已生成！

📁 {文件路径}

📰 {期刊名} 最新动态：
- 📌 {趋势一}
- 📌 {趋势二}

📊 本期 {N} 篇文章

⭐ 推荐阅读：
- 🌟 {论文} — {理由}
- 🌟 {论文} — {理由}
```

**模式 B 摘要格式：**
```
✅ 领域扫描报告已生成！

📁 {文件路径}

💡 {1-2句话回答用户问题}

📰 检索期刊：{期刊列表}
📊 找到 {N} 篇相关文章

🎯 关键发现：
- 📌 {发现一}
- 📌 {发现二}

⭐ 推荐阅读：
- 🌟 {论文} — {理由}
- 🌟 {论文} — {理由}
```

**对话框回复可视化要求：**
- 使用 emoji 图标区分不同信息块
- 关键信息加粗
- 每个要点控制在 1-2 句话
- 整体控制在用户无需滚动即可看完的长度
- 避免 markdown 表格
- 语气简洁、信息密度高

---

## 期刊目录管理

期刊目录存储在 `期刊目录.md` 文件中，按学科分组。用户可以：

1. **查看期刊**：直接说期刊名，如"Nature 最新一期"
2. **按学科组查询**：说学科组名，如"心理学期刊"、"医学期刊"
3. **新增期刊**：编辑 `期刊目录.md`，在对应学科表格中添加行
4. **删除期刊**：编辑 `期刊目录.md`，删除对应行

**学科组速查：**
| 学科组 | 包含期刊（部分） |
|--------|----------------|
| 综合组 | Nature, Science, PNAS, Nature Communications |
| 医学组 | NEJM, The Lancet, JAMA, BMJ, Nature Medicine |
| 心理组 | Nature Mental Health, Psychological Bulletin, JPSP |
| 神经组 | Nature Neuroscience, Neuron, Journal of Neuroscience |
| AI组 | Nature Machine Intelligence, IEEE TPAMI, JMLR |
| 物理组 | Physical Review Letters, Nature Physics |
| 化学组 | JACS, Nature Chemistry, Angewandte Chemie |
| 生物组 | Nature Biotechnology, Nature Cell Biology |
| 经济组 | American Economic Review, QJE |
| 社科组 | American Sociological Review, APSR |
| 教育组 | Review of Educational Research, Journal of Educational Psychology |
| 环境组 | Nature Climate Change, Nature Sustainability |

完整期刊列表见 `期刊目录.md`。

---

## 个人署名

skill来源：山野的云，清华大学心理学系博士生
