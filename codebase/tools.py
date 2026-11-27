"""Công cụ của bài toán — FoodResolve AI (Track D1 · Team RUA).

Gồm đúng 5 công cụ gắn @tool:
  1. get_order(order_id) — tra cứu đơn hàng + tính thời gian/hợp lệ trạng thái bằng code
  2. get_policy(issue_type) — đọc chính sách & ngưỡng bồi thường từ data/policy.json
  3. get_complaint_history(user_id) — tra cứu số lần khiếu nại trong tháng của user
  4. check_limit(issue_type, amount, order, complaints_in_month, request_type) — cổng kiểm soát hạn mức tất định
  5. escalate_to_human(case_id, reason) — tạo bản nháp mã ca CS-xxx chờ nhân viên duyệt
"""
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

_FALLBACK_POLICY = {
    "schema_version": "1.1-cp2-fallback",
    "global_caps": {
        "max_auto_refund_vnd": 300000,
        "max_auto_voucher_vnd": 30000,
        "unassigned_cancel_threshold_min": 20,
        "late_voucher_min_delay_min": 30,
        "late_voucher_max_delay_min": 60,
        "heavy_delay_escalate_min": 60,
        "monthly_complaints_escalate_threshold": 3,
    },
    "valid_status_combos": {
        "waiting_driver": ["none"],
        "delivering": ["assigned", "picked_up"],
        "delivered": ["picked_up"],
        "cancelled": ["none"],
    },
    "rules": [
        {
            "issue_type": "unassigned_cancel_refund",
            "condition": "HUY_DON khi driver_status == 'none' AND restaurant_prepared == false AND phut_tu_luc_dat > 20 AND total <= 300000 AND complaints_in_month < 3",
            "max_action": "HUY_HOAN",
            "max_amount": 300000,
        },
        {
            "issue_type": "late_delivery_voucher",
            "condition": "KHIEU_NAI_TRE khi 30 < phut_tre_so_voi_eta <= 60 AND complaints_in_month < 3",
            "max_action": "VOUCHER",
            "max_amount": 30000,
        },
    ],
}

_FALLBACK_ORDERS = [
    {
        "order_id": "DH001",
        "user_id": "U01",
        "restaurant": "Quán Mẫu 2",
        "items": [{"name": "Cơm gà xối mỡ", "qty": 1, "price": 50000}],
        "ship_fee": 15000,
        "total": 65000,
        "placed_at": "2026-11-27T11:00",
        "eta": "2026-11-27T11:30",
        "now": "2026-11-27T11:15",
        "status": "waiting_driver",
        "driver_status": "none",
        "is_batched": False,
        "restaurant_prepared": False,
    },
    {
        "order_id": "DH004",
        "user_id": "U04",
        "restaurant": "Quán Mẫu 5",
        "items": [
            {"name": "Phở bò tái chín", "qty": 1, "price": 55000},
            {"name": "Trà đào cam sả", "qty": 1, "price": 25000},
        ],
        "ship_fee": 15000,
        "total": 95000,
        "placed_at": "2026-11-27T11:50",
        "eta": "2026-11-27T12:20",
        "now": "2026-11-27T12:15",
        "status": "waiting_driver",
        "driver_status": "none",
        "is_batched": False,
        "restaurant_prepared": False,
    },
]

_FALLBACK_HISTORY = {"U01": 0, "U04": 1}


def _read_json_or_fallback(filename: str, fallback):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return fallback


def _normalize_order_id(order_id: str) -> str:
    raw = str(order_id or "").strip().replace("đ", "D").replace("Đ", "D").upper()
    return re.sub(r"[#\s\-]+", "", raw)


def _compute_minutes(order: dict) -> tuple:
    placed_dt = datetime.fromisoformat(order["placed_at"])
    eta_dt = datetime.fromisoformat(order["eta"])
    now_dt = datetime.fromisoformat(order["now"])
    phut_tu_luc_dat = int((now_dt - placed_dt).total_seconds() // 60)
    phut_tre_so_voi_eta = int((now_dt - eta_dt).total_seconds() // 60)
    return phut_tu_luc_dat, phut_tre_so_voi_eta


@tool
def get_order(order_id: str) -> dict:
    """Tên: get_order — Tra cứu đơn hàng từ data/orders.json và tính số phút/hợp lệ trạng thái bằng code.
    Input: order_id (str, hỗ trợ dạng '#dh-004', 'DH004', 'ĐH004').
    Output: dict thông tin đơn (đã bỏ trường PII) kèm 'found', 'phut_tu_luc_dat', 'phut_tre_so_voi_eta', 'trang_thai_hop_le'; hoặc {'found': False, 'order_id': ...}.
    Tác động ra ngoài: Không (chỉ đọc)."""
    normalized_id = _normalize_order_id(order_id)
    if not normalized_id:
        return {"found": False, "order_id": ""}

    orders = _read_json_or_fallback("orders.json", _FALLBACK_ORDERS)
    policy = _read_json_or_fallback("policy.json", _FALLBACK_POLICY)
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
    policy = _read_json_or_fallback("policy.json", _FALLBACK_POLICY)
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
    Input: user_id (str, ví dụ 'U07').
    Output: dict {'user_id': str, 'so_lan_thang_nay': int}.
    Tác động ra ngoài: Không (chỉ đọc)."""
    uid = str(user_id or "").strip()
    history = _read_json_or_fallback("complaint_history.json", _FALLBACK_HISTORY)
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
) -> dict:
    """Tên: check_limit — Cổng kiểm soát chính sách và hạn mức bồi thường tất định bằng code Python (không gọi AI).
    Input: issue_type (str), amount (int), order (dict từ get_order), complaints_in_month (int|None, None sẽ tự đọc complaint_history.json theo order['user_id']), request_type ('HUY_DON'|'KHIEU_NAI_TRE', mặc định '').
    Output: dict {'ok': bool, 'expected_decision': str, 'max': int, 'rule_id': str, 'ly_do': str}.
    Tác động ra ngoài: Không (tính toán thuần túy)."""
    policy = _read_json_or_fallback("policy.json", _FALLBACK_POLICY)
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
        history = _read_json_or_fallback("complaint_history.json", _FALLBACK_HISTORY)
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

    # 5. Nhánh HUY_DON
    if req == "HUY_DON":
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


@tool
def escalate_to_human(case_id: str, reason: str) -> dict:
    """Tên: escalate_to_human — Tạo bản nháp mã ca chuyển nhân viên CSKH xử lý.
    Input: case_id (str, mã đơn hoặc mã tình huống), reason (str, lý do chuyển).
    Output: dict {'ma_ca': str, 'trang_thai': 'ban_nhap_cho_duyet', 'ly_do': str}.
    Tác động ra ngoài: Có (đảo được — chỉ tạo bản nháp chờ người duyệt, không gửi tin hay ghi DB thật)."""
    raw = str(case_id or "").strip()
    m = re.search(r"(?:#)?\b(?:DH|ĐH)[\s\-]?(\d{1,4})\b", raw, re.IGNORECASE)
    if m:
        ma_ca = "CS-DH" + m.group(1)
    else:
        clean = re.sub(r"[^A-Za-z0-9]+", "", raw.replace("đ", "D").replace("Đ", "D")).upper()
        ma_ca = f"CS-{clean[:12]}" if clean else "CS-001"
    return {
        "ma_ca": ma_ca,
        "trang_thai": "ban_nhap_cho_duyet",
        "ly_do": str(reason or "").strip(),
    }
