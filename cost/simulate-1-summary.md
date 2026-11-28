# Tóm tắt mô phỏng simulate-1@20261128-085957

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it_tre_it | 24 | 2 | 3269 | 229 | 2.0 | 8.2 |
| dung_vua_tre_vua | 24 | 3 | 4916 | 342 | 3.0 | 11.9 |
| dung_nhieu_khieu_nai_cao | 2 | 4 | 5908 | 415 | 3.5 | 14.5 |

Tỉ lệ đạt dùng để tính: 30/30 (100%) — lượt run-2@20261128-084938

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (300.000 người) | Chi phí / tháng — cơ sở (1.000.000 người) | Chi phí / tháng — cao (10.000.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini (vào 0.15 · ra 0.6 $/1M) | $0.00080 (≈ 21 ₫) | $0.00080 (≈ 21 ₫) | $0.00031 (≈ 8 ₫) | $466.67 (≈ 12.138.214 ₫) | $1,555.58 (≈ 40.460.715 ₫) | $15,555.83 (≈ 404.607.149 ₫) | $0.0016 (≈ 40 ₫) |
| gpt-4o (vào 2.5 · ra 10.0 $/1M) | $0.0133 (≈ 346 ₫) | $0.0133 (≈ 346 ₫) | $0.0052 (≈ 135 ₫) | $7,777.92 (≈ 202.303.574 ₫) | $25,926.38 (≈ 674.345.248 ₫) | $259,263.84 (≈ 6.743.452.478 ₫) | $0.0259 (≈ 674 ₫) |
| gemini-2.5-flash-lite (vào 0.1 · ra 0.4 $/1M) | $0.00053 (≈ 14 ₫) | $0.00053 (≈ 14 ₫) | $0.00021 (≈ 5 ₫) | $311.12 (≈ 8.092.143 ₫) | $1,037.06 (≈ 26.973.810 ₫) | $10,370.55 (≈ 269.738.099 ₫) | $0.0010 (≈ 27 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.6) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-4o-mini. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
- Tỷ giá: 1 USD = 26.010 ₫ (Vietcombank niêm yết chiều bán ra ngày 27/11/2026 (https://www.vietcombank.com.vn)).
