# IPO Inquiry Dossier

> 不写代码、没用过 GitHub 也没关系。想先快速看懂这个工具能做什么、长什么样，看这一页就够，不用安装任何东西：[从这里开始](从这里开始.md)。

**给 IPO 审核问询找可比公司的先例，按统一标准筛出能用的，再逐字取证，自动生成可直接粘贴进答复的底稿。**

做 IPO 项目时，最花时间的往往不是抄写，而是判断：先读懂一道审核问询到底在问什么，再到几家到十几家可比公司、每家好几份问询回复里翻找相关先例，然后一条条判断它是不是真的可比、能不能用。方向理解错了，翻半天还得作废。

这个工具把最磨人的理解和检索压下来。你给它一批可比公司的问询回复 PDF 和一道题，它先理解题意、检索可能相关的先例、按统一标准打分初筛，再生成一份格式整齐、能直接粘贴的 `.docx` 底稿。引用由脚本按页码从源 PDF 逐字读出，一字不差、标好出处，不会被 AI 改写。你要做的是复核它挑出来的先例，而不是从零大海捞针。

## 为什么比人工好

| | 人工 | 这个技能 |
|---|---|---|
| 找可比先例 | 在多家公司、多份文件里反复读、反复判断，慢且容易看走眼 | 自动检索加按统一标准初筛，你只复核 |
| 引用与格式 | 电脑上复制粘贴，引用靠人核对、排版容易乱 | 脚本按页码逐字取证，一字不差、格式统一 |
| 判断标准 | 因人而异 | 统一评分标准，每步可回溯 |
| 耗时 | 一份三到五小时 | 几分钟 |

关键在于把**判断**和**取证**拆开：AI 只决定“哪些案例可比、抄哪几段”，而底稿正文由脚本按页码从源 PDF 逐字读出。既拿到 AI 的判断效率，又保住引用与原文一字不差、排版统一。

## 给谁用

做 IPO 项目的投行人员，常要为一道审核问询找可比公司的先例：在多家可比公司、每家好几份问询回复里翻找、判断、复制粘贴，整理成可引用的底稿。这件事反复、费时、靠经验，还容易判断失准。这个工具把它变成可复用、可回溯的流程。

## 看效果

![示例底稿](docs/sample.png)

`examples/` 里有一份完整成品（[底稿_功率器件代工毛利率改善措施_2025-03-14.docx](examples/底稿_功率器件代工毛利率改善措施_2025-03-14.docx)）、对应的 `sample_hits.jsonl`（精排结果输入示范）和 `sample_ranking_report.jsonl`（含被丢弃候选的打分回溯）。建议先打开这份 docx 看产物长什么样。

## 怎么用

> 前提：这是给 Claude Code、Codex、Cursor 这类 coding agent 用的技能。没用过这类工具，看顶部那份说明就够，不必往下读。

**快速上手，三步：**

1. **装**——对你的 agent 说一句话，让它把 https://github.com/hhaa134323/ipo-inquiry-dossier 克隆到 `~/.claude/skills/` 下，它会自己装好。
2. **放**——把可比公司的问询回复 PDF 放进任意一个目录。
3. **说**——告诉 agent：用 ipo-inquiry-dossier 帮我做底稿，PDF 在哪个目录、要回答哪道问询。剩下的它全自动跑完。

下面是更细的说明，平时不用全看。

### 安装

**自然语言安装（推荐）** —— 直接对 agent 说：

> 把 https://github.com/hhaa134323/ipo-inquiry-dossier 这个 Claude Code 技能克隆到我的 `~/.claude/skills/` 下，然后用它帮我做一份可比先例底稿。

agent 会自己 `git clone` 到技能目录，首次运行时还会自动建好运行环境（见下方「依赖」）。

**手动安装（Claude Code）** —— 自己 clone：

```bash
# 全局（所有项目可用）
git clone https://github.com/hhaa134323/ipo-inquiry-dossier.git ~/.claude/skills/ipo-inquiry-dossier

# 或项目级（仅当前项目）
git clone https://github.com/hhaa134323/ipo-inquiry-dossier.git 你的项目/.claude/skills/ipo-inquiry-dossier
```

也可用 `claude --add-dir /path/to/ipo-inquiry-dossier` 直接引用，无需拷贝。

**其他 coding agent（Codex / Gemini CLI / Cursor…）** —— 把仓库链接丢给它，让它从 **`SKILL.md`** 读起、按需加载 `docs/` 和 `scripts/`；有文件系统权限的也可照上面装进自己的技能目录。

### 使用

装好后，用斜杠命令 `/ipo-inquiry-dossier`，或者直接像下面示例这样把需求说清楚：

> 我的可比公司问询回复 PDF 都放在 `<我放PDF的目录>`（换成你自己的真实路径，比如 Windows 写 `D:\可比公司问询回复`，Mac/Linux 写 `~/可比公司问询回复`），底稿想输出到 `<输出目录>`。请用 ipo-inquiry-dossier 帮我做一份可比先例底稿，要回答的问询是：「<把要回答的那道审核问询原文粘到这里>」

<details>
<summary>输入和输出路径的细节，一般不用管，agent 会自动带参数</summary>

脚本用 `--input` 和 `--output` 两个参数控制，你只要把自己的目录路径告诉 agent，它会自动带上参数，不用自己敲。注意传的是你自己存放 PDF、想要产物的目录，不是 skill 安装目录里的子文件夹。

- **输入 PDF 目录** —— `--input`（简写 `-i`），放可比公司问询回复 PDF 的目录。脚本会递归扫描该目录下所有 `*.pdf`。Windows 例 `D:\可比公司问询回复`；Mac/Linux 例 `~/可比公司问询回复` 或 `/Users/你的用户名/可比公司问询回复`。
- **输出 docx 目录** —— `--output`（简写 `-o`），底稿 docx 的输出目录，产物名形如 `底稿_{主题}_{日期}.docx`；同目录还会落一份 `hits.jsonl`（精排结果，必要时可用 `--hits` 单独指定路径）。Windows 例 `D:\底稿输出`；Mac/Linux 例 `~/底稿输出`。

</details>

技能会：

1. 调 `extract.py --input <PDF目录>` 把 PDF 逐页抽成 `[PAGE n]` 文本缓存（脚本）；
2. 检索可比先例，按统一评分标准（rubric，5 个维度各 0–2 分）精排、产出 `hits.jsonl`（**这步靠 AI 判断**）；
3. 调 `build_dossier.py --input <PDF目录> --output <输出目录>` 按页码逐字渲染出 `.docx` 底稿（脚本）。

你全程只提供 PDF 和问题、告诉 agent 文件放在哪，不用自己敲命令、不用装依赖。

## 依赖（首次自动装）

依赖只有 `pymupdf` 和 `python-docx`，**使用者不用手动装**。`SKILL.md` 里写了「首次运行自动建 venv + 装依赖」：agent 第一次跑时会建一个 `.venv` 并把依赖装进去，之后统一用该 venv 的解释器跑脚本（跨平台，不引入 uv 之类额外工具）。脚本只用 `pathlib` 和标准库，Windows / macOS / Linux 一致运行。

## Skill 结构

```
ipo-inquiry-dossier/
├── SKILL.md              技能入口（name/description 自动触发；工作流 + 规则）
├── docs/
│   ├── METHODOLOGY.md    方法论唯一事实源（召回、精排 rubric、hits 契约、渲染规则）
│   └── sample.png        示例底稿截图
├── scripts/
│   ├── extract.py        PDF 抽取为 [PAGE n] 文本缓存
│   └── build_dossier.py  hits.jsonl + PDF 渲染为 .docx
├── examples/             成品 docx + hits / 精排报告样例
└── requirements.txt      pymupdf, python-docx
```

技能用**渐进式披露**：agent 先读 `SKILL.md` 拿到全局地图，其余文件按需加载。

| 文件 | 作用 | 何时加载 |
|---|---|---|
| `SKILL.md` | 工作流 + 规则 | 总是（技能触发时） |
| `docs/METHODOLOGY.md` | 方法论唯一事实源 | 召回 / 精排 / 写 hits 时 |
| `scripts/extract.py` | PDF → 文本缓存 | 步骤 1 |
| `scripts/build_dossier.py` | 渲染 .docx | 步骤 3 |
| `examples/` | 成品 + hits 格式样例 | 想看产物或对照格式时 |
| `requirements.txt` | 依赖清单 | 首次装依赖时 |

## 设计要点

### 引用逐字可溯，不被 AI 改写
- PDF 正文由 `extract.py`（PyMuPDF）一次性抽成带 `[PAGE n]` 标记的 `.txt` 缓存。
- AI 只决定“抄哪些”并记下页码指针；渲染时由 `build_dossier.py` 按页码直接从 PDF 逐字读出——引用与原文一字不差，也不进 AI 上下文被改写。
- 顺带的好处：token 消耗与底稿篇幅解耦，一份十页底稿约几千 token，而非几十万。

### 召回与精排两段分离（AI 负责的部分）
- 召回：从问题原文拆限定词，做同义 / 口径扩展，机械 grep 扫缓存，高召回不取舍。
- 精排：逐个候选按一套固定的**评分标准（rubric）**打分。rubric 就是这张“打分表”，5 个维度——同问询实质、真问询先例、产品行业可比、口径一致、可借鉴——每个维度 0–2 分；总分达 7 分且没有 0 分项才保留。这保证不同问题、不同人用同一把尺子。
- 所有候选（含丢弃的）记录在 `ranking_report.jsonl`，每步判断可回溯。

### 脚本确定性渲染 docx
- 结论速览卡 / 五级溯源表 / 关键锚点自动标黄 / 表格三级兜底（真表格→截图→段落）/ 自动目录（Word 右键“更新域”）。

## 工作流

虚线框是 **AI 判断**的环节，实线框是**脚本确定性执行**：

```mermaid
flowchart TD
    A["问询回复 PDF"] --> B["extract.py 抽文本缓存"]
    B --> C["检索可比先例<br>+ 评分精排"]
    C --> D["hits.jsonl<br>页码指针 + 评分"]
    D --> E["build_dossier.py<br>按页码逐字渲染"]
    E --> F[".docx 底稿"]
    classDef ai stroke-dasharray:5 5;
    class C ai;
```

AI 只出现在中间那一步（决定哪些案例可比、抄哪几段）；两端的抽取和渲染都是脚本确定性完成，不经模型。

## 引用纪律

- 引用一律逐字落盘，绝不让 AI 改写；
- 每条结论落到“文件 + 页码”；
- 找不到就说找不到，严禁编造。

方法论完整细节见 [docs/METHODOLOGY.md](docs/METHODOLOGY.md)。
