# Khảo sát — đơn giao đồ ăn bị kẹt / trễ (CP2-5)

> Mục tiêu: **≥ 20 người ngoài nhóm** từng đặt đồ ăn qua app. Hỏi **hành vi đã xảy ra** trong 1 tháng qua, không hỏi "có thích không".
> Không thu tên, email, SĐT, mã học viên (trừ câu 12 nếu người trả lời tự để lại).
> Dùng để kiểm lại giả thuyết ở `evidence/hypothesis.md`: "Mình đúng nếu thấy … ≥ 50% người trả lời khảo sát kể từng gặp ít nhất 1 lần đơn bị kẹt/trễ gây ảnh hưởng bữa ăn trong 1 tháng qua".

## Thông tin gửi

| | |
|---|---|
| Link form | __ |
| Kênh đã gửi | __ (vd nhóm chat lớp L3B, nhóm bạn ngoài lớp) |
| Giờ mở | __ (dự kiến theo plan: 17:00 Thứ Sáu 27/11) |
| Giờ chốt | __ |
| Người phụ trách | Vũ Nam Khánh |
| Số người đã trả lời (cập nhật) | __ |

## Bộ câu hỏi

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

## Đếm khi có kết quả (ghi trước khi xem câu trả lời)

- **Mẫu số:** số người trả lời ngoài nhóm có câu 2 khác "không dùng app nào".
- **Số chính 1:** số người có câu 4 ≥ 1 → x / n (%). Đây là số dùng để kiểm giả thuyết (ngưỡng ≥ 50%).
- **Số chính 2:** trong số người gặp kẹt / trễ, số người chọn "muốn hủy nhưng app không cho" ở câu 7, và "không được gì" ở câu 8.
- **Số lần / tháng** (câu 4) và **giá trị đơn** (câu 9) dùng cho persona §8 và kiểm trần 300.000đ trong `data/policy.json`.
- Dưới khoảng 10 người thì chỉ ghi x/n, không ghi %.

## Lưu kết quả

- `results.csv`: bản xuất **đã xoá** mọi cột nhận ra người trả lời (cột liên hệ ở câu 12, dấu thời gian chi tiết). Bản gốc **không** commit.
- Số chính + ≥ 3 câu trả lời nguyên văn (câu 10) → `evidence/summary.md`.
