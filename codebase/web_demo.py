"""Web Demo Server (100% Python stdlib) cho FoodResolve AI — không đụng vào run.py / tracing.py.

Chạy từ thư mục gốc repo:
    python codebase/web_demo.py
Mở trình duyệt tại:
    http://127.0.0.1:8000

Lưu ý giới hạn bản demo: trạng thái của phiên hiện tại (bồi thường trùng & bản nháp CS-... tạo trong phiên)
lưu in-memory trong tiến trình và tự xóa khi bấm "Làm mới phiên" hoặc khởi động lại server.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
import sys
import time
import urllib.parse

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
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        qs = urllib.parse.parse_qs(parsed_url.query)

        if path in ("/", "/demo.html"):
            self._send_html(os.path.join(BASE_DIR, "demo.html"))
            return
        if path == "/api/status":
            self._send_json(
                200,
                {
                    "model_provider": ai.MODEL_PROVIDER,
                    "model_name": ai.MODEL_NAME or "fake",
                    "draft_cases_count": len(tools.DRAFT_CASES),
                    "active_sessions_count": len(tools.SESSION_COMPENSATIONS),
                    "state_persistence": "in_memory_only",
                },
            )
            return
        if path == "/api/orders":
            try:
                self._send_json(200, {"orders": _load_orders_catalog()})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return
        if path == "/api/drafts":
            sid = (qs.get("session_id") or [""])[0].strip() or None
            drafts = tools.list_draft_cases(session_id=sid)
            self._send_json(
                200,
                {
                    "session_id": sid,
                    "drafts": drafts,
                    "count": len(drafts),
                    "total_draft_cases_count": len(tools.DRAFT_CASES),
                },
            )
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

            session_id = str(data.get("session_id") or "").strip() or None
            pending_context = str(data.get("pending_context") or "").strip()
            effective_text = f"{pending_context} {text}".strip() if pending_context else text

            t0 = time.perf_counter()
            tracing.begin("web_demo")
            try:
                res = agent.answer(effective_text, session_id=session_id)
                summary, events = tracing.end()
            except Exception as e:
                tracing.end()
                self._send_json(500, {"error": f"{type(e).__name__}: {e}"})
                return
            latency_ms = int((time.perf_counter() - t0) * 1000)

            raw_output = res.get("output", "") if isinstance(res, dict) else str(res)
            parsed = _parse_agent_output(raw_output)

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
                    "effective_input": agent._mask_pii(effective_text),
                    "session_id": session_id,
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
                    "session_drafts_count": len(tools.list_draft_cases(session_id)) if session_id else len(tools.DRAFT_CASES),
                },
            )
            return

        if self.path == "/api/reset-session":
            session_id = str(data.get("session_id") or "").strip() or None
            if session_id:
                tools.reset_session_compensations(session_id)
                cleared_drafts = tools.reset_draft_cases(session_id)
            else:
                cleared_drafts = 0
            self._send_json(
                200,
                {
                    "ok": True,
                    "cleared_session_id": session_id,
                    "cleared_drafts_count": cleared_drafts,
                    "draft_cases_count": len(tools.DRAFT_CASES),
                    "active_sessions_count": len(tools.SESSION_COMPENSATIONS),
                },
            )
            return

        if self.path == "/api/escalate":
            order_id = str(data.get("order_id") or "KHIEU_NAI").strip()
            reason = str(data.get("reason") or "Khách hàng yêu cầu nhân viên CSKH xem xét lại").strip()
            session_id = str(data.get("session_id") or "").strip() or None
            safe_reason = agent._mask_pii(reason)
            draft = tools.escalate_to_human(order_id, safe_reason, session_id=session_id)
            self._send_json(
                200,
                {
                    "draft": draft,
                    "draft_cases_count": len(tools.DRAFT_CASES),
                    "session_drafts_count": len(tools.list_draft_cases(session_id)) if session_id else len(tools.DRAFT_CASES),
                },
            )
            return

        self._send_json(404, {"error": "Endpoint không tồn tại"})

    def log_message(self, fmt, *args):
        print(f"[web_demo] {self.address_string()} - {fmt % args}")


def main():
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), DemoHandler)
    print(f"FoodResolve Demo đang chạy tại: http://127.0.0.1:{port}")
    print(f"Model hiện tại: MODEL_PROVIDER={ai.MODEL_PROVIDER} | MODEL_NAME={ai.MODEL_NAME or 'fake'}")
    print("Lưu ý: trạng thái phiên (bồi thường trùng & nháp ca CS-...) lưu in-memory, tự xóa khi làm mới phiên hoặc dừng server.")
    print("Nhấn Ctrl+C để dừng.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng server.")
        server.server_close()


if __name__ == "__main__":
    main()