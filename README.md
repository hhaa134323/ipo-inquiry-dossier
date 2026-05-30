# IPO 问询检索 · 可比案例底稿生成

输入一道审核问询问题 + 一批可比公司的问询回复 PDF，输出一份**带页码溯源**的可比案例底稿（`.docx`）。

## 这是什么 / 什么时候用

- **输入**：一道问询问题 + 若干可比公司 PDF
- **输出**：`底稿_{主题}_{日期}.docx`，每条命中都标注「公司 / 轮次 / 日期 / 文件 / 页码」五级溯源
- **适合**：需要快速找到“同类公司这道问询题怎么答的”，并把命中片段连同出处贴进 Word

## 怎么用（Windows，PowerShell）

> 依赖已由脚本内联声明（PEP 723），用 `uv` 运行会自动安装，**无需手动 `pip install`**。

**0. 装 uv（一次性）**

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**1. 放入 PDF，抽取文本缓存**

把可比公司 PDF 放进 `input/` 目录，然后：

```powershell
uv run scripts/extract.py --input .\input
```

→ 为每个 PDF 生成同名 `.txt`，每页以 `[PAGE n]` 开头，作为后续检索的缓存。

**2. 生成命中清单 `hits.jsonl`**

这一步是本技能的核心：读取 `.txt` 缓存，按问询问题做召回 + 严判，产出 `output/hits.jsonl`（判决逻辑见 `docs/METHODOLOGY.md`）。文件格式：第一行是 meta，其余每行一个候选案例。

```json
{"主题":"毛利率分析","问题原文":"请发行人结合单价、销量、成本变化，量化分析报告期内主营产品毛利率的变动情况及原因。","检索条件":"毛利率 单价 销量"}
{"序号":"示例","公司":"可比公司A","轮次":"第一轮","日期":"20240101","文件":"问询回复.pdf","问询":{"页":12,"形式":"文本"},"回复":{"起页":42,"止页":45,"形式":"表格"},"相关性":"同为毛利率拆分问询，回复含单价/销量/成本量化表","判可比依据":{"保留":true,"总分":8},"关键锚点":{"回复":["毛利率变动"]}}
```

> 只有 `判可比依据.保留 == true` 的候选才会进入正文底稿，其余进文末附录。

**3. 生成底稿**

```powershell
uv run scripts/build_dossier.py --input .\input --output .\output --hits .\output\hits.jsonl
```

→ 得到 `output\底稿_毛利率分析_20240101.docx`，每个案例含问询/回复原文、表格、五级溯源信息，命中锚点黄色高亮。

## 目录结构

- `scripts/extract.py` — PDF → 带 `[PAGE n]` 的文本缓存
- `scripts/build_dossier.py` — `hits.jsonl` + PDF → `.docx`
- `docs/METHODOLOGY.md` — 召回 + 严判方法论（单一事实源）
- `examples/` — 示例底稿与 `hits.jsonl`

## License

MIT
