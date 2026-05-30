---
name: ipo-inquiry-dossier
description: A 股 IPO 问询函检索 + 生成可比案例答题底稿（原文不过模型），mentor / 求职作品集场景。用户提到 IPO、问询、可比公司、底稿、招股书、反馈意见、审核问询时自动触发。
---

# IPO 问询可比案例底稿

## 何时用

收到一道"请你找可比上市公司的审核问询回复案例，做一份答题底稿"类型的面试题/笔试/mentor 任务时使用。

## 三步工作流

1. **extract.py** `scripts/extract.py` —— 将可比公司 PDF 逐页抽取文本为 `[PAGE n]` 缓存（.txt），原文不过模型。
2. **检索 → 精排** —— 人工 / AI 按 `docs/METHODOLOGY.md` 步骤完成召回与精排，产出 `hits.jsonl`。
3. **build_dossier.py** `scripts/build_dossier.py` —— 读 hits.jsonl + PDF 源文件，生成可直接粘贴的 `.docx` 底稿。

## 运行示例

```bash
# 1. 抽取文本缓存
python scripts/extract.py --input /path/to/pdf-dir

# 2. 在 hits.jsonl 中写入精排结果（格式见 docs/METHODOLOGY.md）

# 3. 生成底稿
python scripts/build_dossier.py --input /path/to/pdf-dir --output /path/to/out --hits /path/to/hits.jsonl
```

## CLI 参数

| 脚本 | 参数 | 说明 | 默认（相对当前工作目录） |
|---|---|---|---|
| `extract.py` | `--input` / `-i` | 递归扫描 PDF 的目录 | `./input` |
| `build_dossier.py` | `--input` / `-i` | 含 PDF 与 .txt 缓存的目录 | `./input` |
| `build_dossier.py` | `--output` / `-o` | 输出目录（.docx + 截图） | `./output` |
| `build_dossier.py` | `--hits` | hits.jsonl 路径 | `{output}/hits.jsonl` |

所有路径接受绝对或相对路径，默认相对当前工作目录。

## 详细规格

详细方法论（召回策略、精排 rubric、hits.jsonl 契约、底稿渲染规则）见 **`docs/METHODOLOGY.md`**，本文档的唯一事实源。

## 引用纪律

- 原文**绝不过 AI 改写**，所有引用由脚本逐字从缓存落盘。
- 所有结论必须落到"文件 + 页码"。
- 严禁编造；找不到就说找不到。

## 依赖

```bash
pip install -r requirements.txt
```
