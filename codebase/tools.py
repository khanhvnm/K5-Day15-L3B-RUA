"""Công cụ của bài toán — FoodResolve AI (Track D1 · Team RUA).

Gồm đúng 5 công cụ gắn @tool:
  1. get_order(order_id) — tra cứu đơn hàng + tính thời gian/hợp lệ trạng thái bằng code
  2. get_policy(issue_type) — đọc chính sách & ngưỡng bồi thường từ data/policy.json
  3. get_complaint_history(user_id) — tra cứu số lần khiếu nại trong tháng của user
  4. check_limit(issue_type, amount, order, complaints_in_month, request_type) — cổng kiểm soát hạn mức tất định
  5. escalate_to_human(case_id, reason) — tạo bản nháp mã ca CS-xxx chờ nhân viên duyệt
"""
import copy
from datetime import datetime
import json
import os
import re
from typing import Optional

from tracing import tool, TOOLS  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

_PII_FIELDS = {
    "phone",
    "address",
    "sdt",
    "dia_chi",
    "email",
    "driver_phone",
    "driver_address",
    "customer_phone",
    "customer_address",
}

# Cache đọc file theo mtime để tránh đọc lại JSON nhiều lần trong cùng 1 lượt xử lý
_DATA_CACHE: dict = {}

# Theo dõi bồi thường trùng trong cùng một phiên (opt-in theo session_id cho demo nhiều lượt)
SESSION_COMPENSATIONS: dict = {}


def _read_data(filename: str):
    """Đọc file nguồn sự thật trong data/ (có cache theo mtime). Thiếu file thì báo lỗi."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Thiếu {path} — chạy `python data/gen_orders.py` để sinh lại dữ liệu."
        )
    mtime_ns = os.stat(path).st_mtime_ns
    cached = _DATA_CACHE.get(path)
    if cached and cached[0] == mtime_ns:
        return copy.deepcopy(cached[1])
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    _DATA_CACHE[path] = (mtime_ns, data)
    return copy.deepcopy(data)


def _normalize_order_id(order_id: str) -> str:
    raw = str(order_id or "").strip().replace("đ", "D").replace("Đ", "D").upper()
    raw = re.sub(r"[#\s\-]+", "", raw)
    m = re.fullmatch(r"DH(\d{1,4})", raw)
    return "DH" + m.group(1).zfill(3) if m else raw


def _compute_minutes(order: dict) -> tuple:
    placed_dt = datetime.fromisoformat(order["placed_at"])
    eta_dt = datetime.fromisoformat(order["eta"])
    now_dt = datetime.fromisoformat(order["now"])
    phut_tu_luc_dat = int((now_dt - placed_dt).total_seconds() // 60)
    phut_tre_so_voi_eta = int((now_dt - eta_dt).total_seconds() // 60)
    return phut_tu_luc_dat, phut_tre_so_voi_eta


def record_session_compensation(session_id: str, order_id: str, decision: str) -> None:
    """Ghi nhận đề xuất bồi thường đã tạo trong một phiên hội thoại (chỉ dùng khi truyền session_id)."""
    if not session_id or decision not in ("HUY_HOAN", "VOUCHER"):
        return
    oid = _normalize_order_id(order_id)
    SESSION_COMPENSATIONS.setdefault(session_id, set()).add((oid, decision))


def has_session_compensation(session_id: Optional[str], order_id: str, decision: str) -> bool:
    """Kiểm tra cặp (order_id, loại bồi thường) đã được tạo trong phiên hay chưa."""
    if not session_id or decision not in ("HUY_HOAN", "VOUCHER"):
        return False
    oid = _normalize_order_id(order_id)
    return (oid, decision) in SESSION_COMPENSATIONS.get(session_id, set())


def reset_session_compensations(session_id: Optional[str] = None) -> None:
    """Xóa lịch sử bồi thường phiên (1 phiên hoặc toàn bộ)."""
    if session_id is None:
        SESSION_COMPENSATIONS.clear()
    else:
        SESSION_COMPENSATIONS.pop(session_id, None)


@tool
def get_order(order_id: str) -> dict:
    """Tên: get_order — Tra cứu đơn hàng từ data/orders.json và tính số phút/hợp lệ trạng thái bằng code.
    Input: order_id (str, chấp nhận biến thể chữ hoa/thường, có dấu # hoặc -).
    Output: dict thông tin đơn (đã bỏ trường PII) kèm 'found', 'phut_tu_luc_dat', 'phut_tre_so_voi_eta', 'trang_thai_hop_le'; hoặc {'found': False, 'order_id': ...}.
    Tác động ra ngoài: Không (chỉ đọc)."""
    normalized_id = _normalize_order_id(order_id)
    if not normalized_id:
        return {"found": False, "order_id": ""}

    orders = _read_data("orders.json")
    policy = _read_data("policy.json")
    valid_combos = policy.get("valid_status_combos", {})

    for item in orders:
        if _normalize_order_id(item.get("order_id", "")) == normalized_id:
            clean = {k: v for k, v in item.items() if k not in _PII_FIELDS}
            phut_tu_luc_dat, phut_tre_so_voi_eta = _compute_minutes(clean)
            status = clean.get("status", "")
            driver_status = clean.get("driver_status", "")
            trang_thai_hop_le = driver_status in valid_combos.get(status, [])
            clean["found"] = True
            clean["phut_tu_luc_dat"] = phut_tu_luc_dat
            clean["phut_tre_so_voi_eta"] = phut_tre_so_voi_eta
            clean["trang_thai_hop_le"] = trang_thai_hop_le
            return clean

    return {"found": False, "order_id": normalized_id}


@tool
def get_policy(issue_type: str = "all") -> dict:
    """Tên: get_policy — Đọc chính sách bồi thường và các ngưỡng từ data/policy.json.
    Input: issue_type (str, mặc định 'all' để lấy toàn bộ, hoặc tên 1 rule cụ thể trong policy).
    Output: dict gồm 'global_caps', 'valid_status_combos', 'rules' (khi 'all') hoặc rule tương ứng + 'global_caps'; không thấy trả {'found': False, 'issue_type': ...}.
    Tác động ra ngoài: Không (chỉ đọc)."""
    policy = _read_data("policy.json")
    key = (issue_type or "").strip()
    if not key or key.lower() == "all":
        return {
            "global_caps": policy.get("global_caps", {}),
            "valid_status_combos": policy.get("valid_status_combos", {}),
            "rules": policy.get("rules", []),
        }

    for rule in policy.get("rules", []):
        if rule.get("issue_type") == key:
            res = dict(rule)
            res["found"] = True
            res["global_caps"] = policy.get("global_caps", {})
            return res

    return {"found": False, "issue_type": key}


@tool
def get_complaint_history(user_id: str) -> dict:
    """Tên: get_complaint_history — Tra cứu số lần khiếu nại trong tháng của khách hàng từ data/complaint_history.json.
    Input: user_id (str, mã người dùng lấy từ đơn hàng).
    Output: dict {'user_id': str, 'so_lan_thang_nay': int}.
    Tác động ra ngoài: Không (chỉ đọc)."""
    uid = str(user_id or "").strip()
    history = _read_data("complaint_history.json")
    return {
        "user_id": uid,
        "so_lan_thang_nay": int(history.get(uid, 0)) if uid else 0,
    }


@tool
def check_limit(
    issue_type: str,
    amount: int,
    order: dict,
    complaints_in_month: Optional[int] = None,
    request_type: str = "",
    session_id: Optional[str] = None,
) -> dict:
    """Tên: check_limit — Cổng kiểm soát chính sách và hạn mức bồi thường tất định bằng code Python (không gọi AI).
    Input: issue_type (str), amount (int), order (dict từ get_order), complaints_in_month (int|None), request_type ('HUY_DON'|'KHIEU_NAI_TRE'), session_id (str|None, tùy chọn kiểm bồi thường trùng trong phiên).
    Output: dict {'ok': bool, 'expected_decision': str, 'max': int, 'rule_id': str, 'ly_do': str}.
    Tác động ra ngoài: Không (tính toán thuần túy)."""
    policy = _read_data("policy.json")
    caps = policy.get("global_caps", {})
    valid_combos = policy.get("valid_status_combos", {})

    max_auto_refund = int(caps.get("max_auto_refund_vnd", 300000))
    max_auto_voucher = int(caps.get("max_auto_voucher_vnd", 30000))
    unassigned_cancel_min = int(caps.get("unassigned_cancel_threshold_min", 20))
    late_min = int(caps.get("late_voucher_min_delay_min", 30))
    heavy_delay_min = int(caps.get("heavy_delay_escalate_min", 60))
    complaints_threshold = int(caps.get("monthly_complaints_escalate_threshold", 3))

    try:
        amt = int(amount) if amount is not None and not isinstance(amount, bool) else -1
    except (TypeError, ValueError):
        amt = -1

    if complaints_in_month is None:
        uid = str(order.get("user_id") or "").strip() if isinstance(order, dict) else ""
        history = _read_data("complaint_history.json")
        complaints = int(history.get(uid, 0)) if uid else 0
    else:
        try:
            complaints = int(complaints_in_month)
        except (TypeError, ValueError):
            complaints = 0

    def _finish(expected_decision: str, max_amt: int, rule_id: str, ly_do: str) -> dict:
        if expected_decision in ("HUY_HOAN", "VOUCHER"):
            ok = 0 < amt <= max_amt
        else:
            ok = amt == 0
        return {
            "ok": ok,
            "expected_decision": expected_decision,
            "max": max_amt,
            "rule_id": rule_id,
            "ly_do": ly_do,
        }

    # 1. Thiếu / không tìm thấy đơn hàng
    if not order or not order.get("found"):
        return _finish(
            "HOI_LAI",
            0,
            "missing_order_id",
            "Không tìm thấy đơn hàng hợp lệ trong hệ thống, cần hỏi lại mã đơn.",
        )

    oid = str(order.get("order_id") or "")
    status = order.get("status", "")
    driver_status = order.get("driver_status", "")

    # 2. Mâu thuẫn cặp (status, driver_status)
    if driver_status not in valid_combos.get(status, []):
        return _finish(
            "CHUYEN_NV",
            0,
            "inconsistent_order_state",
            f"Trạng thái đơn mâu thuẫn (status={status}, driver_status={driver_status}), cần nhân viên kiểm tra.",
        )

    # 3. Đơn đã hủy (tránh bồi thường trùng)
    if status == "cancelled":
        return _finish(
            "TU_CHOI",
            0,
            "duplicate_compensation",
            "Đơn hàng đã ở trạng thái đã hủy trước đó, không áp dụng hoàn tiền hoặc voucher bổ sung.",
        )

    # 4. Xác định nhánh yêu cầu
    req = (request_type or "").strip().upper()
    if req not in ("HUY_DON", "KHIEU_NAI_TRE"):
        it_lower = (issue_type or "").strip().lower()
        if any(kw in it_lower for kw in ("cancel", "unassigned", "huy", "tai_xe", "chua_co")):
            req = "HUY_DON"
        else:
            req = "KHIEU_NAI_TRE"

    if "phut_tu_luc_dat" in order and "phut_tre_so_voi_eta" in order:
        phut_tu_luc_dat = int(order["phut_tu_luc_dat"])
        phut_tre_so_voi_eta = int(order["phut_tre_so_voi_eta"])
    else:
        phut_tu_luc_dat, phut_tre_so_voi_eta = _compute_minutes(order)

    total = int(order.get("total", 0))
    restaurant_prepared = bool(order.get("restaurant_prepared", False))

    # 5. Nhánh HUY_DON (policy.json: restaurant_prepared / driver_status != 'none' -> CHUYEN_NV)
    if req == "HUY_DON":
        if has_session_compensation(session_id, oid, "HUY_HOAN"):
            return _finish(
                "TU_CHOI",
                0,
                "duplicate_compensation",
                f"Đơn {oid} đã có phiếu đề xuất hủy hoàn trong phiên này, không áp dụng bồi thường trùng.",
            )
        if restaurant_prepared or driver_status != "none":
            return _finish(
                "CHUYEN_NV",
                0,
                "cancel_restaurant_prepared_or_picked_up",
                "Quán đã chuẩn bị món hoặc đơn đã có tài xế nhận, không thể tự động hủy đơn.",
            )
        if phut_tu_luc_dat <= unassigned_cancel_min:
            return _finish(
                "TU_CHOI",
                0,
                "unassigned_too_early",
                f"Đơn mới chờ {phut_tu_luc_dat} phút, chưa vượt ngưỡng {unassigned_cancel_min} phút để tự động hủy hoàn.",
            )
        if total > max_auto_refund:
            return _finish(
                "CHUYEN_NV",
                0,
                "cancel_high_value_cap_exceeded",
                f"Giá trị đơn {total}đ vượt trần tự động hoàn {max_auto_refund}đ, cần nhân viên duyệt.",
            )
        if complaints >= complaints_threshold:
            return _finish(
                "CHUYEN_NV",
                0,
                "repeat_complainer_limit",
                f"Tài khoản đã khiếu nại {complaints} lần trong tháng (≥ ngưỡng {complaints_threshold}), cần nhân viên xét duyệt.",
            )
        return _finish(
            "HUY_HOAN",
            total,
            "unassigned_cancel_refund",
            f"Đơn chưa có tài xế, quán chưa làm món, đã chờ {phut_tu_luc_dat} phút (> {unassigned_cancel_min} phút) và giá trị {total}đ ≤ {max_auto_refund}đ.",
        )

    # 6. Nhánh KHIEU_NAI_TRE
    if has_session_compensation(session_id, oid, "VOUCHER"):
        return _finish(
            "TU_CHOI",
            0,
            "duplicate_compensation",
            f"Đơn {oid} đã có phiếu đề xuất voucher giao trễ trong phiên này, không áp dụng bồi thường trùng.",
        )
    if phut_tre_so_voi_eta <= 0:
        detail = (
            f"còn/sớm hơn {abs(phut_tre_so_voi_eta)} phút"
            if phut_tre_so_voi_eta < 0
            else "đúng giờ dự kiến"
        )
        return _finish(
            "TU_CHOI",
            0,
            "late_delivery_under_threshold",
            f"Đơn hàng hiện chưa quá giờ dự kiến ({detail}), chưa áp dụng voucher giao trễ.",
        )
    if phut_tre_so_voi_eta <= late_min:
        return _finish(
            "TU_CHOI",
            0,
            "late_delivery_under_threshold",
            f"Đơn chỉ trễ {phut_tre_so_voi_eta} phút so với giờ dự kiến, chưa vượt ngưỡng {late_min} phút để cấp voucher.",
        )
    if phut_tre_so_voi_eta > heavy_delay_min:
        return _finish(
            "CHUYEN_NV",
            0,
            "heavy_delay_escalate",
            f"Đơn trễ {phut_tre_so_voi_eta} phút (> {heavy_delay_min} phút — trễ nặng), cần nhân viên xử lý trực tiếp.",
        )
    if complaints >= complaints_threshold:
        return _finish(
            "CHUYEN_NV",
            0,
            "repeat_complainer_limit",
            f"Tài khoản đã khiếu nại {complaints} lần trong tháng (≥ ngưỡng {complaints_threshold}), cần nhân viên xét duyệt.",
        )
    voucher_cap = min(max_auto_voucher, total)
    return _finish(
        "VOUCHER",
        voucher_cap,
        "late_delivery_voucher",
        f"Đơn giao trễ {phut_tre_so_voi_eta} phút (trong khoảng {late_min}–{heavy_delay_min} phút), đủ điều kiện voucher tối đa {voucher_cap}đ.",
    )


# Hàng chờ bản nháp chuyển nhân viên (chỉ trong bộ nhớ của tiến trình; mỗi bản nháp cũng nằm trong trace)
DRAFT_CASES: list = []


@tool
def escalate_to_human(case_id: str, reason: str) -> dict:
    """Tên: escalate_to_human — Tạo bản nháp ca chuyển nhân viên CSKH xử lý, mã ca duy nhất CS-<tham chiếu>-<số thứ tự>.
    Input: case_id (str, mã đơn hoặc nhãn tình huống), reason (str, lý do chuyển).
    Output: dict {'ma_ca': str, 'tham_chieu': str, 'trang_thai': 'ban_nhap_cho_duyet', 'ly_do': str}.
    Tác động ra ngoài: Không gửi đi đâu — chỉ thêm bản nháp vào hàng chờ DRAFT_CASES (bộ nhớ) chờ nhân viên duyệt."""
    raw = str(case_id or "").strip()
    m = re.search(r"(?:DH|ĐH)[\s\-]?(\d{1,4})(?!\d)", raw, re.IGNORECASE)
    if m:
        ref = "DH" + m.group(1).zfill(3)
    else:
        ref = re.sub(r"[^A-Za-z0-9]+", "", raw.replace("đ", "D").replace("Đ", "D")).upper()[:12] or "KHAC"
    draft = {
        "ma_ca": f"CS-{ref}-{len(DRAFT_CASES) + 1:03d}",
        "tham_chieu": ref,
        "trang_thai": "ban_nhap_cho_duyet",
        "ly_do": str(reason or "").strip(),
    }
    DRAFT_CASES.append(draft)
    return dict(draft)