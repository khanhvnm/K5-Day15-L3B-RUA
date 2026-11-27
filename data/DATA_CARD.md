# Data card — dữ liệu bản chạy thử dùng

> Tài liệu mô tả 3 tập dữ liệu giả lập (`synthetic`) cho bản chạy thử **FoodResolve AI (Track D1 — Nhóm RUA)** và cách sử dụng nguồn review công khai (không đưa nguyên file review thô vào repo).

---

## Dataset 1 · `data/orders.json` (Đơn hàng giả lập)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Nguồn tra cứu cho `@tool get_order(order_id)` và kiểm tra điều kiện thời gian/giá trị trong `@tool check_limit`; phục vụ sinh bộ câu thử `eval/benchmark.csv`. |
| **Từ đâu** | Nhóm tự sinh có kiểm soát kịch bản (`synthetic`), viết bằng script [gen_orders.py](file:///D:/Hackathon/K5-Day15-L3B-RUA/data/gen_orders.py) với `seed = 42`. |
| **Xử lý những bước gì** | Thiết kế ma trận 30 ca chuẩn đúng 13 trường của [plan.md](file:///D:/Hackathon/K5-Day15-L3B-RUA/docs/plan.md) (biên thời gian chưa tài xế `15'/20'/21'/25'/90'`, biên trễ `29'/30'/31'/35'/45'/60'/61'/65'`, đơn nhỏ `22k`, biên trần `299.999đ / 300.000đ / 300.001đ`, đơn tiệc `500k`, quán đã nấu `restaurant_prepared=true`, tài xế đã lấy `picked_up`, đơn đúng giờ `DH019`, đơn đã hủy kiểm bồi thường trùng `DH022`, dữ liệu trạng thái mâu thuẫn `DH030`, user `>=3` khiếu nại `DH023–DH025`); kiểm tra tự động `total == sum(items) + ship_fee` và đảm bảo chỉ dùng tên `"Quán Mẫu N"`. |
| **Số dòng / số đoạn** | `30` đơn (`DH001`–`DH030`), phủ `18` user (`U01`–`U18`). |
| **Phiên bản / ngày lấy** | Tạo ngày `27/11/2026` (`seed = 42`, cố định trường `now` theo chuẩn ISO `YYYY-MM-DDTHH:MM` để kết quả chạy lại luôn giống nhau). |
| **Nhãn** | `synthetic` *(dữ liệu tự dựng để chạy thử, KHÔNG phải bằng chứng pain)*. |
| **Giới hạn** | Chỉ gồm 1 món hoặc vài món mẫu, dùng thời điểm giả lập `now` cố định trong ngày `2026-11-27`; chưa phản ánh toàn bộ biến động thực tế của API đối tác thanh toán. |

---

## Dataset 2 · `data/policy.json` (Chính sách giả lập & Trần tự động)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Nguồn cấu hình ngưỡng xử lý cho `@tool get_policy(issue_type)` và `@tool check_limit`. |
| **Từ đâu** | Nhóm thiết kế (`synthetic`) dựa trên bảng mục 0 trong [plan.md](file:///D:/Hackathon/K5-Day15-L3B-RUA/docs/plan.md), tham khảo thông lệ ngành (GrabFood / ShopeeFood / BeFood / DoorDash Auto-refund cap) và phân tích phân bố giá trị đơn / thời gian chờ từ nguồn review công khai. |
| **Xử lý những bước gì** | Chuẩn hóa thành `13` rules có `(issue_type, condition, max_action, max_amount)`; tách rõ yêu cầu HỦY khi `restaurant_prepared = true` (`CHUYEN_NV`) khỏi khiếu nại giao trễ trên đơn `delivering` (`VOUCHER <= 30.000đ` khi thỏa 4 điều kiện); đặt `max_auto_refund_vnd = 300.000đ` (cho phép `<= 300.000đ` như `299.999đ`, `300.000đ`; chặn `300.001đ`, `500.000đ`); bổ sung `inconsistent_order_state`, `duplicate_compensation`, và quy định rõ `complaints_in_month >= 3` chỉ chặn `HUY_HOAN` và `VOUCHER` (không đè lên `HOI_LAI` hay `TU_CHOI`). |
| **Số dòng / số đoạn** | `13` rules + `global_caps` + `decision_priority`. |
| **Phiên bản / ngày lấy** | `schema_version: 1.0-cp2` (`27/11/2026`). |
| **Nhãn** | `synthetic` *(chính sách giả lập dùng trong hackathon, KHÔNG phải chính sách nội bộ chính thức của ShopeeFood/GrabFood)*. |
| **Giới hạn** | Các mốc `20/30/60` phút và `30.000đ / 300.000đ` là ngưỡng giả lập phục vụ đánh giá Guardrails, cần rà soát nghiệp vụ nếu triển khai thật. |

---

## Dataset 3 · `data/complaint_history.json` (Lịch sử khiếu nại theo tháng)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Nguồn tra cứu số lần khiếu nại trong tháng cho `@tool get_complaint_history(user_id)`. |
| **Từ đâu** | Nhóm tự sinh (`synthetic`) cùng script `data/gen_orders.py`. |
| **Xử lý những bước gì** | Gán số lần khiếu nại tháng cho `18` user giả lập (`U01`–`U18`), trong đó có `3` user chạm ngưỡng `>= 3` lần (`U07=4`, `U08=3`, `U15=5`) gắn với `DH023`, `DH024`, `DH025`. |
| **Số dòng / số đoạn** | `18` user (`U01`–`U18`). |
| **Phiên bản / ngày lấy** | `27/11/2026`. |
| **Nhãn** | `synthetic`. |
| **Giới hạn** | Lưu tổng số đếm theo tháng (`dict[str, int]`) đúng hợp đồng CP2 trong `docs/plan.md`; bồi thường trùng kiểm qua trạng thái `cancelled` (`DH022`) + lịch sử cùng `(order_id, issue_type, loại bồi thường)` trong phiên ở `check_limit`. |

---

## Nguồn ngoài không commit · Review Google Play (`reviews_food_2026.csv`)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Chỉ dùng cho **bằng chứng pain** (`evidence/`, trích mẫu `300` dòng gắn nhãn) và để Việt Anh **viết lại thành câu thử** trong `eval/benchmark.csv`. **KHÔNG dùng cho AI tra cứu lúc chạy (`runtime`).** |
| **Từ đâu** | Tập review công khai của các app giao đồ ăn tại Việt Nam năm 2026 (`ShopeeFood: 1.465`, `Grab: 452`, `GreenSM: 245`, `be: 169` — tổng `2.331` dòng 1–2★), lưu ngoài repo tại `docs/no_commit/` (đã chặn trong `.gitignore`). |
| **Xử lý những bước gì** | Script `evidence/scripts/sample_reviews.py` lấy ngẫu nhiên `300` review (`seed=42`), bỏ cột `user_hash`, cắt `<= 2` câu và quét che tự động SĐT/email/biển số trước khi đưa vào `evidence/labels/`. |
| **Nhãn** | `dữ liệu thật đã ẩn danh`. |
| **Giới hạn** | Chỉ gồm review `1–2★` nên thiên lệch về người dùng đang bức xúc; không đại diện cho tỷ lệ % toàn bộ đơn hàng ngoài thực tế, nên phải kiểm chéo lại bằng khảo sát và phỏng vấn. |
