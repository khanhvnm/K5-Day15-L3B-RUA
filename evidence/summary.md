# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, hoàn thiện CP3-4 trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Hai nguồn thật đã đủ ngưỡng CP3: Đào data (`N = 300`, tái tạo bằng [count_labels.py](scripts/count_labels.py)) và Khảo sát (`n = 23` / `25` lượt gửi, tái tạo bằng [anonymize_survey.py](scripts/anonymize_survey.py)).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File & trạng thái |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | [x] (`143/300 = 47.7% >= 40%`) | [data-mining.md](data-mining.md) · [count_labels.py](scripts/count_labels.py) |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | [x] (`n = 23` ngoài nhóm có đặt đồ ăn; `20/23 = 87.0% >= 50%`) | [questions.md](survey/questions.md) · [results.csv](survey/results.csv) · [anonymize_survey.py](scripts/anonymize_survey.py) |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | [ ] *(chưa có dữ liệu)* | `evidence/interviews/` (mới có `TEMPLATE.md`, **0** phiếu `P1..P3.md`) |

## 2. Số chính

- **Đào data (`N = 300` dòng từ `part1..4.csv`, loại trừ `30` dòng `overlap_30_thanh.csv`):**
  - Nhóm giả thuyết D1 (`cho_tai_xe + ghep_don + giao_tre + khong_huy_duoc`): **`143/300` (`47.7%`)** — chi tiết nhãn chính: `khong_huy_duoc: 48/300` (`16.0%`), `ghep_don: 42/300` (`14.0%`, `171` `thumbs_up`), `giao_tre: 30/300` (`10.0%`, thêm `56` lần ở nhãn phụ → `86/300 = 28.7%` tổng lần nhắc), `cho_tai_xe: 23/300` (`7.7%`, thêm `22` lần ở nhãn phụ → `45/300 = 15.0%`).
  - Nhóm tài chính & CSKH đi kèm: `hoan_tien: 34/300` (`11.3%`, `125` `thumbs_up`); `cskh_khong_giai_quyet: 7/300` (`2.3%` nhãn chính + `20` lần ở nhãn phụ → `27/300 = 9.0%` tổng lần nhắc).
  - Ngoài phạm vi / khác: `thieu_sai_mon: 9/300` (`3.0%` — chuyển nhân viên), `khac: 107/300` (`35.7%`).
  - Theo app: **Grab `33/53` (`62.3%`)** · **ShopeeFood `90/193` (`46.6%`)** · **GreenSM `16/35` (`45.7%`)** · **be `4/19` (`21.1%`)**.
  - Độ khớp gắn nhãn chéo (`overlap_30_thanh.csv` vs `part1.csv`): **`30/30` nhãn chính (`100.0%`), `26/30` trùng cả `ghi_chu`** *(lưu ý: `part1.csv` do AI gợi ý và Khánh duyệt, nên đây là độ khớp Duy Thành ↔ AI đã duyệt)*.
- **Khảo sát (`results.csv`, `25` người trả lời — cả 4 thành viên nhóm RUA đã xác nhận không điền form):**
  - Mẫu số người có đặt đồ ăn 1 tháng qua: **`n = 23 / 25`** (`11` học viên L3B, `6` học viên L3A, `6` bạn bè ngoài lớp).
  - **Số chính 1 — Từng gặp `>= 1` lần giao muộn `>= 15'` trong 1 tháng qua:** **`20/23` (`87.0%`)** (`8` người `1 lần`, `11` người `2–3 lần`, `1` người `4–5 lần`, `3` người `0 lần`).
  - **Tình trạng & mức độ trễ (trong `20` người gặp trễ):** `14/20` (`70.0%`) báo tài xế đã nhận nhưng giao rất chậm (nghi ghép đơn), `4/20` (`20.0%`) chưa có tài xế (`3` đang tìm tài xế + `1` trời mưa không thấy tài xế), `2/20` không rõ; mức trễ `15–30'` (`11/20 = 55.0%`), **`30–60'` (`8/20 = 40.0%`)**, không nhớ (`1/20`).
  - **Số chính 2 — Kết quả cuối & thời gian xử lý (`n = 20`):** **`10/20` (`50.0%`) hoàn toàn không giải quyết được** (`7/20` *"Không huỷ được, vẫn phải nhận đơn"* + `3/20` *"Không ai giải quyết"*); `3/20` hủy được nhưng hoàn chậm/thiếu; chỉ `3/20` hủy hoàn đủ tiền và `2/20` được bù voucher; `2/20` ghi tay *"Nhận đơn"* / *"Vẫn nhận đồ nhưng muộn"*. Trong `12/20` người có liên hệ/xử lý (`8/20` không liên hệ): `2/20` mất `< 5'`, `6/20` mất `5–15'`, `2/20` mất `15–30'`, `2/20` mất `> 30'`.
  - **Giá trị đơn (`n = 23`) & hậu quả (`n = 20`):** `22/23` (`95.7%`) đơn phổ thông dưới `200.000đ` (`Dưới 50k`: 3, `50–100k`: 13, `100–200k`: 6, `Trên 200k`: 1); **`12/20` (`60.0%`) giảm dùng (`9/20`) hoặc chuyển sang app khác (`3/20`)** sau sự cố.
- **Phỏng vấn:** *Chưa thực hiện (`0/3` phiếu `P1..P3.md` — không bịa số).*

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | *(chưa phỏng vấn)* | | | | |
| P2 | *(chưa phỏng vấn)* | | | | |
| P3 | *(chưa phỏng vấn)* | | | | |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, không PII)

1. **`khong_huy_duoc`** — *"Đặt đồ ăn quán gần nhà bắt đợi cả tiếng chưa thấy báo nhận đơn. Hủy thì ko được."* — `ShopeeFood`, `2026-06-24`, `review_id=7de0494b-d6af-450b-9adf-65d5200bf448`, `thumbs_up=11`
2. **`ghep_don`** — *"Giờ chế độ ghép đơn khiến thời gian giao hàng rất chậm. Gọi bữa trưa mà gần 2 tiếng đồ ăn mới đến nơi."* — `ShopeeFood`, `2026-10-21`, `review_id=2abeceb3-5d48-4690-b34d-e26d94c53bcb`, `thumbs_up=24`
3. **`cho_tai_xe`** — *"kì vl,đặt hàng từ chiều tối,xong cái app bảo ko tìm thấy tài xế, đã đói còn phải đợi, bực vl"* — `Grab`, `2026-04-30`, `review_id=7ce7616d-a90f-4282-bb71-07f3b2277b63`, `thumbs_up=6`
4. **`hoan_tien`** — *"chán lắm mua deal trừ tiền không được hoàn trả r mà lại còn không có shiper giao. đặt đi đặt lại không được giao hàng."* — `ShopeeFood`, `2026-01-10`, `review_id=1a717622-3aef-427a-8464-f608e35effcd`, `thumbs_up=30`
5. **`cskh_khong_giai_quyet`** — *"chăm sóc khách hàng bằng cách dùng AI phản hồi chung chung, thậm chí tài xế lấy đơn cũng không khiếu nại được"* — `ShopeeFood`, `2026-09-22`, `review_id=2343c034-a0d2-4b26-a8cd-40067cbb6950`, `thumbs_up=7`
6. **Khảo sát câu 15** — *"Thà tự đi mua về ăn còn hơn"* — phiếu `stt=7` (`Học viên L3A`, `results.csv`)
7. **Khảo sát câu 15** — *"không huỷ được đơn, tổng đài sử lý quá lâu"* — phiếu `stt=17` (`Học viên L3A`, `results.csv`)
8. **Khảo sát câu 15** — *"nhà ở khu xa , vắng người ship lâu và ít người ship"* — phiếu `stt=5` (`Học viên L3B`, `results.csv`)

## 4. Các nguồn có khớp nhau không

- **Hai nguồn khớp nhau rất mạnh về nguyên nhân lẫn hệ quả:**
  - **Về nguyên nhân gốc:** Nguồn review `1–2★` cho thấy **`47.7%` (`143/300`)** rơi vào 4 lỗi D1 (nổi bật `khong_huy_duoc: 16.0%` và `ghep_don: 14.0%`, `28.7%` tổng lần nhắc trễ); nguồn khảo sát ngoài đời thực (`n = 23`) cũng xác nhận **`70.0%` (`14/20`)** đơn trễ rơi vào trạng thái nghi ghép đơn, `20.0%` (`4/20`) do chưa có tài xế, và **`50.0%` (`10/20`)** kết thúc trong trạng thái bị khóa hủy hoặc không ai giải quyết.
  - **Khác biệt mức độ do đặc thù mẫu (đã dự báo từ CP2):** Review trên kho ứng dụng chỉ chọn mức `1–2★` nên thời gian chờ cực đoan (thường `60–120` phút), trong khi ở người dùng phổ thông trong khảo sát (`87.0%` từng gặp trễ `>= 15'`/tháng), mức trễ phổ biến là `15–30'` (`55.0%`) và `30–60'` (`40.0%`), và phần lớn đơn dưới `200k` (`22/23 = 95.7%`). Điều này trực tiếp kiểm chứng **tính hợp lý của 3 ngưỡng policy trong `data/policy.json`**: không chi bù tràn lan dưới `30'`, cấp `VOUCHER <= 30.000đ` ở vùng `30–60'`, và trần tự động hoàn `300.000đ` phủ hầu hết đơn bữa ăn thường (`>= 95%`).
  - **Tác động kinh doanh:** `12/20` (`60.0%`) người gặp trễ trong khảo sát cho biết **dùng ít hơn (`9/20`) hoặc chuyển app khác (`3/20`)** — khớp với phàn nàn bỏ app xuất hiện lặp lại trong tập review.

## 5. Kết luận

- **Giả thuyết ở [hypothesis.md](hypothesis.md) (giữ nguyên không sửa):** **ĐÚNG và vượt ngưỡng ở cả 2 nguồn đã thu thập:**
  - **Nguồn 1 (Đào data):** `143/300` (**`47.7%` `>= 40%`**) thuộc nhóm kẹt tài xế / ghép đơn / giao trễ / không hủy được.
  - **Nguồn 2 (Khảo sát):** `20/23` (**`87.0%` `>= 50%`**) người đặt đồ ăn gặp ít nhất 1 lần đơn trễ `>= 15'` trong 1 tháng qua, với `60.0%` giảm dùng hoặc chuyển app sau sự cố.
- **Kiểm độ nhạy của con số `47.7%`** (review CP3-R, 28/11): định nghĩa `khong_huy_duoc` ở `data-mining.md` mục 2 có cả ca *"đặt nhầm"*, và khoảng **13–17 / 48** review `khong_huy_duoc` chỉ nói *bấm nhầm / đặt nhầm, muốn hủy ngay* mà không nhắc chờ, trễ hay tài xế. Đó không phải đơn kẹt (agent xử lý ca này bằng `CHUYEN_NV`, xem câu thử B30). Bỏ các ca này ra thì nhóm D1 còn khoảng **`126–130/300` (`42–43%`)**, **vẫn ≥ `40%`**. Kết luận không đổi, nhưng khi trình bày nên nói *"khoảng 42–48%"*. *(Cách đếm: lọc `nhan=khong_huy_duoc` không có `cho_tai_xe/ghep_don/giao_tre` trong `ghi_chu` và trích dẫn không có từ chờ/lâu/trễ/tài xế/ship → 17 dòng, đọc tay thì 13 dòng rõ ràng là đặt nhầm.)*
- **Nhãn có AI hỗ trợ:** theo `docs/ai-usage.md`, ngoài `part1` (75 dòng, Claude Code gợi ý, Khánh duyệt) thì `part2` (75 dòng) cũng do Antigravity gợi ý nhãn nháp rồi Vũ Thành sửa. Như vậy **150/300** nhãn có AI gợi ý trước, chỉ `part3–4` do người gắn từ đầu.
- **Điều vẫn chưa biết:** Nhóm chưa có phỏng vấn sâu (`0/3` file `P*.md` trong `evidence/interviews/`), và câu hỏi khảo sát gộp mức độ trễ ảnh hưởng bữa ăn vào cùng câu tần suất `>= 15'` (`17/20` người gặp trễ ghi nhận bị nguội đồ, bỏ bữa/ăn muộn hoặc trễ việc/học; `3/20` *"Không bị ảnh hưởng gì nhiều"* → tỷ lệ ảnh hưởng thực chất là **`17/23 = 73.9%`** vẫn vượt ngưỡng `50%`).

## 6. Số liệu Pain & Impact gửi đội trưởng cho `spec.md` §1–§2 và Slide

- **Thừa số cho công thức Impact (`spec.md` §2 = `số người × số lần/tháng × phút mất`):**
  - **Quy mô người dùng công khai** *(đối chiếu lại nguyên văn 2 bài ngày 28/11/2026 — bản trước ghi sai số của bài VnExpress)*:
    - CafeBiz (đăng 20/05/2025): *"ứng dụng này hiện là kênh tiếp cận hơn 10 triệu người dùng"* — đây là **tổng người dùng cả app be** (gọi xe + giao đồ ăn + dịch vụ khác), **không** phải số người dùng beFood, và bài không ghi số này tính tại thời điểm nào (`https://cafebiz.vn/be-group-tang-toc-nguoi-dung-tang-50-gmv-tang-60-pha-hoi-nong-vao-grab-va-xanh-sm-176250520162320667.chn`).
    - VnExpress (đăng 09/07/2025): theo NielsenIQ (khảo sát tháng 4/2025, tính theo **số đơn** trong 7 ngày) *"ShopeeFood và GrabFood chiếm thị phần lớn nhất, lần lượt đạt 56% và 36%"*, beFood đứng thứ ba; Statista ước thị trường giao đồ ăn VN *"gần 2,8 tỷ USD năm nay"* (2025). Bài **không** có số 2,1 tỷ USD, cũng không có tỷ lệ 48%/48%, và không nêu số người dùng giao đồ ăn (`https://vnexpress.net/shopeefood-grabfood-nam-hon-90-thi-truong-giao-do-an-4911752.html`).
    - ⇒ **Chưa có số công khai về số người dùng app giao đồ ăn.** Ở `spec.md` §2, dùng "hơn 10 triệu" làm cận trên của **người dùng be** thì phải ghi rõ đó là người dùng cả app; muốn dùng làm số người dùng giao đồ ăn thì ghi *(tự ước tính)*.
  - **Tỷ lệ người gặp & tần suất/tháng (từ `evidence/survey/results.csv`, `n = 23`):** `20/23` (`87.0%`) gặp `>= 1` lần trễ `>= 15'`/tháng (`8` người `1 lần`, `11` người `2–3 lần`, `1` người `4–5 lần` → bình quân nhóm gặp trễ khoảng `~2.0` lần/tháng *(ước lượng từ trung điểm khoảng câu 6)*, toàn mẫu `~1.7` lần/tháng).
  - **Thời gian mất vì sự cố (từ khảo sát `n = 20`):** `11/20` trễ `15–30'`, `8/20` trễ `30–60'` (trung bình ước lượng `~28–30` phút chờ trễ/ca) + `10/20` mất thêm `5–30+` phút để liên hệ CSKH/tự xử lý (`6/20` mất `5–15'`, `2/20` mất `15–30'`, `2/20` mất `>30'`).
  - **Liên kết chi phí:** Sẵn sàng đồng bộ 3 nhóm tần suất trễ từ câu 6 khảo sát (`0–1` lần: `11/23`, `2–3` lần: `11/23`, `4–5` lần: `1/23`) vào [cost/personas.yaml](../cost/personas.yaml) ở PR chi phí riêng (để tránh xung đột với nhánh nối model).
