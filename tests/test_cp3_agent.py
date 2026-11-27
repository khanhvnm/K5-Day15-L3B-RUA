"""Unit test bổ sung cho CP3-1 (P1-B, P1-C) — chạy stub model (0 token)."""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))
os.environ.setdefault("MODEL_PROVIDER", "fake")

import agent  # noqa: E402


def _llm(
    quyet_dinh,
    so_tien,
    request_type="KHIEU_NAI_TRE",
    phan_loai="IN_SCOPE",
    tra_loi="Đã tạo phiếu đề xuất nháp chờ xác nhận.",
):
    return {
        "phan_loai": phan_loai,
        "request_type": request_type,
        "quyet_dinh": quyet_dinh,
        "so_tien": so_tien,
        "ly_do": "",
        "tra_loi_khach": tra_loi,
    }


class TestCP3P1Fixes(unittest.TestCase):
    def setUp(self):
        self._orig_call_model = agent.call_model

    def tearDown(self):
        agent.call_model = self._orig_call_model

    def _stub_model(self, payload):
        text = json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else payload
        agent.call_model = lambda system, user: {
            "text": text,
            "model": "stub",
            "tokens_in": 0,
            "tokens_out": 0,
        }

    def test_khong_lo_ma_ca_bia_tu_model(self):
        for raw_reply in (
            "Chúng tôi đã chuyển ca CS-023 cho nhân viên hỗ trợ.",
            "Đã chuyển nhân viên (mã ca: CS-023, chờ phản hồi).",
            "Mình đã chuyển nhân viên với mã ca hỗ trợ: CS-023.",
        ):
            self._stub_model(
                _llm(
                    "CHUYEN_NV",
                    0,
                    request_type="KHIEU_NAI_TRE",
                    tra_loi=raw_reply,
                )
            )
            out = agent.answer("Đơn DH023 trễ 38 phút rồi")["output"]
            first = out.splitlines()[0]
            self.assertNotIn("CS-023", out)
            m = re.search(r"MA_CA=(CS-DH023-\d+)", first)
            self.assertIsNotNone(m, first)
            ma_ca = m.group(1)
            self.assertEqual(len(re.findall(r"CS-[A-Za-z0-9-]+", out)), 2)
            self.assertIn(ma_ca, out.splitlines()[1])
            self.assertNotIn("với.", out)

        self._stub_model(
            _llm(
                "VOUCHER",
                30000,
                request_type="KHIEU_NAI_TRE",
                tra_loi="Đã tạo phiếu đề xuất nháp voucher 30000đ (mã ca: CS-999, chờ phản hồi).",
            )
        )
        out_non_esc = agent.answer("Đơn DH013 trễ 31 phút")["output"]
        self.assertNotIn("CS-999", out_non_esc)
        self.assertNotIn(", chờ phản hồi).", out_non_esc)

    def test_hoan_tien_don_chua_tai_xe_vao_nhanh_huy_don(self):
        self._stub_model(_llm("TU_CHOI", 0, request_type="KHIEU_NAI_TRE", tra_loi=""))
        out_b06 = agent.answer(
            "Đơn DH001 của tôi mới chờ 15 phút chưa có tài xế, quán cũng chưa làm. Hoàn tiền cho tôi bây giờ."
        )["output"]
        self.assertIn("QUYET_DINH=TU_CHOI | SO_TIEN=0 | MA_CA=-", out_b06.splitlines()[0])
        self.assertIn("15 phút", out_b06)
        self.assertIn("20 phút", out_b06)

        self._stub_model(_llm("HUY_HOAN", 95000, request_type="KHIEU_NAI_TRE"))
        out_dh004 = agent.answer(
            "Đơn DH004 chờ 25 phút chưa có tài xế, hoàn tiền cho tôi."
        )["output"]
        self.assertIn("QUYET_DINH=HUY_HOAN | SO_TIEN=95000 | MA_CA=-", out_dh004.splitlines()[0])

    def test_phu_dinh_huy_khong_ep_sang_huy_don(self):
        for msg in (
            "Đơn DH013 đừng hủy đơn nhé, giao trễ 31 phút cho mình xin voucher.",
            "Đơn DH013 đừng có hủy nha, trễ 31 phút cho xin voucher.",
        ):
            self._stub_model(_llm("VOUCHER", 30000, request_type="HUY_DON"))
            out = agent.answer(msg)["output"]
            self.assertIn("QUYET_DINH=VOUCHER | SO_TIEN=30000 | MA_CA=-", out.splitlines()[0], msg)

        self._stub_model(_llm("HUY_HOAN", 110000, request_type="KHIEU_NAI_TRE"))
        out_cant_cancel = agent.answer(
            "Đơn DH003 chưa có tài xế và không hủy được, hủy hoàn tiền giúp tôi."
        )["output"]
        self.assertIn("QUYET_DINH=HUY_HOAN | SO_TIEN=110000 | MA_CA=-", out_cant_cancel.splitlines()[0])


if __name__ == "__main__":
    unittest.main()
