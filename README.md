# IPO 问询可比案例底稿

**一个 AI 驱动的 A 股 IPO 问询函底稿生成工具。收到面试题／笔试／mentor 任务——"请你找可比上市公司的审核问询回复案例，做一份答题底稿"——时，把 PDF 丢进去，出来可直接粘贴的 `.docx`。**

## 解决了什么真实问题

投行 / 证券研究的面试、笔试或实习任务中，经常会收到**找一家可比上市公司的审核问询回复，逐字抄录关键段落并做成一份底稿**的要求。传统做法是：

1. 人工翻大量 PDF，逐页"复制 → 粘贴 → 排版" → 3~5 小时
2. 大模型直接把整份 PDF 塞进上下文 → Token 飞涨、模型易篡改原文措辞
3. 没有统一的方法论 → 不同人的底稿质量参差不齐

这个工具把"判断"和"输出"分离：**模型只做判断（哪些案例可比、值不值得抄），底稿渲染全由确定性脚本完成，原文逐字落盘，不经过模型改写。**

---

## 核心设计亮点

### 🔑 原文不过模型（省 Token + 合规零改写）
- 所有 PDF 正文只由 `extract.py` 通过 PyMuPDF 一次性抽取为 `[PAGE n]` 标记的 `.txt` 缓存。
- 模型从缓存中**通过页码指针引用原文**，绝不把整份 PDF 塞进上下文；底稿渲染时由 `build_dossier.py` 按页从 PDF 直接逐字读取，**不经过模型管道**。
- 效果：Token 消耗与底稿篇幅解耦（一份 10 页底稿 ≈ 几千 Token，而非数十万）。

### 🔑 召回 → 精排两段检索 + Rubric 严判
- **召回阶段**：从问题原文拆关键词，做同义/口径扩展（附扩展表），机械 `grep -i` 扫描缓存，高召回、不取舍。
- **精排阶段**：5 维度 Rubric（同问询实质、真先例、产品可比、口径一致、可借鉴），每项 0–2 分，≥7 分且无 0 分才保留。
- 所有候选（含丢弃案例）全程记录在 `ranking_report.jsonl`，可回溯每步判断。

### 🔑 确定性脚本渲染 .docx
- **速览卡**：底稿首屏自动汇总"保留案例 / 精排结论 / 缺口说明 / 可直接移植章节"。
- **关键锚点高亮**：hits.jsonl 中的短文本指针命中原文后自动标黄，不限条目数。
- **表格三级兜底**：`find_tables()` 健康表 → Word 真表格；坏表 → 高清截图；无表 → 段落文本。
- **自动目录**：Word TOC 域，右键更新域即完成跳转。

### 🔑 跨平台
- 纯 `pathlib` + Python 标准库，Windows / macOS / Linux 一致运行。
- 所有路径通过 CLI 参数传入，默认相对当前工作目录，无硬编码。

---

## 工作流

```mermaid
flowchart LR
    A[PDF<br/>可比公司问询回复] --> B[extract.py<br/>PyMuPDF 逐页抽取]
    B --> C[.txt 缓存<br/>[PAGE n] 标记]
    C --> D[检索 → 精排<br/>grep 召回 + Rubric 严判]
    D --> E[hits.jsonl<br/>指针 + 相关性 + 锚点]
    E --> F[build_dossier.py<br/>python-docx 渲染]
    F --> G[.docx 底稿<br/>可复制粘贴]
    
    style A fill:#e1f5fe
    style C fill:#fff3e0
    style E fill:#e8f5e9
    style G fill:#fce4ec
```

---

## 快速开始

### 1. 克隆并创建虚拟环境

```bash
git clone https://github.com/hhaa134323/ipo-inquiry-dossier ipo-inquiry-dossier
cd ipo-inquiry-dossier

# macOS / Linux
python -m venv .venv
source .venv/bin/activate

# Windows (cmd)
python -m venv .venv
.venv\Scripts\activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 抽取 PDF 文本缓存

```bash
# 将可比公司 PDF 放入某目录后：
python scripts/extract.py --input /path/to/pdfs
```

### 4. 生成底稿

```bash
# 手动或借助 AI 完成检索定位后写入 hits.jsonl，然后：
python scripts/build_dossier.py --input /path/to/pdfs --output ./my_dossier --hits ./my_dossier/hits.jsonl
```

输出文件为 `底稿_{主题}_{日期}.docx`。

> 详细方法论（召回策略、精排 rubric、hits.jsonl 契约、底稿渲染规则）见 [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)。

---

## 目录结构

```
ipo-inquiry-dossier/
├── SKILL.md                 # Claude Code Skill 唯一入口（YAML frontmatter 自动匹配触发）
├── docs/
│   └── METHODOLOGY.md       # 唯一方法论事实源（检索/精排/渲染全规范）
├── scripts/
│   ├── extract.py           # PDF → [PAGE n] 文本缓存（PyMuPDF）
│   └── build_dossier.py     # hits.jsonl + PDF → .docx 底稿（python-docx）
├── examples/
│   ├── sample_hits.jsonl    # 样例命中数据（演示格式与结构）
│   ├── sample_ranking_report.jsonl  # 样例精排报告
│   └── 底稿_功率器件代工毛利率改善措施_2025-03-14.docx  # 演示底稿成品
├── requirements.txt
├── .gitignore
└── README.md
```

> **SKILL.md** 是 Claude Code 自动触发的入口文件，`name` + `description` 匹配用户场景后激活技能。其他 AI 工具可直接调用 `scripts/` 下的 CLI 脚本。

---

## 效果预览

![示例底稿](docs/sample.png)

> 📸 **待补**：请将一张 `.docx` 效果截图（建议含速览卡 + 黄色高亮段落 + 自动表格）放入 `docs/` 目录，并命名为 `sample.png`，然后删除上方 `<!-- ... -->` 注释。

---

## 先看产物

`examples/` 目录下已有：

- **`底稿_功率器件代工毛利率改善措施_2025-03-14.docx`** —— 一份真实的底稿成品，可直接打开看效果（速览卡、目录、案例排版、锚点高亮、表格重建）。
- **`sample_hits.jsonl`** —— 对应的命中数据格式，展示 JSON 契约与字段含义。

建议**先下载 `.docx` 看看产物长什么样**，再回来看代码与工作流。

---

## 许可证

MIT
