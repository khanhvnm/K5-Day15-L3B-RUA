# Data card — dữ liệu bản chạy thử dùng

> Tài liệu mô tả 3 tập dữ liệu giả lập (`synthetic`) cho bản chạy thử **FoodResolve AI (Track D1 — Nhóm RUA)** và cách sử dụng nguồn review công khai (không đưa nguyên file review thô vào repo).
>
> Sinh lại / kiểm tra: `python data/gen_orders.py` (ghi `orders.json` + `complaint_history.json`) · `python data/gen_orders.py --verify` (kiểm file đang commit khớp script, kiểm chéo `policy.json`, in bảng `order_id → ca`).

---

## Dataset 1 · `data/orders.json` (Đơn hàng giả lập)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Nguồn tra cứu cho `@tool get_order(order_id)` và kiểm tra điều kiện thời gian/giá trị trong `@tool check_limit`; phục vụ viết bộ câu thử `eval/benchmark.csv`. |
| **Từ đâu** | Nhóm tự dựng có kiểm soát kịch bản (`synthetic`) bằng script [gen_orders.py](gen_orders.py). Mỗi đơn được khai báo tay trong bảng `SCENARIO_SPECS`, script không dùng số ngẫu nhiên nên chạy lại luôn ra cùng một file. |
| **Xử lý những bước gì** | Thiết kế ma trận 30 ca theo đúng 13 trường trong [plan.md](../docs/plan.md) (CP2-1): biên thời gian chưa tài xế `15'/20'/21'/25'/90'`, biên trễ `29'/30'/31'/35'/45'/60'/61'/65'`, đơn nhỏ `22k`, biên trần `299.999đ / 300.000đ / 300.001đ`, đơn tiệc `500k`, quán đã nấu `restaurant_prepared=true`, tài xế đã lấy `picked_up`, đơn đã giao đúng giờ `DH019`, đơn đã hủy để kiểm bồi thường trùng `DH022`, trạng thái mâu thuẫn `DH030`, user `>=3` khiếu nại `DH023–DH025`. Script tự kiểm: `total == sum(qty*price) + ship_fee`, mốc giờ hợp lệ, tên quán chỉ dạng `"Quán Mẫu N"`, mọi `user_id` có trong lịch sử, và chỉ `DH030` có cặp `(status, driver_status)` nằm ngoài `valid_status_combos` của `policy.json`. |
| **Số dòng / số đoạn** | `30` đơn (`DH001`–`DH030`), phủ `18` user (`U01`–`U18`). |
| **Phiên bản / ngày lấy** | Tạo ngày `27/11/2026`. Mỗi đơn có trường `now` riêng (thời điểm khách nhắn, ISO `YYYY-MM-DDTHH:MM`) để kết quả chạy lại luôn giống nhau. `get_order` phải tính `phut_tu_luc_dat = now - placed_at` và `phut_tre_so_voi_eta = now - eta` từ trường này, không dùng giờ hệ thống. |
| **Nhãn** | `synthetic` *(dữ liệu tự dựng để chạy thử, KHÔNG phải bằng chứng pain)*. |
| **Giới hạn** | Mỗi đơn có 1–2 món mẫu, giá tự đặt *(tự ước tính)*. Mọi mốc thời gian nằm trong ngày `2026-11-27`. Không có giờ giao thực tế cho đơn `delivered` nên độ trễ tính theo `now`. Không mô phỏng thanh toán, hoàn tiền một phần hay đơn nhiều quán. |

---

## Dataset 2 · `data/policy.json` (Chính sách giả lập & trần tự động)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Nguồn cấu hình ngưỡng cho `@tool get_policy(issue_type)` và `@tool check_limit`. |
| **Từ đâu** | Nhóm thiết kế (`synthetic`) theo bảng chính sách đề xuất ở mục 0 [plan.md](../docs/plan.md). Các ngưỡng `20/30/60` phút, `30.000đ`, `300.000đ` là *(tự ước tính)*, chưa đối chiếu với chính sách thật của app nào. |
| **Xử lý những bước gì** | Chuẩn hóa thành `13` rules dạng `(issue_type, condition, max_action, max_amount)`, kèm `global_caps`, `valid_status_combos`, `derived_fields`, `request_types` và `decision_priority` (9 mục, **mỗi mục chỉ một quyết định** để chấm tự động được). Tách hai nhánh: `HUY_DON` xét theo `phut_tu_luc_dat` + trạng thái quán/tài xế, `KHIEU_NAI_TRE` xét theo `phut_tre_so_voi_eta`. Quán đã nấu chỉ chặn HỦY (→ `CHUYEN_NV`), không chặn VOUCHER của nhánh trễ. Trần `max_auto_refund_vnd = 300.000đ` (cho `299.999đ`, `300.000đ`; chặn `300.001đ`, `500.000đ`). `complaints_in_month >= 3` chỉ đổi `HUY_HOAN`/`VOUCHER` thành `CHUYEN_NV`. `HUY_HOAN` và `VOUCHER` đều đánh dấu `requires_human_approval` (chỉ tạo bản nháp). |
| **Số dòng / số đoạn** | `13` rules + `global_caps` + `valid_status_combos` + `decision_priority` (9 mục). |
| **Phiên bản / ngày lấy** | `schema_version: 1.1-cp2` (`27/11/2026`). Bản 1.1 so với 1.0: mỗi mục chỉ còn một quyết định, ghi rõ phạm vi của các rule trễ/hủy, thêm `valid_status_combos`, bỏ số liệu không có nguồn. |
| **Nhãn** | `synthetic` *(chính sách giả lập dùng trong hackathon, KHÔNG phải chính sách nội bộ chính thức của ShopeeFood/GrabFood)*. |
| **Giới hạn** | Ngưỡng do nhóm tự đặt, cần rà nghiệp vụ nếu triển khai thật. Phân loại `HUY_DON` / `KHIEU_NAI_TRE` / ngoài phạm vi dựa vào lời khách, nên sai ở bước này sẽ dẫn tới sai rule. Bồi thường trùng chỉ kiểm được trong phiên, data không lưu lịch sử bồi thường theo đơn. |

---

## Dataset 3 · `data/complaint_history.json` (Lịch sử khiếu nại theo tháng)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Nguồn tra cứu số lần khiếu nại trong tháng cho `@tool get_complaint_history(user_id)`. |
| **Từ đâu** | Nhóm tự dựng (`synthetic`), sinh cùng [gen_orders.py](gen_orders.py). |
| **Xử lý những bước gì** | Gán số lần khiếu nại tháng cho `18` user giả lập (`U01`–`U18`), trong đó `3` user chạm ngưỡng `>= 3` lần (`U07=4`, `U08=3`, `U15=5`), gắn với `DH023`, `DH024`, `DH025`. |
| **Số dòng / số đoạn** | `18` user (`U01`–`U18`). |
| **Phiên bản / ngày lấy** | `27/11/2026`. |
| **Nhãn** | `synthetic`. |
| **Giới hạn** | Chỉ lưu tổng số lần theo tháng (`dict[str, int]`), không có ngày hay loại khiếu nại. Con số khách tự khai trong tin nhắn KHÔNG thay thế file này: file này là nguồn sự thật. |

---

## Nguồn ngoài không commit · Review Google Play (`reviews_food_2026.csv`)

| Hạng mục | Nội dung |
|---|---|
| **Dùng để làm gì** | Chỉ dùng cho **bằng chứng pain** (`evidence/`, trích mẫu `300` dòng gắn nhãn) và để Việt Anh **viết lại thành câu thử** trong `eval/benchmark.csv`. **KHÔNG dùng cho AI tra cứu lúc chạy (`runtime`), KHÔNG dùng để suy ra ngưỡng chính sách.** |
| **Từ đâu** | Tập review công khai của các app giao đồ ăn tại Việt Nam năm 2026 (`ShopeeFood: 1.465`, `Grab: 452`, `GreenSM: 245`, `be: 169`, tổng `2.331` dòng 1–2★), lưu ngoài repo tại `docs/no_commit/` (đã chặn trong `.gitignore`). |
| **Xử lý những bước gì** | Script `evidence/scripts/sample_reviews.py` *(CP2-5, đã merge vào `main`; kiểm tái lập: `--verify`)* lấy ngẫu nhiên `300` review (`seed=42`), bỏ cột `user_hash`, cắt còn `<= 2` câu và tự động che SĐT/email/biển số trước khi đưa vào `evidence/labels/`. |
| **Nhãn** | `dữ liệu thật đã ẩn danh`. |
| **Giới hạn** | Chỉ gồm review `1–2★` nên thiên về người dùng đang bức xúc. Không đại diện cho tỷ lệ % đơn hàng ngoài thực tế, nên cần kiểm chéo bằng khảo sát và phỏng vấn. |
