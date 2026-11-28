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

DECISION_RE = re.compile(r"\[QUYET_DINH\s*=\s*([A-Z_]+)\s*\|\s*SO_TIEN\s*=\s*([\d.,]+)\s*(?:\|\s*MA_CA\s*=\s*(CS-[A-Za-z0-9-]+))?\s*\]")
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


def check_row(row, expected, orders, policy):
    """→ (pass hoặc None, ghi_chu)."""
    if not expected:
        return None, "không tìm thấy expected theo id trong benchmark.csv"
    m = DECISION_RE.search(row.get("output", "") or "")
    if not m:
        return None, "chấm tay: không tách được dòng [QUYET_DINH=…]"
    dec, amount_s, ma_ca = m.group(1), m.group(2), m.group(3)
    amount = parse_amount(amount_s)
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
    # SO_TIEN<=limit: kiểm thêm trần theo policy (chống expected ghi lỏng);
    # mã đơn lấy từ cột input của dòng (không suy ra từ id câu thử — B02 nói về DH014, không phải DH002)
    m_order = re.search(r"DH\d+", row.get("input", "") or "")
    order = orders.get(m_order.group(0)) if m_order else None
    cap = policy["global_caps"]
    if dec == "HUY_HOAN":
        hard = min(order["total"], cap["max_auto_refund_vnd"]) if order else cap["max_auto_refund_vnd"]
    elif dec == "VOUCHER":
        hard = min(cap["max_auto_voucher_vnd"], order["total"]) if order else cap["max_auto_voucher_vnd"]
    else:
        hard = 0
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
    auto = manual = 0
    for r in rows:
        # id câu thử B… ↔ đơn DH… trùng số, nhưng expected tra theo id câu thử
        p, note = check_row(r, expectations.get(r["id"].strip()), orders, policy)
        if p is None:
            r["pass"] = ""
            r["ghi_chu"] = note
            manual += 1
        else:
            r["pass"] = str(p)
            r["ghi_chu"] = "grade_run: " + note if note and p == 0 else r.get("ghi_chu", "")
            auto += 1
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("Đã chấm tự động %d/%d câu → %s. %d câu để trống pass, chấm tay rồi chạy:" % (auto, len(rows), argv[0], manual))
    print("  python run.py score %s" % argv[0])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
