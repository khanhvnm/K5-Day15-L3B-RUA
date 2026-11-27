"""Script lấy mẫu ngẫu nhiên 300 review 1–2★ (seed cố định) phục vụ CP2-5 (gắn nhãn pain).

Đọc file review thô từ `docs/no_commit/reviews_food_2026.csv` (hoặc fallback `_local/reviews_food_2026.csv`),
loại bỏ hoàn toàn `user_hash`, che PII (SĐT / email / biển số nếu có), cắt trích dẫn tối đa 2 câu,
rồi chia đều 4 phần (75 dòng/người) + 1 tập 30 dòng gắn chung để kiểm độ khớp (IAA).

Chạy:
    python evidence/scripts/sample_reviews.py
"""

from __future__ import annotations

import csv
import os
import random
import re

SEED = 42
SAMPLE_SIZE = 300
OVERLAP_SIZE = 30

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRIMARY_INPUT = os.path.join(ROOT, "docs", "no_commit", "reviews_food_2026.csv")
FALLBACK_INPUT = os.path.join(ROOT, "_local", "reviews_food_2026.csv")
LABELS_DIR = os.path.join(ROOT, "evidence", "labels")

ALLOWED_APPS = {"shopeefood", "grab", "greensm", "be", "befood", "grabfood"}
FIELDS = [
    "app",
    "review_id",
    "date",
    "score",
    "thumbs_up",
    "trich_dan",
    "nhan",
    "ghi_chu",
]


def redact_pii(text: str) -> str:
    """Che SĐT, email hoặc biển số xe nếu xuất hiện trong nội dung review."""
    s = re.sub(r"(?<!\d)(?:\+84|0)(?:[\s.-]?\d){8,10}(?!\d)", "[SDT]", text)
    s = re.sub(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", "[EMAIL]", s)
    s = re.sub(r"\b\d{2}[A-Z]\d?[-\s]?\d{3,5}\.?\d{0,2}\b", "[BIEN_SO]", s)
    return s


def first_two_sentences(text: str) -> str:
    """Rút gọn trích dẫn tối đa 2 câu và làm sạch xuống dòng."""
    clean = " ".join((text or "").split())
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", clean) if p.strip()]
    short = " ".join(parts[:2]) if parts else clean
    return redact_pii(short)[:280]


def find_source_csv() -> str:
    if os.path.exists(PRIMARY_INPUT):
        return PRIMARY_INPUT
    if os.path.exists(FALLBACK_INPUT):
        return FALLBACK_INPUT
    raise FileNotFoundError(
        f"Không tìm thấy file review tại {PRIMARY_INPUT} hoặc {FALLBACK_INPUT}"
    )


def build_samples(seed: int = SEED) -> dict[str, list[dict]]:
    src = find_source_csv()
    with open(src, encoding="utf-8-sig", newline="") as f:
        raw_rows = list(csv.DictReader(f))

    eligible: list[dict] = []
    for r in raw_rows:
        app_low = (r.get("app") or "").strip().lower()
        score_s = str(r.get("score") or "").strip()
        content = (r.get("content") or "").strip()
        if app_low not in ALLOWED_APPS:
            continue
        if score_s not in ("1", "2"):
            continue
        if len(content) < 8:
            continue
        eligible.append(
            {
                "app": r.get("app", "").strip(),
                "review_id": (r.get("review_id") or "").strip(),
                "date": (r.get("date") or "").strip(),
                "score": score_s,
                "thumbs_up": str(r.get("thumbs_up") or "0").strip(),
                "trich_dan": first_two_sentences(content),
                "nhan": "",
                "ghi_chu": "",
            }
        )

    rng = random.Random(seed)
    chosen = rng.sample(eligible, min(SAMPLE_SIZE, len(eligible)))
    part_size = len(chosen) // 4
    parts = {
        "part1.csv": chosen[0:part_size],
        "part2.csv": chosen[part_size : 2 * part_size],
        "part3.csv": chosen[2 * part_size : 3 * part_size],
        "part4.csv": chosen[3 * part_size : 4 * part_size],
    }
    # Lấy 30 dòng từ part1 (phần Khánh) để Duy Thành gắn chéo độc lập vào file overlap riêng
    parts["overlap_30_thanh.csv"] = [
        dict(row) for row in parts["part1.csv"][:OVERLAP_SIZE]
    ]
    return parts


def main() -> int:
    os.makedirs(LABELS_DIR, exist_ok=True)
    parts = build_samples(SEED)
    for fname, rows in parts.items():
        out_path = os.path.join(LABELS_DIR, fname)
        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Đã ghi {len(rows)} dòng -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
