# Operation Guide

## 打开网站

```text
index.html
```

推荐用 Chrome 或 Edge 打开，浏览器缩放 90%-110%。

## 讲前价格检查

模型价格、套餐权益和账号门槛变化很快。若现场会具体提费用，建议讲前刷新：

- OpenAI / Codex pricing
- ChatGPT pricing
- Claude pricing
- Cursor pricing
- Trae 官网

## 快捷键

- `↓` / `→`：下一屏
- `↑` / `←`：上一屏
- `1`-`5`：跳到对应案例
- `Home`：回到开头
- `End`：跳到结尾

## 代码案例

```bash
cd case_pack/01_code_debug
python src/analyze_experiment.py
```

该脚本故意带有问题，用于让 Agent 现场修复。参考答案在：

```text
src/analyze_experiment_solution.py
```

## 专利案例

```bash
cd case_pack/02_patent_pdf
python patent_pdf_extractor.py sample_pdfs --out outputs/sample_catalog.txt --csv outputs/sample_info.csv
```

## 绘图案例

```bash
cd case_pack/04_plot_style
python plot_paper_style.py
```

## 小工具案例

双击：

```text
case_pack/05_report_tool/index.html
```
