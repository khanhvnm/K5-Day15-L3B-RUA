# AI SPEC — [Tên lát cắt] · Nhóm [tên nhóm] · Phòng [XXX] · Zone [X]

> Mốc nộp: §7 chốt chuẩn "đạt" tại **CP2 19:30 Thứ Sáu 27/11** · §0–§7 nộp **CP3 10:00 Thứ Bảy 28/11** · đủ §0–§10 **CP4 14:30 Thứ Bảy 28/11** · §10 changelog ghi tiếp đến **23:59 Thứ Bảy 28/11**.
> Đầu mỗi mục ghi bước guide (`02-guide.md` trong repo đề) chỉ cách điền. Mỗi mục ngắn, có số và nguồn; chi tiết để ở file được trỏ tới. Xoá dòng hướng dẫn trong ngoặc vuông khi điền xong.

Track: [ ] A · [ ] B · [ ] C · [ ] D · [ ] E — bài toán: [đề gợi ý trong file track, hoặc bài toán nhóm tự mở rộng] __
Data BTC cấp đã dùng (nếu có — không commit nguyên file): __

## §0. Hiện tại việc này diễn ra thế nào *(guide 1.1)*
- Luồng hiện tại của việc này, trong khoá hoặc trên app thật (3–5 bước; ảnh chụp từ tài khoản của mình, đã che thông tin):
- Công cụ / AI đang được dùng cho việc này (nếu có) + nguồn. Không kiểm được thì ghi "chưa kiểm":

## §1. Người dùng & bằng chứng *(guide 1.1, 1.2)*
- Người dùng chính (một vai cụ thể):
- Việc họ cố làm xong (`động từ + đối tượng + bối cảnh`, không có chữ AI):
- Hôm nay họ giải bằng gì, hỏng ở đâu, vì sao chưa bỏ:
- Pain (KHÔNG chữ AI): ai — đang làm gì — vướng đâu — hậu quả gì:
- Bằng chứng — số chính + kết luận (chi tiết: `evidence/summary.md`): __

## §2. Impact & quyết định chọn *(guide 1.3)*

| Hướng | Bao nhiêu người gặp | Bao nhiêu lần / tháng | Mỗi lần tốn gì | Impact / tháng | Làm kịp không | Chọn? |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

- **Impact / tháng** của hướng chọn = __ người × __ lần × __ phút = __ — nguồn từng thừa số: __ (không có nguồn thì ghi rõ *(tự ước tính)*)
- Hướng ĐÃ LOẠI + vì sao (giữ lại, đừng xoá):
- Số lần / tháng của từng kiểu người dùng (dùng cho persona ở §8):

## §3. Giải pháp tương tự *(guide 2.1)*
- [sản phẩm / tính năng gần giống]: một điều đáng học · một điều đáng né · mình khác gì

## §4. Thiết kế *(guide 2.2, 3.2)*
- **Lát cắt MỘT CÂU** (1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả):
- Không làm (≥3 điều):
- **Sơ đồ** (ảnh / Mermaid / draw.io): [chèn ở đây]
- **Hình dạng:** [ ] workflow cố định · [ ] một agent · [ ] nhiều agent — 2 dòng lý do, và vì sao **không** chọn hình dạng phức tạp hơn:
- **AI dựa vào đâu** — mỗi công cụ (khớp `codebase/tools.py`):

  | Công cụ | Input | Output | Tác động ra ngoài? |
  |---|---|---|---|
  | `get_order` | `order_id` (chấp nhận `DH003`, `dh3`, `#DH-003`, `ĐH003`) | Dict đơn từ `data/orders.json` + `found`, `phut_tu_luc_dat`, `phut_tre_so_voi_eta` (tính bằng code từ `placed_at`/`eta`/`now`), `trang_thai_hop_le` (theo `valid_status_combos`); không có đơn → `{"found": false}` | Không (chỉ đọc) |
  | `get_policy` | `issue_type` (`"all"` hoặc tên 1 rule) | `global_caps`, `valid_status_combos`, `rules` từ `data/policy.json`; không thấy rule → `{"found": false}` | Không (chỉ đọc) |
  | `get_complaint_history` | `user_id` | `{"user_id", "so_lan_thang_nay"}` từ `data/complaint_history.json` | Không (chỉ đọc) |
  | `check_limit` | `issue_type`, `amount`, `order` (từ `get_order`), `complaints_in_month`, `request_type` (`HUY_DON` / `KHIEU_NAI_TRE`) | `{"ok", "expected_decision", "max", "rule_id", "ly_do"}` — quyết định + số tiền đúng `amount_formula` (HUY_HOAN = total ≤ 300k · VOUCHER = min(30k, total)); **code thuần, không gọi AI** | Không (tính toán thuần) |
  | `escalate_to_human` | `case_id` (mã đơn hoặc nhãn như `ATTP`), `reason` | `{"ma_ca": "CS-<tham chiếu>-<NNN>", "tham_chieu", "trang_thai": "ban_nhap_cho_duyet", "ly_do"}` | Không gửi đi đâu — chỉ thêm bản nháp vào hàng chờ `DRAFT_CASES` (bộ nhớ) + trace, chờ nhân viên duyệt |

- **Mức tự động:** [ ] AI gợi ý, người quyết · [ ] AI tự làm khi chắc, chuyển người khi không · [ ] AI tự làm — lý do (sai thì ai chịu gì, sửa đắt hay rẻ):
- **Chỗ chặn rủi ro** (rủi ro lớn nhất của lát cắt bị chặn ở đâu, bằng gì):
- **Chỗ người duyệt** (việc AI không được tự làm):
- **Nguyên tắc thiết kế** (≥3, bắt buộc G10):

  | Nguyên tắc | Chỗ cụ thể trên sơ đồ / trong bản chạy thử |
  |---|---|
  | G10 — thu hẹp phạm vi khi không chắc |  |
  |  |  |
  |  |  |

- Phần nào còn giả (công cụ trả dữ liệu giả, model chế độ giả…) — ghi rõ, không giả làm thật:
  - **Dữ liệu:** cả 3 công cụ tra cứu đọc dữ liệu `synthetic` do nhóm tự dựng (30 đơn, 13 rule, 18 user — `data/DATA_CARD.md`), không nối hệ thống đơn hàng thật nào. Giờ "hiện tại" là trường `now` cố định trong từng đơn, không phải đồng hồ hệ thống.
  - **Model:** mặc định chạy chế độ giả (`MODEL_PROVIDER` trống → `call_model` trả câu cố định, 0 token) → agent không parse được JSON → luôn ra `CHUYEN_NV`. Nhánh gọi OpenAI trong `codebase/ai.py` đã viết nhưng **chưa có lượt chạy thật nào** trong repo (chưa có `traces/`, `eval/run-N.csv`).
  - **Hoàn tiền / voucher:** `HUY_HOAN` và `VOUCHER` chỉ là quyết định + số tiền trên dòng output, không gọi cổng thanh toán hay hệ thống voucher nào; câu trả lời cho khách ghi rõ là "phiếu đề xuất nháp chờ xác nhận".
  - **Chuyển nhân viên:** `escalate_to_human` chỉ tạo bản nháp trong bộ nhớ của tiến trình (mất khi tắt chương trình), không gửi tới hệ thống CSKH hay ticket thật.
  - **Bồi thường trùng:** chỉ chặn được qua `status = cancelled` (DH022); data không có lịch sử bồi thường theo đơn nên chưa kiểm được bồi thường lặp trên đơn chưa huỷ.

## §5. Chỗ khó — 4 lớp + ≥6 kịch bản + 2 tấn công *(guide 2.3)*

| Kịch bản | Lớp (1–4) | Hành vi mong muốn (nói gì, hiện gì, cho làm gì tiếp) | Câu thử |
|---|---|---|---|
|  |  |  |  |
| *(tấn công)* |  |  |  |
| *(tấn công)* |  |  |  |

(1) nguồn sự thật · (2) mơ hồ / thiếu thông tin · (3) ngoài phạm vi / thẩm quyền · (4) đặc thù lĩnh vực (sai thì người dùng mất gì đắt nhất)

## §6. Bốn đường đi của trải nghiệm
- Mọi thứ suôn sẻ: · Không chắc (lớp 2): · Không có căn cứ (lớp 1): · Người dùng sửa:
- Bị đòi ngoài phạm vi (lớp 3): · Trường hợp đặc thù lĩnh vực (lớp 4):

## §7. Đánh giá & chuẩn "đạt" *(guide 2.4, 4.1)*
- Data card: `data/DATA_CARD.md` · bộ câu thử: `eval/benchmark.csv` — 20 câu (thuong 7 · kho 9 · tu_choi 4; từ data thật 8/20) · metric: `eval/metric_spec.yaml` (3 metric: `khong_vuot_han_muc` 100% · `quyet_dinh_dung` ≥ 80% · `chuyen_nguoi_dung_luc` 100% câu tu_choi + ≥ 90% câu CHUYEN_NV)
- **Chuẩn "đạt"** (chốt **trước 19:30 Thứ Sáu 27/11**, giữ nguyên đến 23:59 Thứ Bảy 28/11): "Đạt khi ≥ 80% câu qua, **và** 100% câu không vượt hạn mức, **và** 100% câu `tu_choi` qua."
- Kết quả: lượt 1 __/__ (__%) · lượt 2 __/__ (__%) — run ID: __ / __ → chi tiết `eval/report.md`, hồ sơ `eval/README.md`

## §8. Chi phí khi dùng thật *(guide 4.2)*
- Persona + giá: `cost/personas.yaml` · lượt mô phỏng: `cost/simulate-__.csv` (__ phiên)
- Chi phí / task thành công: __ (model __) · __ (model __)
- Chi phí / tháng ở quy mô thật: thấp __ · cơ sở __ · cao __ → chi tiết `cost/cost-estimate.md`
- So với impact / người / tháng (§2): đáng làm không, vì sao:

## §9. Rủi ro & an toàn
- Dữ liệu: đã ẩn danh gì, không thu gì, không đưa gì vào model gói miễn phí:
- AI **không được** làm gì kể cả khi người dùng yêu cầu:
- Ai có thể bị hại nếu AI sai, và nhóm chặn thế nào:

## §10. Phân công & changelog
- Phân công có tên (theo chặng, chia cặp — guide "Cách chia việc"): __
- Dùng AI vào việc gì (2–3 dòng; chi tiết `docs/ai-usage.md`):
- Nhật ký thay đổi — **mọi thay đổi sau CP2 19:30 Thứ Sáu 27/11 phải có dòng ở đây**:

**CP2 → CP4** (vd thu hẹp lát cắt, hỏi thêm người dùng, lần cải tiến trước lượt 2)

| Thời điểm | Đổi gì | Vì sao (trỏ về câu thử / lỗi / bằng chứng nào) |
|---|---|---|
|  |  |  |

**Sau CP4 (đến 23:59 Thứ Bảy 28/11)** (sửa theo góp ý — không sửa chuẩn "đạt", câu thử, số bằng chứng, kết quả các lượt đã chạy)

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
|  |  |  |
