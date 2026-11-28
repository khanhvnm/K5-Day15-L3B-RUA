"""Script tổng hợp & kiểm tra chất lượng bộ 300 review đã gắn nhãn (CP3-4).

Đọc `part1.csv .. part4.csv` (75 dòng/file, N = 300) và `overlap_30_thanh.csv` (30 dòng)
tại `evidence/labels/`, kiểm tra hợp lệ mã nhãn / không sót nhãn / không rò PII,
tính bảng `x / 300 (%)`, tổng `thumbs_up`, độ khớp gắn nhãn chéo (`__/30`),
và trích xuất ví dụ an toàn (`<= 2` câu, kèm `app, date, review_id`) cho `evidence/data-mining.md`.

Chạy:
    python evidence/scripts/count_labels.py --status      # kiểm cấu trúc, PII & tiến độ gắn nhãn
    python evidence/scripts/count_labels.py --check       # bắt buộc đủ 300/300 & 30/30, hợp lệ 100%
    python evidence/scripts/count_labels.py --markdown    # xuất bảng §3 & trích dẫn §4 cho data-mining.md
    python evidence/scripts/count_labels.py --self-test   # tự kiểm bằng dữ liệu giả lập cô lập
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LABELS_DIR = ROOT / "evidence" / "labels"

PART_FILES: tuple[str, ...] = ("part1.csv", "part2.csv", "part3.csv", "part4.csv")
OVERLAP_FILE = "overlap_30_thanh.csv"
EXPECTED_PART_ROWS = 75
EXPECTED_TOTAL_ROWS = 300
EXPECTED_OVERLAP_ROWS = 30

EXPECTED_FIELDS: tuple[str, ...] = (
    "app",
    "review_id",
    "date",
    "score",
    "thumbs_up",
    "trich_dan",
    "nhan",
    "ghi_chu",
)

ALLOWED_LABELS: tuple[str, ...] = (
    "cho_tai_xe",
    "ghep_don",
    "giao_tre",
    "khong_huy_duoc",
    "cskh_khong_giai_quyet",
    "hoan_tien",
    "thieu_sai_mon",
    "khac",
)

HYPOTHESIS_LABELS = frozenset({"cho_tai_xe", "ghep_don", "giao_tre", "khong_huy_duoc"})

# Khớp cùng pattern PII trong sample_reviews.py (ngoài nhóm đã che [SDT]/[EMAIL]/[BIEN_SO])
_PHONE_RE = re.compile(r"(?<!\d)(?:\+84|0)(?:[\s.-]?\d){8,10}(?!\d)")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}")
_PLATE_RE = re.compile(r"\b\d{2}[A-Z]\d?[-\s]?\d{3,5}\.?\d{0,2}\b")


@dataclass
class ValidationReport:
    """Kết quả kiểm tra dữ liệu gắn nhãn theo từng file và toàn bộ mẫu."""

    part_rows: list[dict[str, str]]
    part1_rows: list[dict[str, str]]
    overlap_rows: list[dict[str, str]]
    per_file_progress: dict[str, tuple[int, int]]
    errors: list[str]
    warnings: list[str]


def _has_raw_pii(text: str) -> str | None:
    """Trả về loại PII nếu văn bản còn sót SĐT, email hoặc biển số chưa che."""
    if not text:
        return None
    if _PHONE_RE.search(text):
        return "so_dien_thoai"
    if _EMAIL_RE.search(text):
        return "email"
    if _PLATE_RE.search(text):
        return "bien_so"
    return None


def _parse_int(value: str, default: int = 0) -> int:
    try:
        return int((value or "").strip())
    except ValueError:
        return default


def _first_two_sentences(text: str) -> str:
    clean = " ".join((text or "").split())
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", clean) if p.strip()]
    return " ".join(parts[:2]) if parts else clean


def _load_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], [f"Thiếu file: {path}"]
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != EXPECTED_FIELDS:
            return [], [
                f"{path.name}: sai cột CSV (cần {list(EXPECTED_FIELDS)}, thấy {reader.fieldnames})"
            ]
        return list(reader), []


def _validate_rows(
    rows: list[dict[str, str]],
    source_name: str,
    seen_ids: set[str],
    *,
    require_complete: bool,
    allowed_parent_ids: set[str] | None = None,
) -> tuple[int, list[str]]:
    """Kiểm tra ID trùng, mã nhãn hợp lệ và rò rỉ PII trên danh sách dòng CSV."""
    labeled = 0
    errors: list[str] = []
    for idx, row in enumerate(rows, start=2):
        rid = (row.get("review_id") or "").strip()
        if not rid:
            errors.append(f"{source_name}:{idx}: thiếu review_id")
        elif rid in seen_ids:
            errors.append(f"{source_name}:{idx}: trùng review_id '{rid}'")
        else:
            seen_ids.add(rid)

        if allowed_parent_ids is not None and rid and rid not in allowed_parent_ids:
            errors.append(
                f"{source_name}:{idx}: review_id '{rid}' không thuộc part1.csv"
            )

        label = (row.get("nhan") or "").strip()
        if label:
            labeled += 1
            if label not in ALLOWED_LABELS:
                errors.append(f"{source_name}:{idx}: mã nhãn không hợp lệ '{label}'")
        elif require_complete:
            errors.append(f"{source_name}:{idx}: chưa điền cột nhan ({rid})")

        for col in ("trich_dan", "ghi_chu"):
            pii = _has_raw_pii(row.get(col) or "")
            if pii:
                errors.append(
                    f"{source_name}:{idx}: phát hiện {pii} chưa che trong '{col}'"
                )
    return labeled, errors


def validate_dataset(labels_dir: Path, *, require_complete: bool) -> ValidationReport:
    """Đọc 4 file part + 1 file overlap, kiểm tra cấu trúc, mã nhãn và PII."""
    errors: list[str] = []
    warnings: list[str] = []
    part_rows: list[dict[str, str]] = []
    part1_rows: list[dict[str, str]] = []
    per_file_progress: dict[str, tuple[int, int]] = {}
    seen_ids: set[str] = set()

    for fname in PART_FILES:
        rows, file_errs = _load_csv(labels_dir / fname)
        errors.extend(file_errs)
        if file_errs:
            per_file_progress[fname] = (0, 0)
            continue

        if len(rows) != EXPECTED_PART_ROWS:
            msg = f"{fname}: cần {EXPECTED_PART_ROWS} dòng, hiện có {len(rows)}"
            warnings.append(msg)
            if require_complete:
                errors.append(msg)

        labeled, row_errs = _validate_rows(
            rows, fname, seen_ids, require_complete=require_complete
        )
        errors.extend(row_errs)
        per_file_progress[fname] = (labeled, len(rows))
        part_rows.extend(rows)
        if fname == "part1.csv":
            part1_rows = rows

    overlap_rows, ov_errs = _load_csv(labels_dir / OVERLAP_FILE)
    errors.extend(ov_errs)
    if not ov_errs:
        if len(overlap_rows) != EXPECTED_OVERLAP_ROWS:
            msg = (
                f"{OVERLAP_FILE}: cần {EXPECTED_OVERLAP_ROWS} dòng, "
                f"hiện có {len(overlap_rows)}"
            )
            warnings.append(msg)
            if require_complete:
                errors.append(msg)
        part1_ids = {(r.get("review_id") or "").strip() for r in part1_rows}
        ov_labeled, row_errs = _validate_rows(
            overlap_rows,
            OVERLAP_FILE,
            set(),
            require_complete=require_complete,
            allowed_parent_ids=part1_ids or None,
        )
        errors.extend(row_errs)
        per_file_progress[OVERLAP_FILE] = (ov_labeled, len(overlap_rows))
    else:
        per_file_progress[OVERLAP_FILE] = (0, 0)

    return ValidationReport(
        part_rows=part_rows,
        part1_rows=part1_rows,
        overlap_rows=overlap_rows,
        per_file_progress=per_file_progress,
        errors=errors,
        warnings=warnings,
    )


def summarize_labels(report: ValidationReport) -> dict:
    """Tổng hợp số lượng, phần trăm (trên N thực tế), tổng thumbs_up, IAA và theo app."""
    n_total = len(report.part_rows) or EXPECTED_TOTAL_ROWS
    counts = {label: 0 for label in ALLOWED_LABELS}
    secondary_counts = {label: 0 for label in ALLOWED_LABELS}
    any_mention_counts = {label: 0 for label in ALLOWED_LABELS}
    thumbs = {label: 0 for label in ALLOWED_LABELS}
    unknown = 0
    labeled_rows: list[dict[str, str]] = []
    by_app: dict[str, dict] = {}

    for row in report.part_rows:
        label = (row.get("nhan") or "").strip()
        if not label:
            continue
        if label not in counts:
            unknown += 1
            continue
        app = (row.get("app") or "").strip() or "Khac"
        tu = _parse_int(row.get("thumbs_up") or "0")
        counts[label] += 1
        thumbs[label] += tu
        labeled_rows.append(row)

        app_bucket = by_app.setdefault(
            app,
            {
                "total": 0,
                "thumbs_up": 0,
                "counts": {lbl: 0 for lbl in ALLOWED_LABELS},
                "hypothesis_count": 0,
            },
        )
        app_bucket["total"] += 1
        app_bucket["thumbs_up"] += tu
        app_bucket["counts"][label] += 1
        if label in HYPOTHESIS_LABELS:
            app_bucket["hypothesis_count"] += 1

        # Thống kê nhãn phụ (ghi_chu cách nhau bởi ';')
        sec_tokens = [
            tok.strip()
            for tok in re.split(r"[;,|]", row.get("ghi_chu") or "")
            if tok.strip() in counts and tok.strip() != label
        ]
        mentioned = {label, *sec_tokens}
        for tok in set(sec_tokens):
            secondary_counts[tok] += 1
        for m in mentioned:
            any_mention_counts[m] += 1

    hypothesis_count = sum(counts[lbl] for lbl in HYPOTHESIS_LABELS)
    hypothesis_pct = (hypothesis_count / n_total * 100.0) if n_total else 0.0

    # Tính độ khớp gắn nhãn chéo trên cặp part1.csv <-> overlap_30_thanh.csv
    part1_by_id = {
        (r.get("review_id") or "").strip(): (r.get("nhan") or "").strip()
        for r in report.part1_rows
    }
    paired_labeled = 0
    matches = 0
    mismatches: list[tuple[str, str, str]] = []
    for row in report.overlap_rows:
        rid = (row.get("review_id") or "").strip()
        ov_label = (row.get("nhan") or "").strip()
        p1_label = part1_by_id.get(rid, "")
        if not ov_label or not p1_label:
            continue
        paired_labeled += 1
        if ov_label == p1_label:
            matches += 1
        else:
            mismatches.append((rid, p1_label, ov_label))

    # Chọn tối đa 2 ví dụ nhiều thumbs_up nhất cho mỗi nhãn
    top_quotes: list[dict[str, str]] = []
    for label in ALLOWED_LABELS:
        candidates = [r for r in labeled_rows if (r.get("nhan") or "").strip() == label]
        candidates.sort(
            key=lambda r: (
                _parse_int(r.get("thumbs_up") or "0"),
                r.get("review_id") or "",
            ),
            reverse=True,
        )
        for best in candidates[:2]:
            top_quotes.append(
                {
                    "nhan": label,
                    "app": (best.get("app") or "").strip(),
                    "date": (best.get("date") or "").strip(),
                    "review_id": (best.get("review_id") or "").strip(),
                    "thumbs_up": str(_parse_int(best.get("thumbs_up") or "0")),
                    "ghi_chu": (best.get("ghi_chu") or "").strip(),
                    "trich_dan": _first_two_sentences(best.get("trich_dan") or ""),
                }
            )

    return {
        "n_total": n_total,
        "labeled_total": len(labeled_rows),
        "unknown_total": unknown,
        "counts": counts,
        "secondary_counts": secondary_counts,
        "any_mention_counts": any_mention_counts,
        "thumbs": thumbs,
        "by_app": by_app,
        "hypothesis_count": hypothesis_count,
        "hypothesis_pct": hypothesis_pct,
        "overlap_total": len(report.overlap_rows) or EXPECTED_OVERLAP_ROWS,
        "iaa_paired": paired_labeled,
        "iaa_matches": matches,
        "iaa_mismatches": mismatches,
        "top_quotes": top_quotes,
        "warnings": report.warnings,
    }


def render_status(report: ValidationReport, summary: dict) -> str:
    """In tóm tắt tiến độ gắn nhãn và trạng thái kiểm tra PII/schema."""
    lines = ["Trang thai bo review (CP2-5 -> CP3-4):"]
    for fname in (*PART_FILES, OVERLAP_FILE):
        done, total = report.per_file_progress.get(fname, (0, 0))
        lines.append(f"  - {fname}: {done}/{total} dong da gan nhan")
    lines.append(
        f"  - Tong da gan nhan (part1..4): {summary['labeled_total']}/{summary['n_total']}"
    )
    lines.append(
        f"  - Do khop gan nhan cheo: {summary['iaa_matches']}/{summary['iaa_paired']} "
        f"(muc tieu {summary['overlap_total']}/{summary['overlap_total']})"
    )
    if report.warnings:
        lines.append(f"  - Luu y so dong ({len(report.warnings)}):")
        for w in report.warnings:
            lines.append(f"      * {w}")
    if report.errors:
        lines.append(f"  - Canh bao/Loi ({len(report.errors)}):")
        for err in report.errors[:20]:
            lines.append(f"      * {err}")
    else:
        lines.append("  - Schema & PII: dat (0 loi)")
    return "\n".join(lines)


def render_markdown(summary: dict) -> str:
    """Xuất Markdown sẵn sàng dán vào `evidence/data-mining.md` §3 và §4."""
    n_total = summary["n_total"]
    counts = summary["counts"]
    sec_counts = summary["secondary_counts"]
    any_counts = summary["any_mention_counts"]
    thumbs = summary["thumbs"]
    lines = [
        f"## 3. Kết quả tổng hợp (`N = {n_total}`)",
        "",
        "| Đếm gì | x / N | % | Nhắc ở nhãn phụ | Tổng lần nhắc | Tổng thumbs_up | Ghi chú |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for label in ALLOWED_LABELS:
        cnt = counts[label]
        pct = (cnt / n_total * 100.0) if n_total else 0.0
        note = "Nhóm giả thuyết D1" if label in HYPOTHESIS_LABELS else ""
        lines.append(
            f"| `{label}` | `{cnt}/{n_total}` | `{pct:.1f}%` | {sec_counts[label]} | "
            f"{any_counts[label]} (`{any_counts[label] / n_total * 100:.1f}%`) | {thumbs[label]} | {note} |"
        )

    hyp_cnt = summary["hypothesis_count"]
    hyp_pct = summary["hypothesis_pct"]
    ov_total = summary["overlap_total"]
    iaa_m = summary["iaa_matches"]
    iaa_p = summary["iaa_paired"]
    iaa_pct = (iaa_m / iaa_p * 100.0) if iaa_p else 0.0
    hyp_label_expr = " + ".join(sorted(HYPOTHESIS_LABELS))
    lines.extend(
        [
            "",
            (
                f"- Nhóm kẹt/ghép đơn/trễ/không hủy được (`{hyp_label_expr}`): "
                f"`{hyp_cnt}/{n_total}` (`{hyp_pct:.1f}%`) — ngưỡng giả thuyết `>= 40%`."
            ),
            (
                f"- Độ khớp gắn nhãn chéo (`{ov_total}` dòng chung: Duy Thành ↔ part1 do AI gợi ý, Khánh duyệt): "
                f"`{iaa_m}/{ov_total}` (`{iaa_pct:.1f}%` trên {iaa_p} cặp đã gắn đủ)."
            ),
        ]
    )
    if summary["warnings"]:
        lines.append(f"- Lưu ý kiểm tra mẫu: {'; '.join(summary['warnings'])}.")

    lines.extend(
        [
            "",
            "### Phân bổ theo từng ứng dụng",
            "",
            "| Ứng dụng | Số dòng | Nhóm D1 (`x/app`, `%`) | Tổng thumbs_up | Top lỗi chính |",
            "|---|---:|---:|---:|---|",
        ]
    )
    app_order = ("ShopeeFood", "Grab", "GreenSM", "be")
    sorted_apps = sorted(
        summary["by_app"].keys(),
        key=lambda a: (app_order.index(a) if a in app_order else 99, a),
    )
    for app in sorted_apps:
        b = summary["by_app"][app]
        a_total = b["total"]
        a_hyp = b["hypothesis_count"]
        a_pct = (a_hyp / a_total * 100.0) if a_total else 0.0
        top3 = sorted(b["counts"].items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        top_str = ", ".join(f"`{k}` ({v})" for k, v in top3 if v > 0)
        lines.append(
            f"| {app} | {a_total} | `{a_hyp}/{a_total}` (`{a_pct:.1f}%`) | {b['thumbs_up']} | {top_str} |"
        )

    lines.extend(["", "## 4. Ví dụ cụ thể kiểm chứng được", ""])
    if not summary["top_quotes"]:
        lines.append("*(Chưa có dòng nào được gắn nhãn trong `part1..4.csv`.)*")
    else:
        for idx, q in enumerate(summary["top_quotes"], start=1):
            extra = f", `ghi_chu={q['ghi_chu']}`" if q["ghi_chu"] else ""
            lines.append(
                f'{idx}. **`{q["nhan"]}`** — "{q["trich_dan"]}" '
                f"(`app={q['app']}`, `date={q['date']}`, `review_id={q['review_id']}`, `thumbs_up={q['thumbs_up']}`{extra})"
            )
    return "\n".join(lines)


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(EXPECTED_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def run_self_tests() -> int:
    """Tự kiểm tra logic đếm x/300, IAA, phát hiện mã nhãn sai và phát hiện PII."""
    label_cycle = [
        *["cho_tai_xe"] * 45,
        *["ghep_don"] * 45,
        *["giao_tre"] * 45,
        *["khong_huy_duoc"] * 15,  # nhom gia thuyet = 150/300 = 50.0% >= 40%
        *["cskh_khong_giai_quyet"] * 60,
        *["hoan_tien"] * 30,
        *["thieu_sai_mon"] * 30,
        *["khac"] * 30,
    ]
    assert len(label_cycle) == EXPECTED_TOTAL_ROWS

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        all_rows: list[dict[str, str]] = []
        for idx, lbl in enumerate(label_cycle):
            all_rows.append(
                {
                    "app": "ShopeeFood" if idx % 2 == 0 else "Grab",
                    "review_id": f"rev-{idx:03d}",
                    "date": "2026-08-01",
                    "score": "1",
                    "thumbs_up": str((idx % 5) + 1),
                    "trich_dan": f"Don {idx} gap su co [SDT]. Cho mai khong xong.",
                    "nhan": lbl,
                    "ghi_chu": "",
                }
            )
        for p_idx, fname in enumerate(PART_FILES):
            chunk = all_rows[
                p_idx * EXPECTED_PART_ROWS : (p_idx + 1) * EXPECTED_PART_ROWS
            ]
            _write_csv(d / fname, chunk)

        overlap = [dict(r) for r in all_rows[:EXPECTED_OVERLAP_ROWS]]
        for j in range(3):
            overlap[j]["nhan"] = "khac"
        _write_csv(d / OVERLAP_FILE, overlap)

        rep = validate_dataset(d, require_complete=True)
        assert not rep.errors, f"Self-test lỗi không mong đợi: {rep.errors}"
        summary = summarize_labels(rep)
        assert summary["labeled_total"] == 300
        assert summary["counts"]["cho_tai_xe"] == 45
        assert summary["hypothesis_count"] == 150
        assert abs(summary["hypothesis_pct"] - 50.0) < 1e-6
        assert summary["iaa_matches"] == 27
        assert summary["iaa_paired"] == 30
        assert summary["thumbs"]["cho_tai_xe"] == sum((i % 5) + 1 for i in range(45))
        md = render_markdown(summary)
        assert "`150/300` (`50.0%`)" in md
        assert "`27/30`" in md
        assert summary["by_app"]["ShopeeFood"]["total"] == 150
        assert summary["by_app"]["Grab"]["total"] == 150

        # Kiểm tra thiếu 1 dòng ở part4: --check báo lỗi nhưng --markdown dùng N=299 trung thực
        short_part4 = [dict(r) for r in all_rows[3 * EXPECTED_PART_ROWS :]]
        _write_csv(d / "part4.csv", short_part4[:-1])
        strict_short = validate_dataset(d, require_complete=True)
        assert any("cần 75 dòng, hiện có 74" in e for e in strict_short.errors)
        relaxed_short = validate_dataset(d, require_complete=False)
        assert not relaxed_short.errors
        short_summary = summarize_labels(relaxed_short)
        assert short_summary["n_total"] == 299
        assert "ShopeeFood" in short_summary["by_app"]

        # Kiểm tra bắt lỗi mã nhãn lạ và PII chưa che
        bad_part = [dict(r) for r in all_rows[:EXPECTED_PART_ROWS]]
        bad_part[0]["nhan"] = "nhan_khong_ton_tai"
        bad_part[1]["trich_dan"] = "Goi so 0912345678 de hoan tien"
        _write_csv(d / "part1.csv", bad_part)
        bad_rep = validate_dataset(d, require_complete=True)
        assert any("ma nhan" in e or "mã nhãn" in e for e in bad_rep.errors), (
            bad_rep.errors
        )
        assert any("so_dien_thoai" in e for e in bad_rep.errors), bad_rep.errors

        # Kiểm tra --check từ chối dòng chưa gắn nhãn
        empty_part = [dict(r) for r in all_rows[:EXPECTED_PART_ROWS]]
        empty_part[0]["nhan"] = ""
        _write_csv(d / "part1.csv", empty_part)
        incomplete_strict = validate_dataset(d, require_complete=True)
        assert any("chưa điền cột nhan" in e for e in incomplete_strict.errors), (
            incomplete_strict.errors
        )
        incomplete_status = validate_dataset(d, require_complete=False)
        assert not incomplete_status.errors, incomplete_status.errors

    print("SELF_TEST_OK: 4/4 assertions passed")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tổng hợp và kiểm tra bộ nhãn 300 review (CP3-4)."
    )
    parser.add_argument(
        "--labels-dir",
        type=Path,
        default=DEFAULT_LABELS_DIR,
        help="Thư mục chứa part1..4.csv và overlap_30_thanh.csv",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Chỉ kiểm cấu trúc/PII và in tiến độ gắn nhãn",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Kiểm tra nghiêm ngặt: đủ 300/300 + 30/30, hợp lệ mã nhãn và không rò PII",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="In bảng Markdown §3 và ví dụ §4 cho evidence/data-mining.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Chạy bộ tự kiểm tra bằng dữ liệu giả lập trong thư mục tạm",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    # Đảm bảo console Windows UTF-8 không lỗi dấu tiếng Việt
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    args = _build_parser().parse_args(argv)
    if args.self_test:
        return run_self_tests()

    report = validate_dataset(args.labels_dir, require_complete=args.check)
    summary = summarize_labels(report)

    if args.markdown:
        print(render_markdown(summary))
        if report.errors:
            print(render_status(report, summary), file=sys.stderr)
            return 1
        return 0

    if args.status or report.errors or summary["labeled_total"] < EXPECTED_TOTAL_ROWS:
        out = sys.stderr if report.errors else sys.stdout
        print(render_status(report, summary), file=out)
        return 1 if report.errors else 0

    print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
