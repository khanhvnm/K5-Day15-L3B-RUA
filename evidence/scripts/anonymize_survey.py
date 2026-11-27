"""Ẩn danh kết quả khảo sát: evidence/survey/raw-khaosat.csv -> evidence/survey/results.csv

Chạy:  python evidence/scripts/anonymize_survey.py          # ghi results.csv
       python evidence/scripts/anonymize_survey.py --dem    # ghi + in số đếm theo luật ở questions.md

Luật (ghi trong evidence/survey/questions.md, mục "Lưu kết quả"):
  1. Bỏ dòng trùng: cùng một email gửi nhiều lần -> giữ lần gửi CUỐI (theo Timestamp).
     Dòng không có email thì giữ nguyên (không có cách biết trùng).
  2. Bỏ cột nhận dạng: Timestamp, Email Address, cột cách liên hệ (chỉ giữ có / không để lại).
  3. Gộp cách viết tay ở câu "Bạn là": bạn / ban / bạn bè / ban be -> "Bạn bè ngoài lớp".
File raw-* bị .gitignore chặn, không commit. Chỉ dùng thư viện chuẩn.
"""
import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "evidence" / "survey" / "raw-khaosat.csv"
OUT = ROOT / "evidence" / "survey" / "results.csv"

COT_THOI_GIAN = "Timestamp"
COT_EMAIL = "Email Address"
COT_LIEN_HE = "Bạn có sẵn lòng cho nhóm hỏi thêm 10 phút không? Nếu có, để lại cách liên hệ"
COT_BAN_LA = "Bạn là"
COT_CO_DAT = "Trong 1 tháng qua, bạn có đặt đồ ăn qua app không?"
COT_SO_LAN_TRE = ("Một tháng qua, bao nhiêu lần đơn của bạn giao muộn hơn giờ dự kiến "
                  "app báo từ 15 phút trở lên?")
COT_KET_QUA = "Kết quả cuối cùng?"
COT_SAU_DO = "Sau lần đó, bạn dùng app đó thế nào?"

BAN_BE = {"bạn", "ban", "bạn bè", "ban be"}


def doc_raw():
    with open(RAW, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for c in (COT_THOI_GIAN, COT_EMAIL, COT_LIEN_HE, COT_BAN_LA):
        if c not in rows[0]:
            sys.exit("Không thấy cột %r trong %s — form đã đổi câu hỏi?" % (c, RAW.name))
    return rows


def bo_trung(rows):
    thoi_gian = lambda r: datetime.strptime(r[COT_THOI_GIAN], "%m/%d/%Y %H:%M:%S")
    rows = sorted(rows, key=thoi_gian)
    cuoi = {}
    for i, r in enumerate(rows):
        email = r[COT_EMAIL].strip().lower()
        if email:
            cuoi[email] = i
    giu = [r for i, r in enumerate(rows)
           if not r[COT_EMAIL].strip() or cuoi[r[COT_EMAIL].strip().lower()] == i]
    return giu, len(rows) - len(giu)


def an_danh(rows):
    cot_giu = [c for c in rows[0] if c not in (COT_THOI_GIAN, COT_EMAIL, COT_LIEN_HE)]
    out = []
    for stt, r in enumerate(rows, 1):
        d = {"stt": stt}
        for c in cot_giu:
            v = r[c].strip()
            if c == COT_BAN_LA and v.lower() in BAN_BE:
                v = "Bạn bè ngoài lớp"
            d[c] = v
        d["de_lai_lien_he"] = "có" if r[COT_LIEN_HE].strip() else "không"
        out.append(d)
    return out


def dem(rows):
    co_dat = [r for r in rows if r[COT_CO_DAT] == "Có"]
    tre = [r for r in co_dat if r[COT_SO_LAN_TRE] and r[COT_SO_LAN_TRE] != "0 lần"]
    n, x = len(co_dat), len(tre)
    print("Mẫu số (có đặt đồ ăn qua app 1 tháng qua): n = %d / %d người trả lời" % (n, len(rows)))
    print("Số chính 1 — gặp >= 1 lần giao muộn >= 15': %d/%d (%.1f%%)" % (x, n, 100 * x / n if n else 0))
    ket_qua = {}
    for r in tre:
        ket_qua[r[COT_KET_QUA]] = ket_qua.get(r[COT_KET_QUA], 0) + 1
    print("Số chính 2 — kết quả cuối (trong %d người gặp trễ):" % x)
    for k, v in sorted(ket_qua.items(), key=lambda kv: -kv[1]):
        print("   %2d/%d  %s" % (v, x, k or "(bỏ trống)"))
    sau = {}
    for r in tre:
        sau[r[COT_SAU_DO]] = sau.get(r[COT_SAU_DO], 0) + 1
    print("Sau lần đó:", ", ".join("%s %d/%d" % (k or "(bỏ trống)", v, x) for k, v in sau.items()))


def main():
    rows = doc_raw()
    rows, so_trung = bo_trung(rows)
    out = an_danh(rows)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print("Đã ghi %s: %d dòng (bỏ %d dòng trùng email)" % (OUT.relative_to(ROOT), len(out), so_trung))
    if "--dem" in sys.argv:
        dem(out)


if __name__ == "__main__":
    main()
