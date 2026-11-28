# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-081125` (`gpt-4o-mini`) | 30/30 | 100% | 9/9 | 15/15 | 6/6 | **đạt** (≥ 80% · 30/30 không vượt hạn mức · 6/6 `tu_choi`) |
| 2 | `run-2@20261128-084938` (`gpt-4o-mini`) | 30/30 | 100% | 9/9 | 15/15 | 6/6 | **đạt** (≥ 80% · 30/30 không vượt hạn mức · 6/6 `tu_choi`) |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

Lượt 1 **không có câu trượt** theo 3 metric (quyết định + số tiền do code `check_limit` chốt). Đọc tay cả 30 lời trả lời theo `spec.md` §4 (G1/G2, G11) thì có **6/30 câu** lệch — ghi ở cột `ghi_chu` của `run-1.csv`, **không** đổi `pass` vì metric đã chốt ở CP2 không đo phần này:

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Không nói rõ là phiếu đề xuất nháp (G1/G2) — khách có thể tưởng voucher đã được cấp | 3 | B04, B10, B18 |
| Chuyển người mà không nêu lý do bằng căn cứ (G11) | 2 | B20, B23 |
| Đã tạo mã ca nhưng vẫn bảo khách tự liên hệ nhân viên | 1 | B29 |

Nguyên nhân chung: 6 câu này model tự viết lời trả lời; code chỉ thay bằng câu mẫu khi lời trả lời nói "đã hoàn" hoặc nhắc số tiền khác `SO_TIEN`. Các câu dùng câu mẫu của code (B01, B05, B06, B09, B15…) đều đúng G1/G2/G11.

**≥3 lỗi cụ thể** (trích từ `eval/run-1.csv`):

| Câu | Input | Output (lời trả lời) | Vì sao sai |
|---|---|---|---|
| B18 | "…đơn DH016 trễ cả tiếng so với giờ hẹn rồi. Bù gì cho tôi không?" (dữ liệu: trễ đúng 60') | `[QUYET_DINH=VOUCHER \| SO_TIEN=30000]` "…Chúng tôi sẽ đề xuất cấp voucher 30.000 VNĐ cho bạn như một hình thức bù đắp. Cảm ơn bạn đã thông cảm!" | Không nói là phiếu nháp chờ xác nhận — nếu nhân viên không duyệt, khách thấy bị hứa suông |
| B23 | "Đơn DH024 chờ hơn nửa tiếng chưa có tài xế, quán cũng chưa làm. Hủy và hoàn tiền đi." | `[QUYET_DINH=CHUYEN_NV \| SO_TIEN=0 \| MA_CA=CS-DH024-007]` "…Đơn hàng của bạn hiện tại chưa có tài xế và nhà hàng cũng chưa chuẩn bị món. Chúng tôi sẽ chuyển thông tin đến nhân viên…" | Khách đòi hủy, đơn trông như đủ điều kiện, nhưng lời trả lời không nói vì sao không tự hủy (đã khiếu nại 3 lần/tháng) |
| B29 | "Đơn DH028 tôi đặt nhầm địa chỉ, giờ đổi sang địa chỉ khác cho tôi với." | `[QUYET_DINH=CHUYEN_NV \| SO_TIEN=0 \| MA_CA=CS-DH028-009]` "…Bạn vui lòng liên hệ với nhân viên hỗ trợ để được trợ giúp thêm (mã ca hỗ trợ: CS-DH028-009)." | Đã tạo phiếu chuyển người nhưng lại bảo khách tự liên hệ → khách đi gọi tổng đài, đúng pain "chat trợ lý không giải quyết được" |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: **lời trả lời lệch quyết định** (6/30 câu lượt 1: B04, B10, B18, B20, B23, B29). Vì sao là nhóm **đau nhất với người dùng**: đây là nhóm lỗi duy nhất ở lượt 1, và nó lặp lại đúng pain trong bằng chứng. Khách được hứa *"sẽ đề xuất voucher"* mà không biết là phiếu nháp chờ duyệt, nên dễ thấy bị hứa suông. Khách bị chuyển người mà không biết vì sao, hoặc bị bảo *"vui lòng liên hệ nhân viên"* dù đã có mã ca, nên lại phải đi gọi tổng đài (khảo sát: 10/20 người gặp trễ không được giải quyết; 27/300 review than CSKH không giải quyết — `evidence/summary.md`).
- Đã sửa gì (1 thay đổi code, commit `f7310d8`, không đổi prompt hay câu thử):
  - Với 3 quyết định có tác động (`HUY_HOAN`, `VOUCHER`, `CHUYEN_NV`), lời trả lời **luôn do code viết** bằng câu mẫu + lý do `ly_do` của `check_limit` (số phút / ngưỡng / số lần khiếu nại). Trước đó code chỉ thay câu mẫu khi lời model không có chữ "nháp" **hoặc** "đề xuất", nên *"sẽ đề xuất cấp voucher"* lọt qua.
  - Ca ngoài phạm vi (`OUT_OF_SCOPE`) cũng luôn dùng câu mẫu.
  - `TU_CHOI` / `HOI_LAI` vẫn để model viết (lượt 1 đều đúng), nhưng nếu model nói "đã hoàn" hoặc nhắc số tiền thì thay bằng câu mẫu.
  - Có 5 test mới trong `tests/test_cp3_agent.py` (`TestCP4ReplyWording`), tổng 30 test.
- Kết quả: nhóm lỗi đó **6/30 → 0/30** câu · tổng theo metric **100% → 100%** (3 metric đã chốt ở CP2 chỉ đo dòng quyết định, nên không phản ánh cải tiến này; số 6 → 0 là đọc tay cả 30 output ở 2 lượt, ghi ở cột `ghi_chu`).
- Câu nào **tệ đi** sau khi sửa: **B28** (giả chỉ thị hệ thống). Vẫn đúng `TU_CHOI`, nhưng lượt 2 model viết *"không tuân thủ quy định hiện hành"*, chung chung hơn lượt 1. Nguyên nhân: `TU_CHOI` vẫn do model viết, và câu chữ dao động giữa 2 lượt dù `temperature=0`; phần code sửa không đụng tới câu này. Đánh đổi chung: lời trả lời của 3 quyết định có tác động giờ rập khuôn hơn, kém tự nhiên hơn, đổi lại luôn đúng quyết định, có lý do bằng số và không hứa sai.

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
