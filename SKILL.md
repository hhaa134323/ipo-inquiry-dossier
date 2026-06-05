---
name: ipo-inquiry-dossier
description: A 股 IPO 问询函检索 + 生成可比案例答题底稿（原文不过模型）。用户提到 IPO、问询、可比公司、底稿、招股书、反馈意见、审核问询时自动触发。
---

# IPO 问询可比案例底稿

## 何时用

收到一道“请你找可比上市公司的审核问询回复案例，做一份答题底稿”类型的任务时使用。

## 前置：环境在安装时已装好（见 README）

本 skill 的依赖安装放在**安装 skill 时**完成——克隆仓库时由 agent 一并建好 `.venv` 并按 `requirements.txt` 装依赖（详见 README 的「安装」「依赖」两节），**不在任务工作流里重复安装**。任务运行阶段假定环境已就绪。

运行脚本时用隔离环境里的解释器（下文记为 `PY`）：

- macOS / Linux：`PY` = `.venv/bin/python`
- Windows：`PY` = `.venv\Scripts\python.exe`

依赖只有 `pymupdf` 和 `python-docx`，脚本其余只用 `pathlib` 和标准库，Windows / macOS / Linux 一致运行。若运行时发现 `.venv` 不存在（skill 未按 README 装好），再回退执行一次 README「安装」里的环境步骤后继续，不要把安装逻辑混进每次任务。

## 输出与工作目录约定（重要）

- `--output` 目录**只放最终交付物** `底稿_{主题}_{日期}.docx`，不要往里堆别的。
- 所有中间产物——`term_map.jsonl`、`candidates.jsonl`、`hits.jsonl`、`ranking_report.jsonl`、渲染用的页面截图与表格截图——一律写进**工作目录** `_work/`（默认 `{output}/_work`）。这个目录可整个删除，不影响交付的 docx（图片在生成时已内嵌进 docx）。
- **不要临时手写脚本丢进输出目录**：机械步骤已固定为 `scripts/` 下的脚本（见下），直接带参数调用；确需临时草稿也只放进 `_work/`。

## 工作流

> 机械步骤（抽取、召回、读页、渲染）一律调用 `scripts/` 下的固定脚本，**不要临场另写脚本**；只有判断步骤（口径词扩展、rubric 打分）由 AI 完成。

1. **extract.py** `scripts/extract.py` —— 将可比公司 PDF 逐页抽取文本为 `[PAGE n]` 缓存（.txt），原文不过模型。
2. **生成口径词（AI 判断）** —— 从问题原文动态拆解限定词并按行业扩展，落盘到 `_work/term_map.jsonl`（**不得照搬半导体示例表**，详见 `docs/METHODOLOGY.md` 步骤 2）。
3. **recall.py** `scripts/recall.py` —— 机械召回：读 `_work/term_map.jsonl`，grep 全部 `.txt` 缓存，产出 `_work/candidates.jsonl`。脚本只 grep、不取舍、不判断。
4. **精排打分（AI 判断）** —— **打分前必须先读 `docs/METHODOLOGY.md`，严格按 rubric 逐维度打分。** 粗到细级联：闸一只读问询题目打 A/B（用 `read_pages.py` 读题目页）、淘汰主题不符者（维度 A=0 立即淘汰、不读回复）；闸二对幸存者逐字精读回复打 C/D/E（同样用 `read_pages.py` 读回复页区间，不为省 token 裁窗口）。产出 `_work/hits.jsonl`，全过程（含淘汰/丢弃）记 `_work/ranking_report.jsonl`。
    - **read_pages.py** `scripts/read_pages.py` —— 机械读页：`--file X.txt --pages 42-45` 逐字打印指定页，供闸一/闸二阅读，原文不改写。
5. **build_dossier.py** `scripts/build_dossier.py` —— 读 hits.jsonl + PDF 源文件，按页码逐字渲染出可直接粘贴的 `.docx` 底稿到 `--output`（中间截图落 `_work/`）。

## 运行示例

```bash
# 0. 设 PY（见上方「前置」），OUT 为输出目录，WORK 默认 {OUT}/_work
# 1. 抽取文本缓存
PY scripts/extract.py --input /path/to/pdf-dir

# 2.（AI）从问题原文生成口径词 -> 写 {OUT}/_work/term_map.jsonl

# 3. 机械召回
PY scripts/recall.py --input /path/to/pdf-dir --term-map /path/to/out/_work/term_map.jsonl

# 4.（AI）精排：用 read_pages.py 读题目/回复页打分 -> 写 {OUT}/_work/hits.jsonl
PY scripts/read_pages.py --file /path/to/pdf-dir/某公司.txt --pages 42-45

# 5. 生成底稿（中间截图进 _work，docx 落 OUT）
PY scripts/build_dossier.py --input /path/to/pdf-dir --output /path/to/out --hits /path/to/out/_work/hits.jsonl
```

**先看成品**：`examples/` 里有一份完整产物和对应的 `sample_hits.jsonl`（精排结果输入示范）、`sample_ranking_report.jsonl`（含被丢弃候选的打分回溯）。先打开 docx 看产物长什么样，再照着 `sample_hits.jsonl` 的格式写自己的 `hits.jsonl`。

## CLI 参数

| 脚本 | 参数 | 说明 | 默认 |
|---|---|---|---|
| `extract.py` | `--input` / `-i` | 递归扫描 PDF 的目录 | `./input` |
| `recall.py` | `--input` / `-i` | 含 .txt 缓存的目录 | `./input` |
| `recall.py` | `--term-map` / `-t` | AI 生成的口径词表路径 | `./output/_work/term_map.jsonl` |
| `recall.py` | `--output` / `-o` | 候选清单输出路径 | `{term-map 同目录}/candidates.jsonl` |
| `read_pages.py` | `--file` / `-f` | 目标 .txt 缓存（也接受 .pdf） | 必填 |
| `read_pages.py` | `--pages` / `-p` | 页码，如 `42` / `42-45` / `3,7,12-14` | 必填 |
| `build_dossier.py` | `--input` / `-i` | 含 PDF 与 .txt 缓存的目录 | `./input` |
| `build_dossier.py` | `--output` / `-o` | 输出目录（只放最终 .docx） | `./output` |
| `build_dossier.py` | `--work` / `-w` | 中间产物目录（截图/缓存/hits 等） | `{output}/_work` |
| `build_dossier.py` | `--hits` | hits.jsonl 路径 | `{work}/hits.jsonl` |

## 详细规格

详细方法论（召回策略、精排 rubric、hits.jsonl 契约、底稿渲染规则）见 **`docs/METHODOLOGY.md`**，本文档的唯一事实源。

## 引用纪律

- 原文**绝不过 AI 改写**，所有引用由脚本逐字从缓存落盘。
- 所有结论必须落到“文件 + 页码”。
- 严禁编造；找不到就说找不到。
