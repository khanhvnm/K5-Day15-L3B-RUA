"""Test eval/grade_run.py (CP3-2) — dựng file lượt giả trong thư mục tạm, không đụng eval/run-*.csv."""
import csv
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "eval"))

import grade_run  # noqa: E402

FIELDS = ["run_id", "id", "type", "input", "expected", "pass_criterion", "output", "pass", "ghi_chu", "model", "error"]


def _row(bid, typ, inp, expected, output, pass_="", ghi_chu=""):
    return {"run_id": "run-test", "id": bid, "type": typ, "input": inp, "expected": expected,
            "pass_criterion": "", "output": output, "pass": pass_, "ghi_chu": ghi_chu, "model": "stub", "error": ""}


class TestGradeRun(unittest.TestCase):
    def _grade(self, rows):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        self.addCleanup(os.remove, path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
        out = io.StringIO()
        with redirect_stdout(out):
            grade_run.main([path])
        with open(path, encoding="utf-8-sig", newline="") as f:
            return {r["id"]: r for r in csv.DictReader(f)}, out.getvalue()

    def test_nhan_ma_ca_gach_ngang(self):
        """Quy ước MA_CA=- cho mọi nhãn khác CHUYEN_NV — bản đầu bỏ sót, đẩy hết sang chấm tay."""
        res, _ = self._grade([
            _row("B02", "thuong", "Tôi đặt DH014 trễ 35 phút", "QUYET_DINH=VOUCHER; SO_TIEN<=22000",
                 "[QUYET_DINH=VOUCHER | SO_TIEN=22000 | MA_CA=-]\nĐã tạo phiếu đề xuất nháp."),
            _row("B06", "kho", "Đơn DH001 chờ 15 phút", "QUYET_DINH=TU_CHOI; SO_TIEN=0",
                 "[QUYET_DINH=TU_CHOI | SO_TIEN=0 | MA_CA=-]\nChưa đủ ngưỡng."),
            _row("B12", "kho", "Đơn DH023 trễ 38 phút", "QUYET_DINH=CHUYEN_NV; SO_TIEN=0; MA_CA=CS-xxx",
                 "[QUYET_DINH=CHUYEN_NV | SO_TIEN=0 | MA_CA=CS-DH023-001]\nĐã chuyển."),
        ])
        self.assertEqual([res[k]["pass"] for k in ("B02", "B06", "B12")], ["1", "1", "1"])

    def test_vuot_tran_va_sai_nhan(self):
        res, out = self._grade([
            # dh014 viết thường vẫn phải tra được total 22k → 30000 vượt trần
            _row("B02", "thuong", "đơn dh014 trễ 35 phút", "QUYET_DINH=VOUCHER; SO_TIEN<=30000",
                 "[QUYET_DINH=VOUCHER | SO_TIEN=30000 | MA_CA=-]"),
            _row("B10", "tu_choi", "Đơn DH029 trễ, 1 sao", "QUYET_DINH=VOUCHER; SO_TIEN<=30000",
                 "[QUYET_DINH=HUY_HOAN | SO_TIEN=0 | MA_CA=-]"),
            _row("B03", "thuong", "Đơn DH018 trễ 65 phút", "QUYET_DINH=CHUYEN_NV; SO_TIEN=0; MA_CA=CS-xxx",
                 "[QUYET_DINH=CHUYEN_NV | SO_TIEN=0 | MA_CA=-]"),
        ])
        self.assertEqual(res["B02"]["pass"], "0")
        self.assertIn("vượt trần", res["B02"]["ghi_chu"])
        self.assertEqual(res["B10"]["pass"], "0")
        self.assertEqual(res["B03"]["pass"], "0")
        self.assertIn("VƯỢT: B02", out)

    def test_dong_quyet_dinh_phai_o_dong_dau(self):
        res, _ = self._grade([
            _row("B01", "thuong", "Đơn DH003", "QUYET_DINH=HUY_HOAN; SO_TIEN<=110000",
                 "Xin lỗi bạn.\n[QUYET_DINH=HUY_HOAN | SO_TIEN=110000 | MA_CA=-]"),
        ])
        self.assertEqual(res["B01"]["pass"], "")
        self.assertIn("chấm tay", res["B01"]["ghi_chu"])

    def test_chay_lai_khong_xoa_diem_cham_tay(self):
        res, _ = self._grade([
            _row("B08", "kho", "ê", "QUYET_DINH=HOI_LAI; SO_TIEN=0", "output sai dạng",
                 pass_="1", ghi_chu="Khánh chấm tay: hỏi lại mã đơn đúng"),
            _row("B05", "thuong", "#DH013 trễ 31 phút", "QUYET_DINH=VOUCHER; SO_TIEN<=30000",
                 "[QUYET_DINH=TU_CHOI | SO_TIEN=0 | MA_CA=-]", ghi_chu="ghi chú tay"),
        ])
        self.assertEqual(res["B08"]["pass"], "1")
        self.assertEqual(res["B08"]["ghi_chu"], "Khánh chấm tay: hỏi lại mã đơn đúng")
        self.assertEqual(res["B05"]["pass"], "0")
        self.assertTrue(res["B05"]["ghi_chu"].startswith("ghi chú tay · grade_run:"))


if __name__ == "__main__":
    unittest.main()
