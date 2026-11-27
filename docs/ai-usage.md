# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Claude Code | Review `agent.py` / `tools.py` bằng bộ test giả lập model; sửa cổng `check_limit` (không chi tiền khi JSON hỏng, không tự hủy đơn), chặn NFC, mã ca duy nhất; viết `tests/test_cp2_agent.py` (16 test) | Khánh duyệt diff, chạy `python -m unittest discover -s tests` + `python run.py`; Vũ Thành tự khai phần code gốc: __ | Vũ Thành (chủ code) · Khánh (review) |
| Prompt / thiết kế lời gọi mô hình | Claude Code | Sửa quy tắc `request_type` trong `SYSTEM` (chỉ HUY_DON khi khách nói rõ muốn hủy); soạn prompt nháp cho bước chấm thử | Prompt gốc: Vũ Thành tự khai __; prompt nháp chấm thử chạy tay qua chatbot, output dán nguyên văn | Vũ Thành · Khánh |
| Đào data (viết script đếm, gợi ý nhãn) | Claude Code | Review `sample_reviews.py` (bỏ fallback `_local/`, chặn ghi đè nhãn, thêm `--verify`); đề xuất thứ tự ưu tiên nhãn + bảng ca mập mờ trong `data-mining.md` | Nhóm chốt luật nhãn trước khi gắn. **`part2–4` + 30 dòng chung do người gắn tay; `part1` (75 dòng) do Claude Code gợi ý nhãn, Khánh duyệt** — nên độ khớp 30 dòng chung là Duy Thành ↔ AI (ghi rõ ở `data-mining.md` mục 3). Claude Code còn: chèn lại 1 dòng `part4` bị mất (gắn `khac`), đảo nhãn chính 5 dòng `part2`/`part4` cho đúng luật ưu tiên — chủ file xác nhận. Kiểm tay __ dòng, khớp __ | Duy Thành |
| Rà câu hỏi phỏng vấn / khảo sát | Claude Code | Soạn `evidence/survey/questions.md` từ danh sách câu gợi ý trong `docs/plan.md` CP2-5 + cách đếm ghi trước | Khánh rà câu dẫn dắt trước khi gửi form. Sau khi có kết quả: Claude Code viết `evidence/scripts/anonymize_survey.py` (bỏ email / giờ gửi / cách liên hệ, bỏ lượt trùng email, gộp cách viết tay) và chép lại bộ câu đã gửi thật vào `questions.md`; Khánh kiểm `results.csv` không còn email / SĐT | Khánh |
| Viết câu thử (benchmark) | Claude Code | Viết B14–B20 (7 câu biên: an toàn thực phẩm, trần 300k, biên 30'/60', bồi thường trùng, dữ liệu mâu thuẫn); sửa B01, B02 | Việt Anh duyệt cả 7 câu; mỗi câu có `source` (B14, B18 `data_that` có `review_id`, còn lại `tu_viet`); trạng thái đơn đối chiếu `orders.json`. B01–B13 do Việt Anh viết, tự khai công cụ: __ | Việt Anh |
| Sinh data `synthetic` (nếu có) | Claude Code (review + sửa) · bản gốc: Duy Thành tự khai __ | Sửa `policy.json` 1.1 (mỗi mục 1 quyết định, `valid_status_combos`), thêm kiểm chéo policy trong `gen_orders.py` | Không dùng seed ngẫu nhiên — 30 đơn khai tay trong `SCENARIO_SPECS`; `python data/gen_orders.py --verify` khớp file; kiểm tay tổng tiền 4 ca biên (299.999 · 300.000 · 300.001 · 500.000) | Duy Thành |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản | Claude Code | Soạn `spec.md` header, §1, §4 (sơ đồ Mermaid khớp `agent.py`), §5; cập nhật `canvas.md`, `DATA_CARD.md`, `eval/README.md` | Khánh đọc duyệt; số liệu trong canvas / spec chạy lại được từ file gốc (100/300 cờ từ khóa) | Khánh |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
