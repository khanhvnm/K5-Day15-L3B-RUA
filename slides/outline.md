# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Định dạng nào cũng được (PDF, PPTX, HTML…); hoặc nộp link slide (Drive, Canva, Google Slides…) ở form CP4, để ai có link cũng xem được.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Người dùng & pain | Ai · việc gì · chỗ đau + số và trích dẫn | `evidence/summary.md` | ☑ |
| 2 | Vì sao chọn bài này | Bảng impact rút gọn + hướng bị loại | `spec.md` §2 | ☑ |
| 3 | Giải pháp | Lát cắt một câu · sơ đồ · AI tự làm đến đâu, vì sao | `spec.md` §4 | ☑ |
| 4 | Demo live | 1 trường hợp thường + 1 trường hợp khó (lấy từ bộ câu thử); mạng hỏng → video dự phòng | `eval/benchmark.csv` | ☑ |
| 5 | **Đánh giá thế nào** | Dataset · bộ câu thử · metric · lượt 1 → lượt 2 so với chuẩn "đạt" (kèm run ID) · lỗi chính | `eval/README.md`, `eval/report.md` | ☑ |
| 6 | **Chi phí khi dùng thật** | Chi phí / task thành công · 3 kịch bản · so với impact | `cost/cost-estimate.md` | ☑ |
| 7 | Kết luận | Go / iterate / stop — dẫn số ở trang 1, 5, 6 | — | ☑ |
| 8 | Nếu có thêm 1 tuần | 2–3 việc, trỏ về lỗi còn lại / phản hồi người dùng | `eval/report.md` mục 4 · `validation/log.md` | ☑ |

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Ai nói trang nào (mỗi người ≥1 phần):

| Trang | Người nói |
|---|---|
| 1–2 Pain + Impact | Vũ Nam Khánh (số từ Phạm Duy Thành) |
| 3 Giải pháp | Vũ Nam Khánh |
| 4 Demo live | Vũ Thành |
| 5 Đánh giá thế nào | Đỗ Việt Anh |
| 6 Chi phí khi dùng thật | Phạm Duy Thành |
| 7 Kết luận + 8 Nếu có thêm 1 tuần | Vũ Nam Khánh |

**File slide:** nguồn `slides/demo-slides.html` → in ra `demo-slides.pdf` (thư mục gốc, 8 trang) bằng Chrome headless:
`chrome --headless=new --no-pdf-header-footer --print-to-pdf=demo-slides.pdf slides/demo-slides.html`

## Bảng đối chiếu số slide ↔ file nguồn (CP4-R, soát 28/11)

| Trang | Số trên slide | File nguồn | Khớp |
|---|---|---|---|
| 1 | 143/300 (47,7%) · bảo thủ ~42–43% | `evidence/summary.md` §2, §5 · `count_labels.py --check` | ☑ |
| 1 | 20/23 (87%) · 10/20 không giải quyết · 12/20 dùng ít hơn / chuyển app | `evidence/survey/results.csv` (đếm lại bằng script) · `summary.md` §2 | ☑ |
| 1 | Trích dẫn review `2abeceb3…` (ShopeeFood 21/10/2026, 24 hữu ích) · khảo sát stt = 17 | `evidence/summary.md` §3 | ☑ |
| 2 | 11,3% hoàn tiền · 3,0% thiếu/sai món · 3/20 hoàn chậm | `evidence/data-mining.md` §3 · `summary.md` §2 | ☑ |
| 2 | 1,74 lần · 32' + 8,5' ≈ 40' · 1 triệu người (tự ước tính) · ≈ 1,16 triệu giờ · ~15 phút bớt được | `spec.md` §2 | ☑ |
| 3 | trần 300.000đ / 30.000đ · trễ > 60' · khiếu nại ≥ 3 lần · 30 test | `data/policy.json` · `spec.md` §4 · `python -m unittest discover -s tests` | ☑ |
| 4 | Output B01 (HUY_HOAN 110000) · B10 (VOUCHER 30000) · B26 (TU_CHOI, 29') | `eval/run-2.csv` (nguyên văn) | ☑ |
| 5 | 30 câu (9 · 15 · 6 · 11 data thật) · run-1 / run-2 30/30 · 6/6 tu_choi · 6/30 → 0/30 | `eval/README.md` mục 5–6 · `python run.py score eval/run-1.csv` / `run-2.csv` | ☑ |
| 6 | 21 ₫ / 346 ₫ / 14 ₫ per task · 12,1 / 40,5 / 404,6 triệu ₫ · 40 ₫ / người · 50 phiên · 128 lượt · 34% chuyển người | `cost/simulate-1-summary.md` · `cost/cost-estimate.md` · `traces/simulate-1.jsonl` | ☑ |
| 7 | 47,7% · 87% · 30/30 · ≈ 40 ₫ | trang 1, 5, 6 | ☑ |
| 8 | Lỗi #1, #4 · cost mục 4 | `eval/report.md` mục 4 · `cost/cost-estimate.md` mục 4 | ☑ |
