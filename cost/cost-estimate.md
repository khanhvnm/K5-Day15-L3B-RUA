# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): 3 kiểu, chia theo số lần gặp đơn trễ ≥ 15'/tháng. Nguồn: khảo sát `evidence/survey/results.csv` câu 6, n = 23 người đặt đồ ăn.

  | Persona | Tỉ lệ | Phiên / người / tháng | Lượt hỏi / phiên | Nguồn |
  |---|---:|---:|---:|---|
  | `dung_it_tre_it` | 0,48 (11/23) | 0,73 (trung điểm: 3 người 0 lần + 8 người 1 lần) | 2 *(tự ước tính)* | khảo sát câu 6 |
  | `dung_vua_tre_vua` | 0,48 (11/23) | 2,5 (trung điểm 2–3 lần) | 3 *(tự ước tính)* | khảo sát câu 6 |
  | `dung_nhieu_khieu_nai_cao` | 0,04 (1/23) | 4,5 (trung điểm 4–5 lần) | 4 *(tự ước tính)* | khảo sát câu 6 |

  Bình quân ≈ 1,73 phiên / người / tháng, khớp 1,74 lần ở `spec.md` §2. Giả định **mỗi lần đơn trễ là một phiên chat**. Thực tế chỉ 12/20 người gặp trễ có liên hệ (khảo sát câu 12), nên chi phí ở đây là **cận trên**.
- **Số người dùng thật** 3 kịch bản: thấp **300.000** · cơ sở **1.000.000** · cao **10.000.000**. Nguồn: **chưa có số công khai về số người dùng app giao đồ ăn**.
  - Mức cao = toàn bộ người dùng app be: *"hiện là kênh tiếp cận hơn 10 triệu người dùng"*, tính cho cả app (gọi xe + giao đồ ăn + dịch vụ khác) — CafeBiz, đăng 20/05/2025, https://cafebiz.vn/be-group-tang-toc-nguoi-dung-tang-50-gmv-tang-60-pha-hoi-nong-vao-grab-va-xanh-sm-176250520162320667.chn.
  - Mức cơ sở = 10% con số đó, khớp `spec.md` §2 *(tự ước tính)*.
  - Mức thấp = thí điểm *(tự ước tính)*.
- **Giá** 3 model (USD / 1 triệu token, gói trả phí chuẩn):
  - `gpt-4o-mini` (Nhỏ — model đang chạy): vào 0,15 · ra 0,60 — https://openai.com/api/pricing/ · xem 28/11/2026
  - `gpt-4o` (Lớn): vào 2,50 · ra 10,00 — https://openai.com/api/pricing/ · xem 28/11/2026
  - `gemini-2.5-flash-lite` (rẻ hơn, tham chiếu): vào 0,10 · ra 0,40 — https://ai.google.dev/gemini-api/docs/pricing · xem 27/11/2026
  - Tỷ giá 1 USD = 26.010 ₫ (Vietcombank bán ra 27/11/2026).
  - Nhóm không truy cập được `further-reading/model-prices.md` của repo đề, nên giá chép từ trang giá chính thức của nhà cung cấp.
- **Tỉ lệ đạt** dùng để tính: **30/30 (100%)** — lượt `run-2@20261128-084938` (lượt 2, `--rate-from eval/run-2.csv`).
- Đo token trên model **`gpt-4o-mini`**, tính giá model **`gpt-4o`** và **`gemini-2.5-flash-lite`**. Hai model này chưa chạy thật: bộ tách token khác nên số token thật có thể lệch, và tỉ lệ đạt trên 2 model này **chưa đo**.

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-1.csv` · run ID `simulate-1@20261128-085957` · **50 phiên** (128 lượt hỏi, 0 phiên lỗi) · seed **42** · tóm tắt `cost/simulate-1-summary.md`

| Persona | Số phiên | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it_tre_it | 24 | 2 | 3269 | 229 | 2.0 | 8.2 |
| dung_vua_tre_vua | 24 | 3 | 4916 | 342 | 3.0 | 11.9 |
| dung_nhieu_khieu_nai_cao | 2 | 4 | 5908 | 415 | 3.5 | 14.5 |

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp (300.000) | / tháng — cơ sở (1.000.000) | / tháng — cao (10.000.000) | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| **gpt-4o-mini** (đang chạy) | $0.00080 (≈ 21 ₫) | $0.00080 (≈ 21 ₫) | $466.67 (≈ 12,1 triệu ₫) | $1,555.58 (≈ 40,5 triệu ₫) | $15,555.83 (≈ 404,6 triệu ₫) | $0.0016 (≈ 40 ₫) |
| gpt-4o | $0.0133 (≈ 346 ₫) | $0.0133 (≈ 346 ₫) | $7,777.92 (≈ 202,3 triệu ₫) | $25,926.38 (≈ 674,3 triệu ₫) | $259,263.84 (≈ 6,74 tỷ ₫) | $0.0259 (≈ 674 ₫) |
| gemini-2.5-flash-lite | $0.00053 (≈ 14 ₫) | $0.00053 (≈ 14 ₫) | $311.12 (≈ 8,1 triệu ₫) | $1,037.06 (≈ 27,0 triệu ₫) | $10,370.55 (≈ 269,7 triệu ₫) | $0.0010 (≈ 27 ₫) |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**. Ở đây tỉ lệ đạt đo được **đúng là** 30/30, nên chi phí / task thành công = chi phí / phiên. Nhưng 30/30 là trên bộ câu nhóm tự viết, data giả (`eval/report.md` mục 4). Nếu ngoài đời chỉ đạt 80% (ngưỡng "đạt" ở `spec.md` §7), chi phí / task thành công của `gpt-4o-mini` là ≈ 26 ₫.

## 3. So với impact

- **Impact / người / tháng** (`spec.md` §2): khách đặt đồ ăn mất **≈ 70 phút / tháng** vì đơn kẹt/trễ (1,74 lần × 40'). Phần lát cắt **chắc chắn** bớt được là thời gian liên hệ / xử lý: 1,74 lần × 8,5' ≈ **15 phút / người / tháng**. Phần chờ bớt được ở ca hủy sớm chưa đo.
- **Chi phí / người / tháng** (cơ sở, model `gpt-4o-mini`): **$0.0016 ≈ 40 ₫**, tức ≈ 3 ₫ cho mỗi phút liên hệ bớt được.
- **Kết luận một dòng — đáng làm không:** **đáng làm, nếu tính chi phí model.** 40 ₫ / người / tháng với `gpt-4o-mini` là quá nhỏ so với ~15 phút khách được bớt. Chi phí thật quyết định bài toán nằm ở **bồi thường** (voucher ≤ 30.000 ₫, hoàn ≤ 300.000 ₫ mỗi ca, do chính sách chứ không do AI) và **giờ công nhân viên duyệt ca chuyển người**, chưa tính ở đây (mục 4). Giữ `gpt-4o-mini`: `gpt-4o` đắt gấp ~16 lần mà chưa có bằng chứng tốt hơn, vì quyết định và số tiền đã do code chốt.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- **Chi phí ngoài model (chưa tính tiền):** trong 128 lượt hỏi mô phỏng, **44 lượt (34%)** gọi `escalate_to_human`, tức tạo ca chờ nhân viên duyệt (đếm từ `traces/simulate-1.jsonl`). Tỉ lệ này theo **phân bố của bộ câu thử** (15/30 câu `kho`, chọn để thử ca khó), không phải tỉ lệ ngoài đời. Nhưng nó cho thấy giờ công CSKH có thể lớn hơn chi phí model nhiều lần. Cần số ca/giờ của một nhân viên và lương để tính *(chưa có nguồn)*.
- **Cần gạt rẻ nhất:** đổi sang `gemini-2.5-flash-lite` giảm ≈ 33% chi phí model (40 → 27 ₫ / người / tháng), nhưng phải chạy lại eval trên model đó trước khi đổi.
  - Mỗi lượt gửi ≈ 1.600 token vào, phần lớn là prompt `SYSTEM` + dữ liệu đơn. Dùng cache đầu vào (giá cache của `gpt-4o-mini` $0.075/1M, bằng nửa giá thường) có thể giảm thêm. Mô phỏng chưa tính cache.
- **Quy mô nào vẫn đáng làm:** chi phí model tăng tuyến tính theo số người (≈ 40 ₫ / người / tháng), nên ở mọi quy mô trong bảng, chi phí model không phải điểm chặn. Điểm chặn là tỉ lệ ca chuyển người và tiền bồi thường.
