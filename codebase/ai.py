"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
"""
import json
import os
import time
from typing import Optional
import urllib.error
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOW_RAW = False
URL_OPENAI = "https://api.openai.com/v1/chat/completions"
_RETRYABLE_HTTP_CODES = {408, 429, 500, 502, 503, 504}


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()


def post_json(
    url: str,
    headers: dict,
    body: dict,
    timeout: int = 60,
    max_retries: int = 2,
) -> dict:
    """Gửi HTTP POST JSON bằng urllib kèm retry/backoff cho lỗi tạm thời (429/5xx/mạng)."""
    payload = json.dumps(body).encode("utf-8")
    req_headers = dict({"Content-Type": "application/json"}, **headers)
    last_err = None

    for attempt in range(max_retries + 1):
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers=req_headers,
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8"))
            if SHOW_RAW:
                print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
            return data
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last_err = RuntimeError("HTTP %d: %s" % (e.code, detail))
            if e.code in _RETRYABLE_HTTP_CODES and attempt < max_retries:
                time.sleep(0.8 * (2 ** attempt))
                continue
            raise last_err
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = RuntimeError("Network error: %s" % e)
            if attempt < max_retries:
                time.sleep(0.8 * (2 ** attempt))
                continue
            raise last_err

    raise last_err or RuntimeError("Không gọi được API model")


def call_openai(
    system: str,
    user: str,
    response_schema: Optional[dict] = None,
    max_tokens: int = 512,
) -> dict:
    """Gọi OpenAI Chat Completions API (hỗ trợ Structured Outputs strict) và đọc token từ usage."""
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": user}
    ]
    if response_schema:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "food_resolve_decision",
                "strict": True,
                "schema": response_schema,
            },
        }
    else:
        response_format = {"type": "json_object"}

    body = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": response_format,
    }
    data = post_json(URL_OPENAI, {"Authorization": "Bearer " + API_KEY}, body)
    u = data["usage"]
    msg = data["choices"][0]["message"]
    content = msg.get("content")
    refusal = msg.get("refusal")
    text = content if content is not None else (f"[refusal] {refusal}" if refusal else "")
    return {
        "text": text,
        "tokens_in": int(u["prompt_tokens"]),
        "tokens_out": int(u["completion_tokens"]),
    }


@model_call
def call_model(
    system: str,
    user: str,
    response_schema: Optional[dict] = None,
    max_tokens: int = 512,
) -> dict:
    """Gọi model AI theo MODEL_PROVIDER. Giữ tương thích 2 tham số call_model(system, user)."""
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {
            "text": "[câu trả lời giả — chưa nối model] " + last[:60],
            "model": "fake",
            "tokens_in": 0,
            "tokens_out": 0,
        }

    if MODEL_PROVIDER == "openai":
        r = call_openai(system, user, response_schema=response_schema, max_tokens=max_tokens)
        return {
            "text": r["text"],
            "model": MODEL_NAME,
            "tokens_in": int(r["tokens_in"]),
            "tokens_out": int(r["tokens_out"]),
        }

    raise NotImplementedError(
        "chưa viết phần gọi model thật cho MODEL_PROVIDER=%s trong codebase/ai.py — xem docs/connect-model.md"
        % MODEL_PROVIDER
    )