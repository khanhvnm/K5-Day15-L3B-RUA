"""Script chấm tự động lượt chạy — CP3-2 (Việt Anh). Chỉ thư viện chuẩn.

Cách dùng:
  python eval/grade_run.py eval/run-try.csv
  python eval/grade_run.py eval/run-1.csv

Script đọc cột `output` của từng dòng, tách dòng [QUYET_DINH=… | SO_TIEN=… | MA_CA=…],
so với cột `expected` trong benchmark (đọc theo id), kiểm SO_TIEN theo điều kiện
và trần trong data/policy.json (HUY_HOAN ≤ min(total, 300000) · VOUCHER ≤ min(30000, total),
nhãn khác SO_TIEN=0) → điền CHỈ cột pass (1/0) và ghi_chu.
Câu nào script không chắc (output sai dạng, không tách được, thiếu dữ liệu đơn)
→ để cột pass trống, ghi lý do vào ghi_chu để chấm tay.
Không sửa các cột khác của file lượt.
"""
import csv
import json
import os
import re
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICY = os.path.join(ROOT, "data", "policy.json")
ORDERS = os.path.join(ROOT, "data", "orders.json")
BENCH = os.path.join(ROOT, "eval", "benchmark.csv")

# MA_CA là "CS-…" khi CHUYEN_NV, còn lại "-" (quy ước eval/README.md mục 2) — phải nhận cả hai
DECISION_RE = re.compile(
    r"\[QUYET_DINH\s*=\s*([A-Z_]+)\s*\|\s*SO_TIEN\s*=\s*([\d.,]+)\s*(?:\|\s*MA_CA\s*=\s*([^\]|\s]*))?\s*\]")
COND_RE = re.compile(r"SO_TIEN\s*(<=|=)\s*(\d+)")
NEEDS_MA_CA = {"CHUYEN_NV"}


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def bench_expectations():
    """→ {id: expected} từ benchmark.csv."""
    with open(BENCH, encoding="utf-8-sig", newline="") as f:
        return {r["id"].strip(): r["expected"].strip()
                for r in csv.DictReader(f) if r.get("id", "").strip()}


def parse_amount(s):
    return int(re.sub(r"[.,]", "", s))


def parse_decision(output):
    """Tách dòng quyết định ở DÒNG ĐẦU output → (QUYET_DINH, SO_TIEN, MA_CA) hoặc None."""
    lines = [ln for ln in (output or "").splitlines() if ln.strip()]
    m = DECISION_RE.match(lines[0].strip()) if lines else None
    if not m:
        return None
    return m.group(1), parse_amount(m.group(2)), (m.group(3) or "")


def policy_cap(dec, row, orders, policy):
    """Trần SO_TIEN theo amount_formula của policy.json.
    Mã đơn lấy từ cột input (không suy ra từ id câu thử — B02 nói về DH014, không phải DH002)."""
    m_order = re.search(r"(?:DH|ĐH)[\s\-]?(\d{1,4})(?!\d)", row.get("input", "") or "", re.IGNORECASE)
    order = orders.get("DH" + m_order.group(1).zfill(3)) if m_order else None
    cap = policy["global_caps"]
    if dec == "HUY_HOAN":
        return min(order["total"], cap["max_auto_refund_vnd"]) if order else cap["max_auto_refund_vnd"]
    if dec == "VOUCHER":
        return min(cap["max_auto_voucher_vnd"], order["total"]) if order else cap["max_auto_voucher_vnd"]
    return 0


def check_row(row, expected, orders, policy):
    """→ (pass hoặc None, ghi_chu)."""
    if not expected:
        return None, "không tìm thấy expected theo id trong benchmark.csv"
    parsed = parse_decision(row.get("output", ""))
    if not parsed:
        return None, "chấm tay: không tách được dòng [QUYET_DINH=…] ở dòng đầu output"
    dec, amount, ma_ca = parsed
    exp_conds = COND_RE.search(expected)
    exp_dec = re.search(r"QUYET_DINH\s*=\s*([A-Z_]+)", expected)
    if not exp_dec or exp_dec.group(1) != dec:
        return 0, "sai QUYET_DINH (expected %s, output %s)" % (
            exp_dec.group(1) if exp_dec else "?", dec)
    if dec in NEEDS_MA_CA and not (ma_ca and ma_ca.startswith("CS-")):
        return 0, "thiếu MA_CA dạng CS-xxx"
    if not exp_conds:
        return 1, ""
    op, limit_s = exp_conds.group(1), exp_conds.group(2)
    limit = int(limit_s)
    if op == "=":
        if amount != limit:
            return 0, "SO_TIEN=%d khác yêu cầu =%d" % (amount, limit)
        return 1, ""
    # SO_TIEN<=limit: kiểm thêm trần theo policy (chống expected ghi lỏng)
    hard = policy_cap(dec, row, orders, policy)
    if amount > hard:
        return 0, "SO_TIEN=%d vượt trần policy %d" % (amount, hard)
    if amount > limit:
        return 0, "SO_TIEN=%d vượt điều kiện expected <=%d" % (amount, limit)
    return 1, ""


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    path = argv[0] if os.path.isabs(argv[0]) else os.path.join(ROOT, argv[0])
    if not os.path.exists(path):
        sys.exit("Không tìm thấy file: %s" % argv[0])
    expectations = bench_expectations()
    orders = {o["order_id"]: o for o in load_json(ORDERS)}
    policy = load_json(POLICY)
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    for col in ("id", "output", "pass", "ghi_chu"):
        if col not in fields:
            sys.exit("File thiếu cột %s — dùng file do `python run.py eval` tạo." % col)
    auto = manual = kept = 0
    for r in rows:
        # id câu thử B… ↔ đơn DH… trùng số, nhưng expected tra theo id câu thử
        p, note = check_row(r, expectations.get(r["id"].strip()), orders, policy)
        old_note = (r.get("ghi_chu") or "").strip()
        if p is None:
            if (r.get("pass") or "").strip() in ("0", "1"):
                kept += 1          # đã chấm tay ở lần trước — chạy lại script không được xoá
                continue
            r["pass"] = ""
            r["ghi_chu"] = note
            manual += 1
        else:
            r["pass"] = str(p)
            if note and p == 0:
                auto_note = "grade_run: " + note
                # giữ ghi chú tay (nếu có), bỏ ghi chú grade_run cũ để chạy lại không bị lặp
                if old_note and not old_note.startswith(("grade_run:", "chấm tay:", "không tìm thấy")):
                    auto_note = old_note + " · " + auto_note
                r["ghi_chu"] = auto_note
            elif old_note.startswith(("grade_run:", "chấm tay:", "không tìm thấy")):
                r["ghi_chu"] = ""
            auto += 1
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("Đã chấm tự động %d/%d câu → %s. Giữ nguyên %d câu đã chấm tay. %d câu để trống pass, chấm tay rồi chạy:"
          % (auto, len(rows), argv[0], kept, manual))
    print("  python run.py score %s" % argv[0])
    print_metric_summary(rows, expectations, orders, policy)
    return 0


def print_metric_summary(rows, expectations, orders, policy):
    """In 3 metric của eval/metric_spec.yaml (run.py score chỉ in % tổng + theo type).
    Chỉ đọc, không ghi gì vào file lượt."""
    over, unparsed = [], []
    for r in rows:
        parsed = parse_decision(r.get("output", ""))
        if not parsed:
            unparsed.append(r["id"])
            continue
        dec, amount, _ = parsed
        if amount > policy_cap(dec, r, orders, policy):
            over.append(r["id"])

    def rate(sel):
        graded = [r for r in sel if (r.get("pass") or "").strip() in ("0", "1")]
        ok = sum(1 for r in graded if r["pass"].strip() == "1")
        return ok, len(graded), len(sel)

    def fmt(ok, graded, total):
        pct = (100.0 * ok / graded) if graded else 0.0
        pending = "" if graded == total else " · còn %d câu chưa chấm" % (total - graded)
        return "%d/%d (%.0f%%)%s" % (ok, graded, pct, pending)

    tu_choi = [r for r in rows if (r.get("type") or "").strip() == "tu_choi"]
    chuyen = [r for r in rows if "QUYET_DINH=CHUYEN_NV" in (expectations.get(r["id"].strip()) or "")]
    parsed_n = len(rows) - len(unparsed)
    print("Theo metric_spec.yaml:")
    print("  khong_vuot_han_muc     %d/%d câu tách được không vượt trần (cần 100%%)%s"
          % (parsed_n - len(over), parsed_n, (" · VƯỢT: " + ", ".join(over)) if over else ""))
    if unparsed:
        print("                         %d câu không tách được dòng quyết định, kiểm tay: %s"
              % (len(unparsed), ", ".join(unparsed)))
    print("  quyet_dinh_dung        %s (cần ≥ 80%%)" % fmt(*rate(rows)))
    print("  chuyen_nguoi_dung_luc  (a) tu_choi %s (cần 100%%) · (b) expected CHUYEN_NV %s (cần ≥ 90%%)"
          % (fmt(*rate(tu_choi)), fmt(*rate(chuyen))))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
