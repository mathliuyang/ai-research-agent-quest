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
- `1`-`3`：跳到对应案例
- `Home`：回到开头
- `End`：跳到结尾

## Level 01：专利 PDF 整理

```bash
cd case_pack/02_patent_pdf
python patent_pdf_extractor.py sample_pdfs --out outputs/sample_catalog.txt --csv outputs/sample_info.csv
```

## Level 02：Nature Skills 演示

按页面中的三段提示词现场演示：

```text
帮我生成一个模拟数据存到 csv 文件中，我需要对其进行科研绘图。
请帮我用 nature-figure 来完成上述数据的科研绘图。
帮我生成一段对这个结果的中文描述。接下来利用 nature-polishing 对上述的结果描述进行学术英语写作。
```

## Level 03：论文复现报告

打开：

```text
../reproduce_gbdf2_fkpp/report.html
```
