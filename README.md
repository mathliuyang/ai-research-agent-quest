# AI+科研 Agent Quest

一个用于课题组分享的静态展示网站，主题是如何把 AI Agent 融入科研工作流。项目包含主展示页、讲稿、操作指南，以及 5 个可现场演示的案例素材包。

## 在线或本地打开

这是纯静态项目，不依赖后端服务，也不依赖在线 CDN。克隆仓库后直接打开：

```text
index.html
```

推荐使用 Chrome 或 Edge，浏览器缩放保持在 90%-110%。

## 内容结构

```text
assets/       样式、脚本、动态 SVG
case_pack/    5 个演示案例素材包
docs/         讲稿、操作指南、文件结构、检查清单、资料来源
index.html    主展示入口
```

## 演示案例

- Level 01：代码修改与自动调试
- Level 02：批量整理专利 PDF
- Level 03：LaTeX 中英翻译与术语一致性
- Level 04：复现论文图风格
- Level 05：轻量报告生成小工具

时间有限时，优先打开 `index.html`、`case_pack/02_patent_pdf` 和 `case_pack/04_plot_style`，可以覆盖工具选择、文献/专利整理、科研绘图三条主线。

## 快捷键

- 鼠标滚动：按顺序浏览
- `↓` / `→`：下一屏
- `↑` / `←`：上一屏
- `1`-`5`：跳到对应案例
- `Home` / `End`：跳到开头 / 结尾

## 运行示例

代码调试案例：

```bash
cd case_pack/01_code_debug
python src/analyze_experiment.py
```

专利 PDF 整理案例：

```bash
cd case_pack/02_patent_pdf
python patent_pdf_extractor.py sample_pdfs --out outputs/sample_catalog.txt --csv outputs/sample_info.csv
```

论文风格绘图案例：

```bash
cd case_pack/04_plot_style
python plot_paper_style.py
```

## 文档

- `docs/operation_guide.md`：现场操作说明
- `docs/speaker_notes.md`：讲稿和讲解顺序
- `docs/checklist.md`：讲前检查清单
- `docs/sources.md`：页面中涉及的资料来源

## 价格说明

页面中的订阅费用是按 2026-07-02 公开页面整理的现场参考，不作为长期价格承诺。正式分享前如需精确报价，请重新核对官方价格页。
