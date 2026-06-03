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
- Windows：`PY` = `.venv\\Scripts\\python.exe`

依赖只有 `pymupdf` 和 `python-docx`，脚本其余只用 `pathlib` 和标准库，Windows / macOS / Linux 一致运行。若运行时发现 `.venv` 不存在（skill 未按 README 装好），再回退执行一次 README「安装」里的环境步骤后继续，不要把安装逻辑混进每次任务。

## 三步工作流

1. **extract.py** `scripts/extract.py` —— 将可比公司 PDF 逐页抽取文本为 `[PAGE n]` 缓存（.txt），原文不过模型。
2. **检索 -> 精排** —— **精排打分前必须先读取 `docs/METHODOLOGY.md`，严格按其中的 rubric 逐维度打分，不得凭直觉跳过。** 召回用的口径词须从问题原文动态生成（不照搬半导体示例表）；精排走**粗到细级联**——闸一只读问询题目打 A/B 维度、淘汰主题不符者（维度 A=0 立即淘汰、不读回复），闸二对幸存者 grep 定位后**逐字精读回复**打 C/D/E（不为省 token 裁剪深读窗口，证据跨页也读全）。按其步骤完成召回与精排，产出 `hits.jsonl`。
3. **build_dossier.py** `scripts/build_dossier.py` —— 读 hits.jsonl + PDF 源文件，按页码逐字渲染出可直接粘贴的 `.docx` 底稿。

## 运行示例

```bash
# 1. 抽取文本缓存（PY 见上方「前置」）
PY scripts/extract.py --input /path/to/pdf-dir

# 2. 在 hits.jsonl 中写入精排结果（格式见 docs/METHODOLOGY.md，可参照 examples/sample_hits.jsonl）

# 3. 生成底稿
PY scripts/build_dossier.py --input /path/to/pdf-dir --output /path/to/out --hits /path/to/hits.jsonl
```

**先看成品**：`examples/` 里有一份完整产物和对应的 `sample_hits.jsonl`（精排结果输入示范）、`sample_ranking_report.jsonl`（含被丢弃候选的打分回溯）。先打开 docx 看产物长什么样，再照着 `sample_hits.jsonl` 的格式写自己的 `hits.jsonl`。

## CLI 参数

| 脚本 | 参数 | 说明 | 默认 |
|---|---|---|---|
| `extract.py` | `--input` / `-i` | 递归扫描 PDF 的目录 | `./input` |
| `build_dossier.py` | `--input` / `-i` | 含 PDF 与 .txt 缓存的目录 | `./input` |
| `build_dossier.py` | `--output` / `-o` | 输出目录（.docx + 截图） | `./output` |
| `build_dossier.py` | `--hits` | hits.jsonl 路径 | `{output}/hits.jsonl` |

## 详细规格

详细方法论（召回策略、精排 rubric、hits.jsonl 契约、底稿渲染规则）见 **`docs/METHODOLOGY.md`**，本文档的唯一事实源。

## 引用纪律

- 原文**绝不过 AI 改写**，所有引用由脚本逐字从缓存落盘。
- 所有结论必须落到“文件 + 页码”。
- 严禁编造；找不到就说找不到。
