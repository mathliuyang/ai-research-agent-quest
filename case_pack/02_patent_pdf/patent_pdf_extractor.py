#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch extract Chinese patent catalog entries from CNIPA-style patent PDFs.

Usage:
  python patent_pdf_extractor.py ./pdfs
  python patent_pdf_extractor.py ./pdfs --out 专利目录.txt --csv 专利信息.csv

Dependency:
  pip install pymupdf

What it extracts:
  - Granted patents: title, 授权公告号, 授权公告日
  - Published/application patents: title, 申请号, 申请日
  - Sorts each class by the relevant date in descending order.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

try:
    import fitz  # PyMuPDF
except ImportError as exc:
    raise SystemExit("缺少依赖：请先运行 pip install pymupdf") from exc


DATE_RE = r"(20\d{2})\s*[\.\-/年]\s*(\d{1,2})\s*[\.\-/月]\s*(\d{1,2})"
CN_NO_RE = r"CN\s*\d[\d\s]*\s*[A-Z]"


@dataclass
class PatentRecord:
    source_file: str
    category: str          # 已授权 / 已申请 / 待核对
    title: str
    auth_publication_no: str = ""
    auth_publication_date: str = ""
    application_no: str = ""
    application_date: str = ""
    confidence: str = "高"
    note: str = ""

    @property
    def sort_date(self) -> str:
        if self.category == "已授权":
            return self.auth_publication_date
        if self.category == "已申请":
            return self.application_date
        return self.auth_publication_date or self.application_date


def normalize_text(text: str) -> str:
    """Normalize common PDF extraction artifacts while keeping line structure."""
    text = text.replace("\u3000", " ").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    # Repair spaces around decimal points in patent numbers/dates: 2020 .11 .19 -> 2020.11.19
    text = re.sub(r"\s*\.\s*", ".", text)
    return text


def compact(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def format_date_from_match(m: re.Match) -> str:
    y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
    return f"{y}.{mo:02d}.{d:02d}"


def normalize_date(s: str) -> str:
    m = re.search(DATE_RE, s or "")
    return format_date_from_match(m) if m else ""


def parse_date_for_sort(date_s: str) -> int:
    try:
        return datetime.strptime(date_s, "%Y.%m.%d").toordinal()
    except Exception:
        return 0


def normalize_cn_no(s: str) -> str:
    return compact(s).upper()


def extract_first_page_text(pdf_path: Path) -> str:
    with fitz.open(pdf_path) as doc:
        if doc.page_count == 0:
            return ""
        return normalize_text(doc[0].get_text("text"))


def extract_title(text: str) -> str:
    # Most CNIPA PDFs: (54)发明名称 ... (57)摘要
    patterns = [
        r"\(54\)\s*发明名称\s*(.*?)\s*\(57\)\s*摘要",
        r"发明名称\s*(.*?)\s*\(57\)",
        r"\(54\)\s*实用新型名称\s*(.*?)\s*\(57\)",
        r"\(54\)\s*外观设计名称\s*(.*?)\s*\(57\)",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.S)
        if m:
            title = compact(m.group(1))
            # Remove accidental field labels if OCR/text extraction over-captured.
            title = re.sub(r"^(发明名称|实用新型名称|外观设计名称)", "", title)
            return title
    return ""


def extract_field_after_label(text: str, label: str, value_pattern: str) -> str:
    # Example: (21)申请号 202311673161.2
    pat = rf"\({label}\)\s*[^\n]*?\s*({value_pattern})"
    m = re.search(pat, text)
    return m.group(1).strip() if m else ""


def extract_application_no(text: str) -> str:
    raw = extract_field_after_label(text, "21", r"[0-9][0-9\.\s]{6,}")
    return compact(raw)


def extract_application_date(text: str) -> str:
    # Keep it near (22) to avoid grabbing publication dates.
    m = re.search(r"\(22\)\s*申请日\s*" + DATE_RE, text)
    return format_date_from_match(m) if m else ""


def find_cn_number_date_pairs(text: str) -> list[tuple[str, str]]:
    """Find bottom/right-page pairs like 'CN 112613156 B\n2022.04.19'."""
    pairs: list[tuple[str, str]] = []
    pat = rf"({CN_NO_RE})\s*\n\s*({DATE_RE})"
    for m in re.finditer(pat, text):
        cn_no = normalize_cn_no(m.group(1))
        # Date groups are nested after group 2; easiest is normalize group 2.
        date_s = normalize_date(m.group(2))
        if cn_no and date_s:
            pairs.append((cn_no, date_s))
    return pairs


def find_cn_numbers(text: str, suffix: Optional[str] = None) -> list[str]:
    nums = []
    for m in re.finditer(CN_NO_RE, text):
        no = normalize_cn_no(m.group(0))
        if suffix is None or no.endswith(suffix.upper()):
            nums.append(no)
    # Stable de-duplication
    out = []
    for n in nums:
        if n not in out:
            out.append(n)
    return out


def extract_granted_info(text: str) -> tuple[str, str]:
    # Preferred: number/date pair printed at the right side/bottom of first page.
    for no, date_s in find_cn_number_date_pairs(text):
        if no.endswith("B"):
            return no, date_s

    # Fallback: explicit labels, if text extraction preserves values after the labels.
    no = extract_field_after_label(text, "10", CN_NO_RE)
    no = normalize_cn_no(no)
    if no and not no.endswith("B"):
        # Avoid accidentally taking application publication number CN...A for granted patent.
        no = ""
    if not no:
        b_nums = find_cn_numbers(text, "B")
        no = b_nums[0] if b_nums else ""

    m = re.search(r"\(45\)\s*授权公告日\s*(" + DATE_RE + r")", text)
    date_s = format_date_from_match(m) if m else ""
    return no, date_s


def detect_category(text: str, filename: str) -> str:
    fname = filename.upper()
    # (12)发明专利申请 means published application, not granted patent.
    if "(12)发明专利申请" in text or "专利申请" in text[:120]:
        return "已申请"
    if "(12)发明专利" in text and "(12)发明专利申请" not in text:
        return "已授权"
    if re.search(r"CN\d+[BSU]\.PDF$", fname):
        return "已授权"
    if re.search(r"CN\d+A\.PDF$", fname):
        return "已申请"
    # Last-resort classification by CN number suffixes found on first page.
    if find_cn_numbers(text, "B"):
        return "已授权"
    if find_cn_numbers(text, "A"):
        return "已申请"
    return "待核对"


def parse_pdf(pdf_path: Path) -> PatentRecord:
    text = extract_first_page_text(pdf_path)
    title = extract_title(text)
    category = detect_category(text, pdf_path.name)

    app_no = extract_application_no(text)
    app_date = extract_application_date(text)
    auth_no, auth_date = extract_granted_info(text) if category == "已授权" else ("", "")

    missing = []
    if not title:
        missing.append("专利名称")
    if category == "已授权":
        if not auth_no:
            missing.append("授权公告号")
        if not auth_date:
            missing.append("授权公告日")
    elif category == "已申请":
        if not app_no:
            missing.append("申请号")
        if not app_date:
            missing.append("申请日")
    else:
        missing.append("分类")

    confidence = "高" if not missing else "需人工核对"
    note = "" if not missing else "缺少：" + "、".join(missing)

    return PatentRecord(
        source_file=pdf_path.name,
        category=category,
        title=title,
        auth_publication_no=auth_no,
        auth_publication_date=auth_date,
        application_no=app_no,
        application_date=app_date,
        confidence=confidence,
        note=note,
    )


def iter_pdfs(input_path: Path) -> Iterable[Path]:
    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        yield input_path
    elif input_path.is_dir():
        for p in sorted(x for x in input_path.rglob("*") if x.is_file() and x.suffix.lower() == ".pdf"):
            yield p
    else:
        raise SystemExit(f"路径不是 PDF 文件或文件夹：{input_path}")


def sort_records(records: list[PatentRecord]) -> list[PatentRecord]:
    order = {"已授权": 0, "已申请": 1, "待核对": 2}
    return sorted(
        records,
        key=lambda r: (order.get(r.category, 9), -parse_date_for_sort(r.sort_date)),
    )


def build_catalog_text(records: list[PatentRecord]) -> str:
    """
    Build the final TXT catalog in the same structure as the reference image,
    but without dotted leaders or page numbers. Numbering continues across
    授权 and 申请 sections.
    """
    granted = [r for r in records if r.category == "已授权"]
    applied = [r for r in records if r.category == "已申请"]
    review = [r for r in records if r.category not in {"已授权", "已申请"}]

    lines: list[str] = []
    idx = 1

    lines.append("二、专利")
    lines.append("")

    lines.append("1、已授权")
    if granted:
        for r in granted:
            lines.append(
                f"（{idx}）{r.title}，授权公告号 {r.auth_publication_no}，授权公告日 {r.auth_publication_date}"
            )
            idx += 1
    else:
        lines.append("无")

    lines.append("")
    lines.append("2、已申请")
    if applied:
        for r in applied:
            lines.append(
                f"（{idx}）{r.title}，申请号 {r.application_no}，申请日 {r.application_date}"
            )
            idx += 1
    else:
        lines.append("无")

    if review:
        lines.append("")
        lines.append("3、待人工核对")
        for r in review:
            lines.append(f"（{idx}）{r.source_file}：{r.note}")
            idx += 1

    return "\n".join(lines) + "\n"


def write_csv(records: list[PatentRecord], csv_path: Path) -> None:
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        fieldnames = list(asdict(records[0]).keys()) if records else [
            "source_file", "category", "title", "auth_publication_no", "auth_publication_date",
            "application_no", "application_date", "confidence", "note"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))


def main() -> int:
    parser = argparse.ArgumentParser(description="批量识别中国专利 PDF 首页信息并生成目录条目。")
    parser.add_argument("input", type=Path, nargs="?", default=Path("sample_pdfs"), help="PDF 文件或包含 PDF 的文件夹（默认：sample_pdfs）")
    parser.add_argument("--out", type=Path, default=Path("专利目录.txt"), help="输出目录文本文件")
    parser.add_argument("--csv", type=Path, default=Path("专利信息.csv"), help="输出结构化 CSV 文件")
    args = parser.parse_args()

    records: list[PatentRecord] = []
    for pdf in iter_pdfs(args.input):
        try:
            records.append(parse_pdf(pdf))
        except Exception as e:
            records.append(PatentRecord(
                source_file=pdf.name,
                category="待核对",
                title="",
                confidence="需人工核对",
                note=f"读取失败：{e}",
            ))

    records = sort_records(records)
    catalog = build_catalog_text(records)

    args.out.write_text(catalog, encoding="utf-8")
    write_csv(records, args.csv)

    print(catalog)
    print(f"已输出：{args.out.resolve()}")
    print(f"已输出：{args.csv.resolve()}")

    need_review = [r for r in records if r.confidence != "高"]
    if need_review:
        print("\n以下文件建议人工复核：", file=sys.stderr)
        for r in need_review:
            print(f"- {r.source_file}: {r.note}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
