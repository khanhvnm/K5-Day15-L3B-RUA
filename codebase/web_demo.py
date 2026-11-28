"""Web Demo Server (100% Python stdlib) cho FoodResolve AI — không đụng vào run.py / tracing.py.

Chạy từ thư mục gốc repo:
    python codebase/web_demo.py
Mở trình duyệt tại:
    http://127.0.0.1:8000
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, BASE_DIR)

import ai  # noqa: E402
import agent  # noqa: E402
import tools  # noqa: E402
import tracing  # noqa: E402

HEADER_RE = re.compile(
    r"^\[QUYET_DINH=(?P<decision>[A-Z_]+)\s*\|\s*SO_TIEN=(?P<amount>-?\d+)\s*\|\s*MA_CA=(?P<case_id>[^\]]+)\]\s*(?P<reply>.*)$",
    re.DOTALL,
)

# Giá tham khảo gpt-4o-mini (USD / 1M tokens) để hiện ước tính ngay trên Inspector
PRICE_IN_PER_1M = 0.15
PRICE_OUT_PER_1M = 0.60


def _parse_agent_output(raw_output: str) -> dict:
    m = HEADER_RE.match((raw_output or "").strip())
    if not m:
        return {
            "decision": "CHUYEN_NV",
            "amount": 0,
            "ma_ca": "-",
            "reply": raw_output or "",
        }
    return {
        "decision": m.group("decision"),
        "amount": int(m.group("amount")),
        "ma_ca": m.group("case_id").strip(),
        "reply": m.group("reply").strip(),
    }


def _load_orders_catalog() -> list:
    orders = tools._read_data("orders.json")
    history = tools._read_data("complaint_history.json")
    policy = tools._read_data("policy.json")
    valid_combos = policy.get("valid_status_combos", {})
    catalog = []
    for item in orders:
        p_dat, p_tre = tools._compute_minutes(item)
        status = item.get("status", "")
        drv = item.get("driver_status", "")
        catalog.append(
            {
                "order_id": item["order_id"],
                "user_id": item["user_id"],
                "total": item["total"],
                "status": status,
                "driver_status": drv,
                "restaurant_prepared": item["restaurant_prepared"],
                "is_batched": item["is_batched"],
                "phut_tu_luc_dat": p_dat,
                "phut_tre_so_voi_eta": p_tre,
                "trang_thai_hop_le": drv in valid_combos.get(status, []),
                "complaints_in_month": int(history.get(item["user_id"], 0)),
            }
        )
    return catalog


class DemoHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, path: str):
        if not os.path.exists(path):
            self._send_json(404, {"error": f"Không tìm thấy {path}"})
            return
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/demo.html"):
            self._send_html(os.path.join(BASE_DIR, "demo.html"))
            return
        if self.path == "/api/status":
            self._send_json(
                200,
                {
                    "model_provider": ai.MODEL_PROVIDER,
                    "model_name": ai.MODEL_NAME or "fake",
                    "draft_cases_count": len(tools.DRAFT_CASES),
                },
            )
            return
        if self.path == "/api/orders":
            try:
                self._send_json(200, {"orders": _load_orders_catalog()})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return
        if self.path == "/api/drafts":
            self._send_json(200, {"drafts": list(tools.DRAFT_CASES)})
            return
        self._send_json(404, {"error": "Endpoint không tồn tại"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw_body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "JSON đầu vào không hợp lệ"})
            return

        if self.path == "/api/chat":
            text = str(data.get("message") or "").strip()
            if not text:
                self._send_json(400, {"error": "Thiếu nội dung tin nhắn"})
                return

            # Hỗ trợ Mid-Flow Correction ở tầng demo: ghép ngữ cảnh cũ nếu lượt trước bị HOI_LAI
            pending_context = str(data.get("pending_context") or "").strip()
            effective_text = f"{pending_context} {text}".strip() if pending_context else text

            t0 = time.perf_counter()
            tracing.begin("web_demo")
            try:
                res = agent.answer(effective_text)
                summary, events = tracing.end()
            except Exception as e:
                tracing.end()
                self._send_json(500, {"error": f"{type(e).__name__}: {e}"})
                return
            latency_ms = int((time.perf_counter() - t0) * 1000)

            raw_output = res.get("output", "") if isinstance(res, dict) else str(res)
            parsed = _parse_agent_output(raw_output)

            # Lấy ảnh chụp đơn hàng phục vụ panel Inspector (không tính thêm vào trace)
            extracted_id = agent._extract_order_id(effective_text)
            order_snapshot = None
            if extracted_id:
                for row in _load_orders_catalog():
                    if row["order_id"] == extracted_id:
                        order_snapshot = row
                        break

            tokens_in = int(summary.get("tokens_in", 0))
            tokens_out = int(summary.get("tokens_out", 0))
            est_cost_usd = (
                tokens_in * PRICE_IN_PER_1M + tokens_out * PRICE_OUT_PER_1M
            ) / 1_000_000

            self._send_json(
                200,
                {
                    "effective_input": effective_text,
                    "raw_output": raw_output,
                    "parsed": parsed,
                    "order_snapshot": order_snapshot,
                    "extracted_order_id": extracted_id,
                    "trace_summary": summary,
                    "trace_events": events if isinstance(events, list) else [],
                    "latency_ms": latency_ms,
                    "est_cost_usd": round(est_cost_usd, 6),
                    "model_provider": ai.MODEL_PROVIDER,
                    "draft_cases_count": len(tools.DRAFT_CASES),
                },
            )
            return

        if self.path == "/api/escalate":
            order_id = str(data.get("order_id") or "KHIEU_NAI").strip()
            reason = str(data.get("reason") or "Khách hàng yêu cầu nhân viên CSKH xem xét lại").strip()
            draft = tools.escalate_to_human(order_id, reason)
            self._send_json(200, {"draft": draft, "draft_cases_count": len(tools.DRAFT_CASES)})
            return

        self._send_json(404, {"error": "Endpoint không tồn tại"})

    def log_message(self, fmt, *args):
        print(f"[web_demo] {self.address_string()} - {fmt % args}")


def main():
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), DemoHandler)
    print(f"FoodResolve Demo đang chạy tại: http://127.0.0.1:{port}")
    print(f"Model hiện tại: MODEL_PROVIDER={ai.MODEL_PROVIDER} | MODEL_NAME={ai.MODEL_NAME or 'fake'}")
    print("Nhấn Ctrl+C để dừng.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng server.")
        server.server_close()


if __name__ == "__main__":
    main()