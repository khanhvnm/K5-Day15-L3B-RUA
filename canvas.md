# Canvas — RUA · Track D

> Điền ở guide bước 1.4. CP1 17:00 Thứ Sáu 27/11: nộp bản đầu, đủ 7 dòng (dòng 4 được ghi giả thuyết + nguồn sẽ kiểm).
> CP2 19:30 Thứ Sáu 27/11: cập nhật (số bằng chứng đầu, lát cắt đã chốt) và điền dòng "Đã đổi gì so với CP1".
> Track F: chép thêm thẻ đề của nhóm (khung trong file track F) xuống dưới bảng này.

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track + lát cắt dự kiến | D (D1) · Xử lý khiếu nại đơn giao đồ ăn bị trễ / kẹt quá giờ dự kiến |
| 2 | Người dùng chính | Khách đặt đồ ăn qua app |
| 3 | Pain | Người đặt đồ ăn qua app phải chờ hàng giờ vì chưa có tài xế nhận hoặc đơn bị ghép, nhưng không được hủy đơn và trợ lý trong app không giải quyết được; nên mất bữa ăn, mất tiền và bỏ app |
| 4 | Bằng chứng đầu — CP1: giả thuyết + nguồn sẽ kiểm · CP2: số đầu tiên + 1 trích dẫn | **Số đầu (CP2):** 100/300 review 1–2★ (33,3%) trong mẫu ngẫu nhiên `seed=42` trên 4 app (ShopeeFood 193 · Grab 53 · GreenSM 35 · be 19) có cờ từ khóa giao trễ hoặc ghép đơn — cờ có sẵn trong file review gốc, **chưa gắn nhãn tay** (`evidence/data-mining.md`). **Trích dẫn:** *"Giờ chế độ ghép đơn khiến thời gian giao hàng rất chậm. Gọi bữa trưa mà gần 2 tiếng đồ ăn mới đến nơi."* — review ShopeeFood 1★, 21/10/2026, 24 lượt hữu ích (`2abeceb3-5d48-4690-b34d-e26d94c53bcb`). Đang làm: gắn nhãn tay 300 dòng theo 8 nhãn đã chốt + khảo sát ≥20 người |
| 5 | **Lát cắt MỘT CÂU** (1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả) | Một khách đặt đồ ăn · Đơn bị kẹt quá giờ dự kiến (chưa có tài xế nhận hoặc đang bị ghép đơn) · AI quyết định: cho hủy và hoàn tiền / bù voucher và tiếp tục chờ / hỏi lại mã đơn / từ chối khi chưa đủ ngưỡng / chuyển nhân viên · Khách biết ngay tình trạng đơn và được xử lý trong hạn mức chính sách, kèm lý do bằng số |
| 6 | AI tự làm đến đâu + 1 dòng lý do: sai thì ai chịu gì | AI tự quyết hủy+hoàn và voucher **chỉ trong hạn mức** (code `check_limit` kiểm số tiền); vượt hạn mức, quán đã làm món, ngoài phạm vi (thiếu/sai món, đồ hỏng, an toàn thực phẩm) → chuyển nhân viên. Lý do: hoàn sai thì quán/app mất tiền, từ chối sai thì khách mất tiền và niềm tin - nên tiền chỉ ra khi code xác nhận |
| 7 | Phân công có tên | Dữ liệu giả + bằng chứng + chi phí: Phạm Duy Thành · Bộ câu thử + eval: Đỗ Việt Anh · Code agent + nối model: Vũ Thành · Điều phối + review sản phẩm + spec + slide: Vũ Nam Khánh |
| — | *(CP2)* Đã đổi gì so với CP1 | (1) Lát cắt thêm 2 quyết định `HOI_LAI` (thiếu mã đơn) và `TU_CHOI` (chưa đủ ngưỡng / tấn công) — tổng 5 quyết định. (2) Chính sách chốt thành `data/policy.json` 1.1: ngưỡng 20/30/60 phút, trần 30.000đ / 300.000đ *(tự ước tính)*; tiền do code `check_limit` quyết, AI chỉ phân loại. (3) Bằng chứng đổi từ ước lượng từ khóa ~48% trên riêng ShopeeFood (CP1) sang mẫu 300 review trên 4 app: số tạm 33,3% theo cờ từ khóa, đang gắn nhãn tay |
