# Đào data — cách đếm và kết quả

> Điền phần 1 và phần 2 **TRƯỚC khi đếm** (CP2-5). Phần 3–5 sẽ cập nhật tại CP3-4 sau khi cả 4 thành viên gắn nhãn xong `part1.csv .. part4.csv` và kiểm độ khớp 30 dòng chung.

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** Tập review công khai 4 app giao đồ ăn (`ShopeeFood: 1.465`, `Grab: 452`, `GreenSM: 245`, `be: 169` — tổng `2.331` dòng mức `1–2★`, ngày review từ `01/01/2026` đến `26/11/2026`), file thô để tại `docs/no_commit/reviews_food_2026.csv` *(không commit lên GitHub)*.
- **Không lọc theo cột `is_food` của file gốc:** ShopeeFood là app chỉ giao đồ ăn, nhưng `951/1.465` review ShopeeFood bị gắn `is_food=False`, kể cả review rõ ràng về giao đồ ăn (vd *"ghép đơn giao lâu vl"*). Vì vậy cờ này không đáng tin. Với Grab, GreenSM và be, file gốc chỉ giữ dòng `is_food=True`, nên mẫu không lẫn review gọi xe.
- **Đếm gì · trên tập nào · lọc gì:** Lấy ngẫu nhiên **300 review** bằng `seed = 42` trên **toàn bộ 4 app** (`1–2★`, độ dài `>= 8` ký tự; cơ cấu mẫu thu được: `ShopeeFood: 193`, `Grab: 53`, `GreenSM: 35`, `be: 19` — khớp phần *"Nguồn sẽ kiểm"* trong `canvas.md` và CP2-5 trong `docs/plan.md`, phân biệt với ước lượng thô CP1 trên `1.465` review ShopeeFood), gắn **1 nhãn chính (`nhan`)** mô tả nguyên nhân bức xúc cốt lõi nhất (hoặc ghi nhãn phụ vào `ghi_chu`), sau đó tính `x / 300 (%)` và tổng `thumbs_up` theo từng nhãn. Chia 4 phần bằng nhau cho 4 thành viên (`part1..4.csv`, mỗi người `75` dòng) + `overlap_30_thanh.csv` (`30` dòng từ `part1` để Duy Thành và Khánh gắn chéo kiểm độ khớp).
- **Mẫu số là gì:** **`N = 300`** review trong mẫu ngẫu nhiên đã trích (bao gồm cả review không liên quan đơn kẹt/trễ như `thieu_sai_mon` hoặc `khac` để không làm méo mẫu số).
- **Script / công thức:** [sample_reviews.py](scripts/sample_reviews.py) (`seed = 42`). Kiểm tái lập: `python evidence/scripts/sample_reviews.py --verify`. Script không ghi đè file part đã có nhãn. Script gộp & đếm `x/300` sẽ hoàn thiện tại nhánh CP3-4 sau khi đủ 4 file part.

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

**Luật chọn nhãn chính khi một review khớp nhiều nhãn** *(chốt trước khi gắn, không đổi sau khi đếm)*: lấy nhãn **đứng trước** theo thứ tự dưới đây làm `nhan`, các nhãn còn lại ghi vào `ghi_chu`, cách nhau bằng dấu `;`.

`thieu_sai_mon` › `hoan_tien` › `khong_huy_duoc` › `cho_tai_xe` › `ghep_don` › `giao_tre` › `cskh_khong_giai_quyet` › `khac`

Lý do xếp thứ tự: nhãn cụ thể hơn đứng trước nhãn chung (`giao_tre`, `khac`). `cskh_khong_giai_quyet` thường là hệ quả của một lỗi khác nên chỉ làm nhãn chính khi review không nêu lỗi gốc nào.

**Ca mập mờ đã gặp khi đọc trước mẫu:**

| Review nói | Gắn `nhan` |
|---|---|
| Đợi lâu, không có tài xế, không hủy được (*"đợi lâu, thường kco tài xế và k thể hủy đơn"*) | `khong_huy_duoc` · `ghi_chu`: `cho_tai_xe;giao_tre` |
| Tài xế nhận đơn rồi bỏ / không giao, phải chờ tài xế khác | `cho_tai_xe` |
| Bị trừ tiền mà chưa đặt được đơn, hoặc hủy rồi chưa được hoàn | `hoan_tien` |
| Chỉ than "chậm quá / lâu quá", không nói vì sao | `giao_tre` |
| Chỉ chửi chatbot/tổng đài, không nêu lỗi đơn | `cskh_khong_giai_quyet` |
| Chửi chung chung, không rõ lỗi, hoặc nội dung vô nghĩa | `khac` |

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

- Độ khớp gắn nhãn chéo (`30` dòng chung giữa Duy Thành và Khánh): `30/30` nhãn chính (`26/30` trùng cả `ghi_chu`) — đây là **Duy Thành ↔ nhãn AI gợi ý đã được Khánh duyệt**, không phải giữa 2 người gắn tay; xem lưu ý dưới.

**Tiến độ gắn nhãn (23:25 27/11):** đủ `300/300` dòng + `30/30` dòng chung, `python evidence/scripts/sample_reviews.py --verify` khớp `seed=42` cả 5 file.

**Lưu ý trước khi báo độ khớp:**
- `part1.csv` (phần của Khánh) do **Claude Code gợi ý nhãn** theo định nghĩa + luật ưu tiên ở mục 2, Khánh duyệt lại (khai ở `docs/ai-usage.md`). Vì vậy so `overlap_30_thanh.csv` với `part1.csv` là đo **Duy Thành ↔ AI**, không phải giữa 2 người.
- Bản so thô cho `30/30` nhãn chính trùng và `26/30` dòng trùng cả `ghi_chu`; file chung được commit sau khi `part1.csv` đã lên `main` 18 phút. Duy Thành đã xác nhận gắn **không nhìn** `part1.csv` (23:40 27/11).

**Sửa sau review (23:25 27/11, nhánh `evidence/cp2-finalize`):**
- `part4.csv` thiếu 1 dòng (`review_id 15b1f12c-…`, GreenSM, so giá với Grab) làm `--verify` báo lệch seed → chèn lại đúng vị trí 40, gắn `khac` *(Claude Code gắn, Việt Anh đã xác nhận)*.
- 5 dòng đặt nhãn chính trái luật ưu tiên mục 2 → đảo lại theo luật, không đổi tập nhãn của dòng (Vũ Thành, Việt Anh đã xác nhận): `part2` #56 (`cho_tai_xe` → `khong_huy_duoc`) · `part4` #6 (`cskh_khong_giai_quyet` → `hoan_tien`) · #31 (`khong_huy_duoc` → `hoan_tien`) · #72 (`giao_tre` → `khong_huy_duoc`) · #43 chỉ sắp lại thứ tự `ghi_chu`.

## 4. ≥5 ví dụ cụ thể *(chốt trích dẫn kiểm chứng ở CP3-4)*

*(Đang chờ hoàn tất bước gắn nhãn nhóm từ `part1..4.csv`.)*

## 5. Giới hạn của data

- Nguồn review trên kho ứng dụng ở đây chỉ gồm **`1–2★`** nên thiên lệch mạnh về người dùng đang gặp bức xúc nặng; tỷ lệ % thu được **không** đại diện cho tỷ lệ lỗi trên tổng đơn hàng ngoài đời.
- Mẫu nghiêng về ShopeeFood (`193/300`) theo đúng tỷ lệ trong file gốc (`1.465/2.331`). Script không chia tầng theo app nên % gộp phản ánh chủ yếu ShopeeFood.
- `trich_dan` chỉ giữ tối đa 2 câu và 280 ký tự. `9/300` dòng bị cắt ở đúng 280 ký tự và có thể đứt giữa câu; khi cần ngữ cảnh thì tra lại theo `review_id` trong file gốc.
- Data cho biết khách hàng **gặp chuyện gì**, chưa giải thích đầy đủ hành vi xoay xở và mức sẵn sàng chi trả → kiểm chéo lại qua **khảo sát `>= 20` người** và **`>= 3` phỏng vấn** người dùng thật tại `evidence/interviews/` & `evidence/survey/`.
