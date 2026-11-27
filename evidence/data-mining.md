# Đào data — cách đếm và kết quả

> Điền phần 1 và phần 2 **TRƯỚC khi đếm** (CP2-5). Phần 3–5 sẽ cập nhật tại CP3-4 sau khi cả 4 thành viên gắn nhãn xong `part1.csv .. part4.csv` và kiểm độ khớp 30 dòng chung.

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** Tập review công khai 4 app giao đồ ăn (`ShopeeFood: 1.465`, `Grab: 452`, `GreenSM: 245`, `be: 169` — tổng `2.331` dòng mức `1–2★`, năm 2026), file thô để tại `docs/no_commit/reviews_food_2026.csv` *(không commit lên GitHub)*.
- **Đếm gì · trên tập nào · lọc gì:** Lấy ngẫu nhiên **300 review** bằng `seed = 42` trên **toàn bộ 4 app** (`1–2★`, độ dài `>= 8` ký tự; cơ cấu mẫu thu được: `ShopeeFood: 193`, `Grab: 53`, `GreenSM: 35`, `be: 19` — khớp phần *"Nguồn sẽ kiểm"* trong `canvas.md` và CP2-5 trong `docs/plan.md`, phân biệt với ước lượng thô CP1 trên `1.465` review ShopeeFood), gắn **1 nhãn chính (`nhan`)** mô tả nguyên nhân bức xúc cốt lõi nhất (hoặc ghi nhãn phụ vào `ghi_chu`), sau đó tính `x / 300 (%)` và tổng `thumbs_up` theo từng nhãn. Chia 4 phần bằng nhau cho 4 thành viên (`part1..4.csv`, mỗi người `75` dòng) + `overlap_30_thanh.csv` (`30` dòng từ `part1` để Duy Thành và Khánh gắn chéo kiểm độ khớp).
- **Mẫu số là gì:** **`N = 300`** review trong mẫu ngẫu nhiên đã trích (bao gồm cả review không liên quan đơn kẹt/trễ như `thieu_sai_mon` hoặc `khac` để không làm méo mẫu số).
- **Script / công thức:** [sample_reviews.py](file:///D:/Hackathon/K5-Day15-L3B-RUA/evidence/scripts/sample_reviews.py) (`seed = 42`). Script gộp & đếm `x/300` sẽ hoàn thiện tại nhánh CP3-4 sau khi đủ 4 file part.

## 2. Đọc trước, đếm sau — Định nghĩa bộ nhãn

Sau khi rà các dòng đầu và phân tích sơ bộ bài toán D1, định nghĩa **8 nhãn** cố định trước khi gắn nhãn:

| Mã nhãn (`nhan`) | Định nghĩa kiểm chứng (dùng thống nhất giữa 4 người gắn nhãn) |
|---|---|
| `cho_tai_xe` | Phản ánh đặt đơn lâu nhưng không có/mãi chưa có tài xế nhận đơn |
| `ghep_don` | Nhắc trực tiếp việc app/tài xế ghép nhiều đơn khiến thời gian giao kéo dài hoặc đồ nguội |
| `giao_tre` | Phàn nàn giao trễ so với dự kiến, đợi quá lâu (nhưng không nhắc rõ ghép đơn hay chưa có tài xế) |
| `khong_huy_duoc` | Muốn hủy đơn (khi kẹt/chậm/đặt nhầm) nhưng app khóa nút hủy hoặc không cho hủy |
| `cskh_khong_giai_quyet` | Phàn nàn chatbot trả lời rập khuôn, tổng đài/CSKH không hỗ trợ hoặc xử lý chậm |
| `hoan_tien` | Trừ tiền không có đơn, hủy đơn nhưng không hoàn tiền / treo hoàn tiền / ép đổi sang voucher |
| `thieu_sai_mon` | Quán giao thiếu món, sai món, đồ hỏng/ôi thiu *(ngoài phạm vi tự động D1 — phải chuyển người)* |
| `khac` | Lỗi app/định vị/thanh toán, phí ship/deal, thái độ tài xế, hoặc nhận xét chung không rõ lỗi |

## 3. Kết quả *(sẽ điền sau khi cả nhóm gắn xong 300 dòng tại CP3-4)*

| Đếm gì | x / N | % | Tổng thumbs_up | Ghi chú |
|---|---:|---:|---:|---|
| `cho_tai_xe` | `/300` | | | Chờ tổng hợp CP3 |
| `ghep_don` | `/300` | | | Chờ tổng hợp CP3 |
| `giao_tre` | `/300` | | | Chờ tổng hợp CP3 |
| `khong_huy_duoc` | `/300` | | | Chờ tổng hợp CP3 |
| `cskh_khong_giai_quyet` | `/300` | | | Chờ tổng hợp CP3 |
| `hoan_tien` | `/300` | | | Chờ tổng hợp CP3 |
| `thieu_sai_mon` | `/300` | | | Chờ tổng hợp CP3 |
| `khac` | `/300` | | | Chờ tổng hợp CP3 |

- Độ khớp gắn nhãn chéo (`30` dòng chung giữa Duy Thành và Khánh): `__/30`.

## 4. ≥5 ví dụ cụ thể *(chốt trích dẫn kiểm chứng ở CP3-4)*

*(Đang chờ hoàn tất bước gắn nhãn nhóm từ `part1..4.csv`.)*

## 5. Giới hạn của data

- Nguồn review trên kho ứng dụng ở đây chỉ gồm **`1–2★`** nên thiên lệch mạnh về người dùng đang gặp bức xúc nặng; tỷ lệ % thu được **không** đại diện cho tỷ lệ lỗi trên tổng đơn hàng ngoài đời.
- Data cho biết khách hàng **gặp chuyện gì**, chưa giải thích đầy đủ hành vi xoay xở và mức sẵn sàng chi trả → kiểm chéo lại qua **khảo sát `>= 20` người** và **`>= 3` phỏng vấn** người dùng thật tại `evidence/interviews/` & `evidence/survey/`.
