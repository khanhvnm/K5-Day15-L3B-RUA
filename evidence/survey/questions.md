# Khảo sát — đơn giao đồ ăn bị kẹt / trễ (CP2-5)

> Mục tiêu: **≥ 20 người ngoài nhóm** từng đặt đồ ăn qua app. Hỏi **hành vi đã xảy ra** trong 1 tháng qua, không hỏi "có thích không".
> Không thu tên, email, SĐT, mã học viên (trừ câu cuối nếu người trả lời tự để lại cách liên hệ).
> Dùng để kiểm lại giả thuyết ở `evidence/hypothesis.md`: "Mình đúng nếu thấy … ≥ 50% người trả lời khảo sát kể từng gặp ít nhất 1 lần đơn bị kẹt/trễ gây ảnh hưởng bữa ăn trong 1 tháng qua".

## Thông tin gửi

| | |
|---|---|
| Link form | https://forms.gle/Yvuo3at8kf6hLmkp8 |
| Kênh đã gửi | Discord lớp, bạn bè |
| Giờ mở | 17:00 Thứ Sáu 27/11/2026 (câu trả lời đầu tiên lúc 17:01) |
| Bản xuất dùng để đếm | câu trả lời cuối lúc 22:12 Thứ Sáu 27/11/2026 |
| Người phụ trách | Vũ Nam Khánh |
| Số người đã trả lời | **26 lượt gửi → 25 người** sau khi bỏ 1 lượt trùng email (luật ở mục "Lưu kết quả") |

## Bộ câu hỏi đã gửi thật (Google Form)

Form thật khác bản nháp ở dưới: hỏi theo **khoảng** thay vì số, gộp "hủy được không" và "được bù gì" thành một câu "Kết quả cuối cùng", thêm câu về tình trạng đơn, thời gian liên hệ và ảnh hưởng. Cột "Lựa chọn" chép từ các câu trả lời trong bản xuất, nên lựa chọn không ai chọn sẽ không có ở đây.

| # | Câu hỏi (nguyên văn trên form) | Kiểu · lựa chọn đã thấy |
|---|---|---|
| 1 | Bạn là | Chọn một / tự nhập: Học viên L3B · Học viên L3A · bạn bè (nhiều người tự gõ "Bạn", "Ban be"…) |
| 2 | Trong 1 tháng qua, bạn có đặt đồ ăn qua app không? | Có · Không |
| 3 | Bạn đặt qua app nào? | Chọn nhiều: ShopeeFood · Grab · be · GreenSM |
| 4 | Một tháng qua bạn đặt khoảng bao nhiêu đơn? | 1 – 3 · 4 – 8 · 9 – 15 · Trên 15 |
| 5 | Một đơn của bạn thường hết bao nhiêu (cả ship)? | Dưới 50k · 50 – 100k · 100 – 200k · Trên 200k |
| 6 | Một tháng qua, bao nhiêu lần đơn của bạn giao muộn hơn giờ dự kiến app báo từ 15 phút trở lên? | 0 lần · 1 lần · 2 – 3 lần · 4 – 5 lần · … |
| 7 | Lần đó cách đây bao lâu? | Tuần này · Tuần trước · 2 – 4 tuần trước |
| 8 | App báo đơn đang ở tình trạng nào? | Đang tìm tài xế · Tài xế đã nhận đơn nhưng giao rất chậm (khả năng cao là ghép đơn) · Không rõ / App không báo · khác (tự nhập) |
| 9 | Đơn đến muộn hơn giờ dự kiến bao lâu? | 15 – 30 phút · 30 – 60 phút · Không nhớ · … |
| 10 | Lần đó bạn đã làm gì? | Chọn nhiều: Chờ tiếp, không làm gì · Thử huỷ đơn trong app · Chat với trợ lý ảo trong app · Gọi tổng đài / CSKH · Nhắn / gọi tài xế hoặc quán |
| 11 | Kết quả cuối cùng? | Huỷ được và hoàn đủ tiền · Huỷ được nhưng hoàn chậm hoặc thiếu · Được bù voucher · Không huỷ được, vẫn phải nhận đơn · Không ai giải quyết · khác (tự nhập) |
| 12 | Bạn mất bao lâu để liên hệ / giải quyết (không tính thời gian chờ đồ ăn)? | Không liên hệ · Dưới 5 phút · 5 – 15 phút · 15 – 30 phút · Trên 30 phút |
| 13 | Lần đó bạn bị ảnh hưởng gì? | Chọn nhiều: Đồ ăn nguội, hỏng · Bỏ bữa hoặc ăn muộn · Trễ việc · Không bị ảnh hưởng gì nhiều · khác (tự nhập) |
| 14 | Sau lần đó, bạn dùng app đó thế nào? | Vẫn như cũ · Dùng ít hơn · Chuyển sang app khác · … |
| 15 | Kể ngắn điều khiến bạn khó chịu nhất lần đó | Đoạn văn (không bắt buộc) |
| 16 | Bạn có sẵn lòng cho nhóm hỏi thêm 10 phút không? Nếu có, để lại cách liên hệ | Đoạn văn (không bắt buộc) |

**Lệch so với quy định "không thu email":** form bật *thu địa chỉ email* (cột `Email Address`, 19 email). Cột này chỉ dùng để bỏ lượt gửi trùng, rồi bị xoá khỏi `results.csv`; bản gốc không commit.

## Đếm khi có kết quả (ghi trước khi xem câu trả lời)

Luật ghi trước theo bản nháp, đổi số câu cho khớp form thật (nội dung luật không đổi):

- **Mẫu số:** số người trả lời có câu 2 = "Có" (bản nháp: câu 2 khác "không dùng app nào").
- **Số chính 1:** số người có câu 6 khác "0 lần" → x / n (%). Đây là số dùng để kiểm giả thuyết (ngưỡng ≥ 50%). *(Bản nháp: câu 4 ≥ 1.)*
- **Số chính 2:** trong số người gặp trễ, số người chọn "Không huỷ được, vẫn phải nhận đơn" và "Không ai giải quyết" ở câu 11. *(Bản nháp: câu 7 "muốn hủy nhưng app không cho", câu 8 "không được gì".)*
- **Số lần / tháng** (câu 6) và **giá trị đơn** (câu 5) dùng cho persona §8 và kiểm trần 300.000đ trong `data/policy.json`.
- Dưới khoảng 10 người thì chỉ ghi x/n, không ghi %.

**Kiểm "ngoài nhóm":** câu 1 không có lựa chọn "thành viên nhóm RUA" mà nhóm học L3B, nên không loại được người trong nhóm bằng dữ liệu. Không email nào trùng email tác giả commit trong repo. **Cả 4 thành viên đã xác nhận không điền form (23:40 27/11)** — 25 người trả lời đều là người ngoài nhóm.

## Lưu kết quả

- `results.csv`: sinh bằng `python evidence/scripts/anonymize_survey.py` (thêm `--dem` để in số theo luật trên) từ bản xuất gốc `raw-khaosat.csv` (`.gitignore` chặn `evidence/**/raw-*`, **không** commit). Script:
  1. **Bỏ lượt trùng:** cùng một email gửi nhiều lần → giữ lượt gửi **cuối** (người trả lời sửa lại câu trả lời). Luật này chốt lúc 23:25 27/11 sau khi thấy có 1 email gửi 2 lần, **trước khi** đếm số chính. Lượt không có email thì giữ nguyên.
  2. **Xoá cột nhận dạng:** `Timestamp`, `Email Address`, cột cách liên hệ (câu 16 — chỉ giữ cột `de_lai_lien_he` = có / không). Thay bằng cột `stt`.
  3. **Gộp cách viết tay** ở câu 1: "Bạn", "Ban", "Bạn bè", "Ban be" → "Bạn bè ngoài lớp".
- Số chính + ≥ 3 câu trả lời nguyên văn (câu 15) → `evidence/summary.md` (CP3-4).

---

## Bản nháp ban đầu (giữ lại để đối chiếu, không phải bộ câu đã gửi)

| # | Câu hỏi | Kiểu trả lời |
|---|---|---|
| 1 | Bạn là: học viên L3B / học viên lớp khác / người đi làm / sinh viên ngoài khoá / khác | Chọn một |
| 2 | Bạn thường đặt đồ ăn qua app nào? | Chọn nhiều: ShopeeFood · GrabFood · be · Xanh SM Ngon · khác · không dùng app nào |
| 3 | Trong 1 tháng qua, bạn đặt đồ ăn qua app khoảng bao nhiêu đơn? | Số |
| 4 | Trong 1 tháng qua, có bao nhiêu lần đơn của bạn bị kẹt (lâu chưa có tài xế nhận / bị ghép đơn) hoặc giao trễ hơn giờ dự kiến? | Số (0 nếu chưa gặp) |
| 5 | Lần gần nhất đó, đơn trễ thêm khoảng bao lâu so với giờ dự kiến? | Dưới 15' · 15–30' · 30–60' · trên 60' · đơn bị hủy |
| 6 | Lần đó bạn đã làm gì? | Chọn nhiều: chờ tiếp · cố bấm hủy · chat trợ lý trong app · gọi tổng đài · nhắn / gọi tài xế · bỏ, đặt chỗ khác · khác |
| 7 | Lần đó bạn có hủy được đơn không? | Hủy được · muốn hủy nhưng app không cho · không muốn hủy |
| 8 | Lần đó bạn có được hoàn tiền hoặc voucher bù không? | Được hoàn tiền · được voucher · không được gì · không yêu cầu |
| 9 | Giá trị đơn lần đó khoảng bao nhiêu? | Dưới 50k · 50–100k · 100–300k · trên 300k |
| 10 | Điều gì khó chịu nhất ở lần đó? | Đoạn văn |
| 11 | Sau lần đó, bạn có giảm dùng app đó không? | Không đổi · dùng ít hơn · chuyển sang app khác · bỏ hẳn |
| 12 | (tuỳ chọn) Bạn có sẵn lòng cho nhóm hỏi thêm 10 phút không? | Có — cách liên hệ (không bắt buộc) · Không |
