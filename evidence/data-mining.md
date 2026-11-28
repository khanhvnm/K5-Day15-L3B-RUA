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

## 3. Kết quả *(tổng hợp từ `part1..4.csv` bằng `count_labels.py`)*

- **Lệnh tái lập toàn bộ bảng số:** `python evidence/scripts/count_labels.py --check --markdown` (chi tiết code tại [count_labels.py](scripts/count_labels.py)).
- **Kiểm tra mẫu `N = 300`:** `part1..4.csv` đủ `75 x 4 = 300` dòng duy nhất, không lỗi nhãn hay PII; `30` dòng trong `overlap_30_thanh.csv` chỉ dùng đo độ khớp chéo và **không** cộng vào `N = 300`.

| Đếm gì | x / N | % | Nhắc ở nhãn phụ | Tổng lần nhắc | Tổng thumbs_up | Ghi chú |
|---|---:|---:|---:|---:|---:|---|
| `cho_tai_xe` | `23/300` | `7.7%` | 22 | 45 (`15.0%`) | 49 | Nhóm giả thuyết D1 |
| `ghep_don` | `42/300` | `14.0%` | 3 | 45 (`15.0%`) | 171 | Nhóm giả thuyết D1 |
| `giao_tre` | `30/300` | `10.0%` | 56 | 86 (`28.7%`) | 107 | Nhóm giả thuyết D1 |
| `khong_huy_duoc` | `48/300` | `16.0%` | 1 | 49 (`16.3%`) | 79 | Nhóm giả thuyết D1 |
| `cskh_khong_giai_quyet` | `7/300` | `2.3%` | 20 | 27 (`9.0%`) | 20 |  |
| `hoan_tien` | `34/300` | `11.3%` | 1 | 35 (`11.7%`) | 125 |  |
| `thieu_sai_mon` | `9/300` | `3.0%` | 0 | 9 (`3.0%`) | 26 | Ngoài phạm vi tự động D1 |
| `khac` | `107/300` | `35.7%` | 22 | 129 (`43.0%`) | 453 |  |

- **Nhóm giả thuyết D1 (`cho_tai_xe + ghep_don + giao_tre + khong_huy_duoc`):** **`143/300` (`47.7%`)** — vượt ngưỡng `>= 40%` trong `evidence/hypothesis.md`.
- **Độ khớp gắn nhãn chéo (`30` dòng chung giữa Duy Thành và Khánh):** `30/30` nhãn chính (`26/30` trùng cả `ghi_chu`) — đây là **Duy Thành ↔ nhãn AI gợi ý đã được Khánh duyệt**, không phải giữa 2 người gắn tay; xem lưu ý dưới.

**Tiến độ gắn nhãn (23:25 27/11):** đủ `300/300` dòng + `30/30` dòng chung, `python evidence/scripts/sample_reviews.py --verify` khớp `seed=42` cả 5 file.

**Lưu ý trước khi báo độ khớp:**
- `part1.csv` (phần của Khánh) do **Claude Code gợi ý nhãn** theo định nghĩa + luật ưu tiên ở mục 2, Khánh duyệt lại (khai ở `docs/ai-usage.md`). Vì vậy so `overlap_30_thanh.csv` với `part1.csv` là đo **Duy Thành ↔ AI**, không phải giữa 2 người.
- Bản so thô cho `30/30` nhãn chính trùng và `26/30` dòng trùng cả `ghi_chu`; file chung được commit sau khi `part1.csv` đã lên `main` 18 phút. Duy Thành đã xác nhận gắn **không nhìn** `part1.csv` (23:40 27/11).

**Sửa sau review (23:25 27/11, nhánh `evidence/cp2-finalize`):**
- `part4.csv` thiếu 1 dòng (`review_id 15b1f12c-…`, GreenSM, so giá với Grab) làm `--verify` báo lệch seed → chèn lại đúng vị trí 40, gắn `khac` *(Claude Code gắn, Việt Anh đã xác nhận)*.
- 5 dòng đặt nhãn chính trái luật ưu tiên mục 2 → đảo lại theo luật, không đổi tập nhãn của dòng (Vũ Thành, Việt Anh đã xác nhận): `part2` #56 (`cho_tai_xe` → `khong_huy_duoc`) · `part4` #6 (`cskh_khong_giai_quyet` → `hoan_tien`) · #31 (`khong_huy_duoc` → `hoan_tien`) · #72 (`giao_tre` → `khong_huy_duoc`) · #43 chỉ sắp lại thứ tự `ghi_chu`.

### Phân bổ theo từng ứng dụng (`N = 300`)

| Ứng dụng | Số dòng | Nhóm D1 (`x/app`, `%`) | Tổng thumbs_up | Top lỗi chính |
|---|---:|---:|---:|---|
| ShopeeFood | 193 | `90/193` (`46.6%`) | 799 | `khac` (67), `ghep_don` (32), `hoan_tien` (26) |
| Grab | 53 | `33/53` (`62.3%`) | 106 | `khac` (13), `khong_huy_duoc` (12), `ghep_don` (9) |
| GreenSM | 35 | `16/35` (`45.7%`) | 96 | `khac` (18), `khong_huy_duoc` (14), `cho_tai_xe` (2) |
| be | 19 | `4/19` (`21.1%`) | 29 | `khac` (9), `hoan_tien` (4), `khong_huy_duoc` (2) |

## 4. ≥5 ví dụ cụ thể *(nguyên văn từ mẫu đã gắn nhãn, không PII)*

1. **`khong_huy_duoc`** — *"Đặt đồ ăn quán gần nhà bắt đợi cả tiếng chưa thấy báo nhận đơn. Hủy thì ko được."* (`app=ShopeeFood`, `date=2026-06-24`, `review_id=7de0494b-d6af-450b-9adf-65d5200bf448`, `thumbs_up=11`, `ghi_chu=cho_tai_xe`)
2. **`khong_huy_duoc`** — *"thời gian giao quá lâu. k tìm được tài xế 2 tiếng sau mới cho hủy."* (`app=ShopeeFood`, `date=2026-06-21`, `review_id=bdd92b1a-597f-4b8f-80b2-bda6e79c5a4b`, `thumbs_up=10`, `ghi_chu=cho_tai_xe`)
3. **`ghep_don`** — *"Giờ chế độ ghép đơn khiến thời gian giao hàng rất chậm. Gọi bữa trưa mà gần 2 tiếng đồ ăn mới đến nơi."* (`app=ShopeeFood`, `date=2026-10-21`, `review_id=2abeceb3-5d48-4690-b34d-e26d94c53bcb`, `thumbs_up=24`, `ghi_chu=giao_tre`)
4. **`cho_tai_xe`** — *"kì vl,đặt hàng từ chiều tối,xong cái app bảo ko tìm thấy tài xế, đã đói còn phải đợi, bực vl"* (`app=Grab`, `date=2026-04-30`, `review_id=7ce7616d-a90f-4282-bb71-07f3b2277b63`, `thumbs_up=6`)
5. **`giao_tre`** — *"Làm ăn chậm chạp đơn có 2km ship gần 2 tiếng,t ghi thêm.bây giờ hơn 2 tiếng r vẫn chưa thấy đâu"* (`app=ShopeeFood`, `date=2026-10-03`, `review_id=8ac0d1cf-404c-4fd5-8034-0d4794107b74`, `thumbs_up=21`)
6. **`hoan_tien`** — *"chán lắm mua deal trừ tiền không được hoàn trả r mà lại còn không có shiper giao. đặt đi đặt lại không được giao hàng."* (`app=ShopeeFood`, `date=2026-01-10`, `review_id=1a717622-3aef-427a-8464-f608e35effcd`, `thumbs_up=30`, `ghi_chu=cho_tai_xe`)
7. **`cskh_khong_giai_quyet`** — *"chăm sóc khách hàng bằng cách dùng AI phản hồi chung chung, thậm chí tài xế lấy đơn cũng không khiếu nại được"* (`app=ShopeeFood`, `date=2026-09-22`, `review_id=2343c034-a0d2-4b26-a8cd-40067cbb6950`, `thumbs_up=7`)
8. **`thieu_sai_mon`** *(ngoài phạm vi tự động D1)* — *"Quá chán, càng ngày càng tệ, giao thì toàn ghép rất lâu, còn giao thiếu đồ"* (`app=ShopeeFood`, `date=2026-06-25`, `review_id=6c06b455-a425-462e-86b8-160c977c5334`, `thumbs_up=19`, `ghi_chu=ghep_don`)

## 5. Giới hạn của data

- Nguồn review trên kho ứng dụng ở đây chỉ gồm **`1–2★`** nên thiên lệch mạnh về người dùng đang gặp bức xúc nặng; tỷ lệ % thu được **không** đại diện cho tỷ lệ lỗi trên tổng đơn hàng ngoài đời.
- Mẫu nghiêng về ShopeeFood (`193/300`) theo đúng tỷ lệ trong file gốc (`1.465/2.331`). Script không chia tầng theo app nên % gộp phản ánh chủ yếu ShopeeFood, trong khi từng app khác có cấu trúc lỗi riêng (Grab `62.3%` D1; GreenSM `40.0%` là `khong_huy_duoc` `14/35`).
- `part1.csv` (`75` dòng) do AI gợi ý và Khánh duyệt lại nên phép đo chéo `30/30` phản ánh sự thống nhất **Duy Thành ↔ AI gợi ý đã duyệt**, chưa phải 2 người gắn tay độc lập hoàn toàn. `part2.csv` (`75` dòng) cũng có nhãn nháp do Antigravity gợi ý rồi Vũ Thành sửa (`docs/ai-usage.md`) → **150/300** nhãn có AI gợi ý trước; chưa đo độ khớp người ↔ người.
- **Định nghĩa `khong_huy_duoc` gồm cả ca "đặt nhầm"** (mục 2, chốt trước khi đếm — giữ nguyên). Khoảng `13–17/48` dòng `khong_huy_duoc` chỉ là bấm nhầm / đặt nhầm muốn hủy ngay, không nhắc chờ, trễ hay tài xế, nên không phải đơn kẹt. Bỏ ra thì nhóm D1 còn khoảng `126–130/300` (`42–43%`), vẫn ≥ `40%` (cách đếm ở `summary.md` mục 5). Kiểm 6 nhãn ngẫu nhiên (seed `20261128`, review CP3-R 28/11): `6/6` đúng định nghĩa.
- `trich_dan` chỉ giữ tối đa 2 câu và 280 ký tự. `9/300` dòng bị cắt ở đúng 280 ký tự và có thể đứt giữa câu; khi cần ngữ cảnh thì tra lại theo `review_id` trong file gốc.
- Data cho biết khách hàng **gặp chuyện gì**, chưa giải thích đầy đủ tần suất gặp hàng tháng ở người dùng phổ thông → đã kiểm chéo qua **khảo sát `25` người (`n = 23` người đặt đồ ăn)** tại [results.csv](survey/results.csv); phần phỏng vấn sâu (`evidence/interviews/`) hiện vẫn chưa thực hiện (`0/3`).
