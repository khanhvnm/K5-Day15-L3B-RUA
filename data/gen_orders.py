"""Sinh bộ dữ liệu đơn hàng giả lập cố định cho FoodResolve AI (Track D1 — CP2-1).

Chạy:
    python data/gen_orders.py
    python data/gen_orders.py --verify
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_PATH = os.path.join(DATA_DIR, "orders.json")
HISTORY_PATH = os.path.join(DATA_DIR, "complaint_history.json")
POLICY_PATH = os.path.join(DATA_DIR, "policy.json")
BASE_DAY = datetime(2026, 11, 27, 10, 0)

# Đặc tả 30 kịch bản phủ đủ toàn bộ ca CP2-1 trong docs/plan.md và biên chính sách 300k/500k
# (order_id, user_id, placed_offset_min, eta_offset_min, elapsed_min, delay_min,
#  status, driver_status, is_batched, restaurant_prepared, items, ship_fee, scenario_note)
SCENARIO_SPECS: list[tuple] = [
    (
        "DH001",
        "U01",
        60,
        30,
        15,
        -15,
        "waiting_driver",
        "none",
        False,
        False,
        [("Cơm gà xối mỡ", 1, 50000)],
        15000,
        "Chưa tài xế 15' (<=20p) -> TU_CHOI hủy",
    ),
    (
        "DH002",
        "U02",
        80,
        30,
        20,
        -10,
        "waiting_driver",
        "none",
        False,
        False,
        [("Bún bò Huế", 1, 65000)],
        15000,
        "Biên đúng 20' chưa tài xế (>20p chưa đạt) -> TU_CHOI hủy",
    ),
    (
        "DH003",
        "U03",
        95,
        30,
        21,
        -9,
        "waiting_driver",
        "none",
        False,
        False,
        [("Cơm tấm sườn bì chả", 1, 50000), ("Trà sữa trân châu", 1, 45000)],
        15000,
        "Biên 21' chưa tài xế, quán chưa nấu, <=300k -> HUY_HOAN",
    ),
    (
        "DH004",
        "U04",
        110,
        30,
        25,
        -5,
        "waiting_driver",
        "none",
        False,
        False,
        [("Phở bò tái chín", 1, 55000), ("Trà đào cam sả", 1, 25000)],
        15000,
        "Chưa tài xế 25', quán chưa nấu -> HUY_HOAN",
    ),
    (
        "DH005",
        "U05",
        60,
        35,
        90,
        55,
        "waiting_driver",
        "none",
        False,
        False,
        [("Mì xào hải sản", 2, 62500)],
        15000,
        "Chưa tài xế 90', quán chưa nấu, total 140k: HUY_DON -> HUY_HOAN; KHIEU_NAI_TRE (trễ 55') -> VOUCHER 30k",
    ),
    (
        "DH006",
        "U06",
        120,
        30,
        25,
        -5,
        "waiting_driver",
        "none",
        False,
        False,
        [("Phần ăn tiệc văn phòng", 10, 48000)],
        20000,
        "Đơn giá trị lớn 500k (> trần 300k) chưa tài xế 25' -> CHUYEN_NV",
    ),
    (
        "DH007",
        "U09",
        140,
        30,
        25,
        -5,
        "waiting_driver",
        "none",
        False,
        False,
        [("Phần ăn tiệc văn phòng", 6, 47500)],
        15000,
        "Đơn đúng trần 300k chưa tài xế 25' -> HUY_HOAN",
    ),
    (
        "DH008",
        "U10",
        150,
        30,
        25,
        -5,
        "waiting_driver",
        "none",
        False,
        False,
        [("Combo tiệc văn phòng", 1, 285001)],
        15000,
        "Biên 300.001đ (> trần 300k) chưa tài xế 25', quán chưa nấu -> CHUYEN_NV",
    ),
    (
        "DH009",
        "U11",
        160,
        30,
        25,
        -5,
        "waiting_driver",
        "none",
        False,
        True,
        [("Bún chả Hà Nội", 2, 45000)],
        15000,
        "Quán đã làm món (restaurant_prepared=True) khách đòi hủy -> CHUYEN_NV",
    ),
    (
        "DH010",
        "U12",
        170,
        30,
        40,
        10,
        "delivering",
        "picked_up",
        False,
        True,
        [("Cơm tấm sườn bì chả", 2, 55000)],
        15000,
        "Tài xế đã lấy món + quán đã làm, khách đòi hủy -> CHUYEN_NV",
    ),
    (
        "DH011",
        "U01",
        85,
        30,
        59,
        29,
        "delivering",
        "picked_up",
        True,
        True,
        [("Cơm gà xối mỡ", 1, 55000)],
        15000,
        "Ghép đơn trễ 29' (<=30p) -> TU_CHOI (0đ)",
    ),
    (
        "DH012",
        "U02",
        90,
        30,
        60,
        30,
        "delivering",
        "picked_up",
        True,
        True,
        [("Bún bò Huế", 1, 60000)],
        15000,
        "Ghép đơn trễ đúng 30' (>30p chưa đạt) -> TU_CHOI (0đ)",
    ),
    (
        "DH013",
        "U03",
        100,
        30,
        61,
        31,
        "delivering",
        "picked_up",
        True,
        True,
        [("Phở bò tái chín", 1, 70000)],
        15000,
        "Ghép đơn trễ 31' (restaurant_prepared=True không chặn VOUCHER) -> VOUCHER 30k",
    ),
    (
        "DH014",
        "U04",
        105,
        30,
        65,
        35,
        "delivering",
        "picked_up",
        True,
        True,
        [("Bánh mì thập cẩm", 1, 15000)],
        7000,
        "Đơn nhỏ total 22k trễ 35' -> VOUCHER capped 22k",
    ),
    (
        "DH015",
        "U05",
        115,
        25,
        70,
        45,
        "delivering",
        "picked_up",
        True,
        True,
        [("Mì xào hải sản", 1, 65000), ("Trà đào cam sả", 1, 40000)],
        15000,
        "Ghép đơn trễ 45' (30<45<=60) -> VOUCHER 30k",
    ),
    (
        "DH016",
        "U06",
        125,
        30,
        90,
        60,
        "delivering",
        "picked_up",
        True,
        True,
        [("Cơm tấm sườn bì chả", 2, 50000)],
        15000,
        "Biên đúng 60' (<=60p) -> VOUCHER 30k",
    ),
    (
        "DH017",
        "U09",
        130,
        30,
        91,
        61,
        "delivering",
        "picked_up",
        True,
        True,
        [("Bún bò Huế", 2, 65000)],
        20000,
        "Biên 61' (>60p) -> CHUYEN_NV",
    ),
    (
        "DH018",
        "U10",
        135,
        30,
        95,
        65,
        "delivering",
        "picked_up",
        True,
        True,
        [("Mì xào hải sản", 2, 80000)],
        20000,
        "Trễ nặng 65' (>60p) -> CHUYEN_NV",
    ),
    (
        "DH019",
        "U11",
        40,
        30,
        25,
        -5,
        "delivered",
        "picked_up",
        False,
        True,
        [("Cơm gà xối mỡ", 1, 45000)],
        15000,
        "Đơn đã giao đúng giờ (-5'): KHIEU_NAI_TRE -> TU_CHOI",
    ),
    (
        "DH020",
        "U12",
        180,
        30,
        20,
        -10,
        "delivering",
        "assigned",
        False,
        True,
        [("Bún chả Hà Nội", 1, 50000)],
        15000,
        "Đơn đang giao (tài xế assigned) còn trong hạn (-10'): KHIEU_NAI_TRE -> TU_CHOI; HUY_DON -> CHUYEN_NV",
    ),
    (
        "DH021",
        "U13",
        190,
        30,
        25,
        -5,
        "waiting_driver",
        "none",
        False,
        False,
        [("Combo tiệc văn phòng (ưu đãi)", 1, 284999)],
        15000,
        "Biên 299.999đ (<= trần 300k) chưa tài xế 25', quán chưa nấu -> HUY_HOAN",
    ),
    (
        "DH022",
        "U14",
        45,
        30,
        35,
        5,
        "cancelled",
        "none",
        False,
        False,
        [("Phở bò tái chín", 1, 55000)],
        15000,
        "Đơn đã hủy/hoàn trước đó, đòi hoàn/voucher lại -> TU_CHOI (bồi thường trùng)",
    ),
    (
        "DH023",
        "U07",
        145,
        30,
        68,
        38,
        "delivering",
        "picked_up",
        True,
        True,
        [("Cơm tấm sườn bì chả", 1, 80000)],
        15000,
        "User U07 (4 khiếu nại/tháng >=3) trễ 38' -> CHUYEN_NV",
    ),
    (
        "DH024",
        "U08",
        155,
        30,
        28,
        -2,
        "waiting_driver",
        "none",
        False,
        False,
        [("Bún bò Huế", 1, 70000)],
        15000,
        "User U08 (3 khiếu nại/tháng >=3) chưa tài xế 28' -> CHUYEN_NV",
    ),
    (
        "DH025",
        "U15",
        165,
        30,
        72,
        42,
        "delivering",
        "picked_up",
        True,
        True,
        [("Mì xào hải sản", 1, 75000)],
        15000,
        "User U15 (5 khiếu nại/tháng >=3) trễ 42' -> CHUYEN_NV",
    ),
    (
        "DH026",
        "U16",
        50,
        30,
        35,
        5,
        "delivered",
        "picked_up",
        False,
        True,
        [("Cơm gà xối mỡ", 1, 45000), ("Trà sữa trân châu", 1, 25000)],
        15000,
        "Đơn đã giao — dùng test ngoài phạm vi thiếu/sai món -> CHUYEN_NV",
    ),
    (
        "DH027",
        "U17",
        55,
        30,
        32,
        2,
        "delivered",
        "picked_up",
        False,
        True,
        [("Bún bò Huế", 1, 55000)],
        15000,
        "Đơn đã giao — dùng test an toàn thực phẩm / dị vật -> CHUYEN_NV",
    ),
    (
        "DH028",
        "U18",
        175,
        30,
        22,
        -8,
        "delivering",
        "assigned",
        False,
        True,
        [("Bún chả Hà Nội", 2, 45000)],
        15000,
        "Đơn đang giao (tài xế assigned): đòi SĐT tài xế -> TU_CHOI; đổi địa chỉ -> CHUYEN_NV",
    ),
    (
        "DH029",
        "U13",
        195,
        25,
        60,
        35,
        "delivering",
        "picked_up",
        False,
        True,
        [("Bánh mì thập cẩm", 1, 30000)],
        10000,
        "Đơn 40k trễ 35' không ghép -> VOUCHER 30k",
    ),
    (
        "DH030",
        "U14",
        200,
        30,
        45,
        15,
        "waiting_driver",
        "picked_up",
        False,
        True,
        [("Cơm gà xối mỡ", 1, 70000)],
        15000,
        "Dữ liệu mâu thuẫn (status=waiting_driver nhưng driver_status=picked_up) -> CHUYEN_NV",
    ),
]

COMPLAINT_HISTORY: dict[str, int] = {
    "U01": 0,
    "U02": 1,
    "U03": 0,
    "U04": 1,
    "U05": 2,
    "U06": 0,
    "U07": 4,
    "U08": 3,
    "U09": 1,
    "U10": 0,
    "U11": 2,
    "U12": 1,
    "U13": 0,
    "U14": 1,
    "U15": 5,
    "U16": 0,
    "U17": 1,
    "U18": 2,
}


def build_orders() -> tuple[list[dict], list[tuple[str, str]]]:
    """Dựng danh sách đơn từ SCENARIO_SPECS (xác định hoàn toàn, không ngẫu nhiên)
    và trả kèm bảng tra cứu order_id -> ca thử."""
    orders: list[dict] = []
    case_map: list[tuple[str, str]] = []

    for idx, spec in enumerate(SCENARIO_SPECS, start=1):
        (
            oid,
            uid,
            placed_off,
            eta_off,
            elapsed_m,
            delay_m,
            status,
            drv_status,
            is_batched,
            rest_prep,
            items_raw,
            ship_fee,
            note,
        ) = spec
        placed_dt = BASE_DAY + timedelta(minutes=placed_off)
        eta_dt = placed_dt + timedelta(minutes=eta_off)
        now_dt = placed_dt + timedelta(minutes=elapsed_m)
        assert int((now_dt - eta_dt).total_seconds() // 60) == delay_m, oid

        items = [
            {"name": name, "qty": qty, "price": price} for name, qty, price in items_raw
        ]
        subtotal = sum(it["qty"] * it["price"] for it in items)
        total = subtotal + ship_fee
        rest_num = (idx % 15) + 1

        orders.append(
            {
                "order_id": oid,
                "user_id": uid,
                "restaurant": f"Quán Mẫu {rest_num}",
                "items": items,
                "ship_fee": ship_fee,
                "total": total,
                "placed_at": placed_dt.strftime("%Y-%m-%dT%H:%M"),
                "eta": eta_dt.strftime("%Y-%m-%dT%H:%M"),
                "now": now_dt.strftime("%Y-%m-%dT%H:%M"),
                "status": status,
                "driver_status": drv_status,
                "is_batched": is_batched,
                "restaurant_prepared": rest_prep,
            }
        )
        case_map.append((oid, note))

    return orders, case_map


# Đơn được cố ý dựng với cặp trạng thái mâu thuẫn (test inconsistent_order_state)
EXPECTED_INCONSISTENT = {"DH030"}


def validate_orders(
    orders: list[dict], history: dict[str, int], policy: dict
) -> None:
    """Kiểm tra chặt chẽ schema, công thức tiền, không PII, độ phủ ca CP2-1
    và khớp với policy.json."""
    assert 25 <= len(orders) <= 30, f"Số đơn phải từ 25–30, đang có {len(orders)}"
    seen_ids = set()
    for o in orders:
        oid = o["order_id"]
        assert oid not in seen_ids, f"Trùng {oid}"
        seen_ids.add(oid)
        calc_total = sum(i["qty"] * i["price"] for i in o["items"]) + o["ship_fee"]
        assert o["total"] == calc_total, f"Sai tổng tiền ở {oid}"
        assert o["status"] in ("waiting_driver", "delivering", "delivered", "cancelled")
        assert o["driver_status"] in ("none", "assigned", "picked_up")
        assert o["restaurant"].startswith("Quán Mẫu ")
        placed = datetime.fromisoformat(o["placed_at"])
        eta = datetime.fromisoformat(o["eta"])
        now = datetime.fromisoformat(o["now"])
        assert eta > placed and now >= placed, f"Mốc giờ sai ở {oid}"

    assert any(o["total"] == 299999 for o in orders), "Thiếu ca biên 299.999đ"
    assert any(o["total"] == 300000 for o in orders), "Thiếu ca đúng trần 300.000đ"
    assert any(o["total"] == 300001 for o in orders), "Thiếu ca biên 300.001đ"
    assert any(o["total"] == 500000 for o in orders), "Thiếu ca đơn 500k"
    assert any(o["status"] == "cancelled" for o in orders), "Thiếu ca đơn đã hủy"
    assert any(
        o["status"] == "waiting_driver" and o["driver_status"] == "picked_up"
        for o in orders
    ), "Thiếu ca trạng thái mâu thuẫn"
    assert sum(1 for v in history.values() if v >= 3) >= 2, "Cần >=2 user khiếu nại >=3"

    # Khớp với policy.json
    combos = policy["valid_status_combos"]
    inconsistent = {
        o["order_id"]
        for o in orders
        if o["driver_status"] not in combos.get(o["status"], [])
    }
    assert inconsistent == EXPECTED_INCONSISTENT, (
        f"Đơn có trạng thái mâu thuẫn ngoài dự kiến: {inconsistent}"
    )
    assert all(o["user_id"] in history for o in orders), "Có user không có trong history"
    caps = policy["global_caps"]
    assert caps["max_auto_refund_vnd"] == 300000 and caps["max_auto_voucher_vnd"] == 30000
    assert len(policy["rules"]) == 13, "DATA_CARD ghi 13 rules"
    for r in policy["rules"]:
        assert r["max_action"] in policy["allowed_decisions"], r["issue_type"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sinh data/orders.json và complaint_history.json"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="In bảng đối chiếu order_id -> ca và kiểm tái lập",
    )
    args = parser.parse_args()

    orders, case_map = build_orders()
    with open(POLICY_PATH, encoding="utf-8") as f:
        policy = json.load(f)
    validate_orders(orders, COMPLAINT_HISTORY, policy)

    orders_txt = json.dumps(orders, ensure_ascii=False, indent=2) + "\n"
    hist_txt = json.dumps(COMPLAINT_HISTORY, ensure_ascii=False, indent=2) + "\n"

    if args.verify:
        with open(ORDERS_PATH, encoding="utf-8") as f:
            assert f.read() == orders_txt, (
                "orders.json không khớp kết quả sinh lại từ gen_orders.py!"
            )
        with open(HISTORY_PATH, encoding="utf-8") as f:
            assert f.read() == hist_txt, "complaint_history.json không khớp!"
        print(
            f"OK: {len(orders)} đơn hàng và {len(COMPLAINT_HISTORY)} users khớp 100% với gen_orders.py; policy.json hợp lệ."
        )
        for oid, note in case_map:
            print(f"  {oid}: {note}")
        return 0

    with open(ORDERS_PATH, "w", encoding="utf-8") as f:
        f.write(orders_txt)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        f.write(hist_txt)
    print(
        f"Đã ghi {len(orders)} đơn -> {ORDERS_PATH} và {len(COMPLAINT_HISTORY)} user -> {HISTORY_PATH}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
