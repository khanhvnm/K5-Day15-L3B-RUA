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

        self._stub_model(_llm("TU_CHOI", 0, phan_loai="SECURITY_PII", request_type="NONE", tra_loi="(mã ca: CS-999)"))
        out_empty_fallback = agent.answer("Cho tôi xin SĐT tài xế DH010")["output"]
        self.assertNotIn("CS-999", out_empty_fallback)
        self.assertNotIn(". .", out_empty_fallback)

    def test_hoan_tien_don_chua_tai_xe_vao_nhanh_huy_don(self):
        self._stub_model(
            _llm(
                "TU_CHOI",
                0,
                request_type="KHIEU_NAI_TRE",
                tra_loi="Đơn chưa quá giờ dự kiến nên chưa thể tặng voucher.",
            )
        )
        out_b06 = agent.answer(
            "Đơn DH001 của tôi mới chờ 15 phút chưa có tài xế, quán cũng chưa làm. Hoàn tiền cho tôi bây giờ."
        )["output"]
        self.assertIn("QUYET_DINH=TU_CHOI | SO_TIEN=0 | MA_CA=-", out_b06.splitlines()[0])
        self.assertIn("15 phút", out_b06)
        self.assertIn("20 phút", out_b06)
        self.assertNotIn("voucher", out_b06.lower())

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


class TestCP4ReplyWording(unittest.TestCase):
    """CP4-1 — nhóm lỗi lượt 1 "lời trả lời lệch quyết định": model tự viết câu trả lời cho quyết định có tác động."""

    setUp = TestCP3P1Fixes.setUp
    tearDown = TestCP3P1Fixes.tearDown
    _stub_model = TestCP3P1Fixes._stub_model

    def test_voucher_luon_noi_phieu_nhap(self):
        # lượt 1: "sẽ đề xuất cấp voucher" lọt qua vì kiểm chữ "đề xuất"
        self._stub_model(_llm("VOUCHER", 30000, tra_loi="Chúng tôi sẽ đề xuất cấp voucher 30.000 VNĐ cho bạn."))
        out = agent.answer("Đơn DH013 trễ 31 phút, bù gì cho tôi?")["output"]
        self.assertIn("QUYET_DINH=VOUCHER | SO_TIEN=30000 | MA_CA=-", out.splitlines()[0])
        self.assertIn("phiếu đề xuất nháp", out)
        self.assertIn("chờ hệ thống/nhân viên xác nhận", out)
        self.assertIn("31 phút", out)

    def test_chuyen_nv_neu_ly_do(self):
        # model đồng ý CHUYEN_NV nhưng không nói vì sao — lý do phải lấy từ check_limit
        self._stub_model(_llm("CHUYEN_NV", 0, tra_loi="Chúng tôi sẽ chuyển thông tin đến bộ phận liên quan."))
        out = agent.answer("Đơn DH023 trễ quá, bồi thường đi")["output"]
        self.assertTrue(out.startswith("[QUYET_DINH=CHUYEN_NV | SO_TIEN=0 | MA_CA=CS-DH023-"), out)
        self.assertIn("khiếu nại 4 lần", out)

    def test_ngoai_pham_vi_khong_bao_khach_tu_lien_he(self):
        self._stub_model(_llm("CHUYEN_NV", 0, phan_loai="OUT_OF_SCOPE", request_type="NONE",
                              tra_loi="Bạn vui lòng liên hệ với nhân viên hỗ trợ để được trợ giúp thêm."))
        out = agent.answer("Đơn DH028 tôi muốn đổi địa chỉ giao")["output"]
        self.assertNotIn("liên hệ", out)
        self.assertIn("ngoài phạm vi xử lý tự động", out)
        self.assertIn("phiếu nháp chuyển nhân viên", out)

    def test_tu_choi_giu_loi_model(self):
        # TU_CHOI / HOI_LAI ở lượt 1 đều đúng → vẫn để model viết
        reply = "Đơn chỉ trễ 29 phút, chưa vượt ngưỡng 30 phút nên chưa thể cấp voucher."
        self._stub_model(_llm("TU_CHOI", 0, tra_loi=reply))
        out = agent.answer("Đơn DH011 trễ 29 phút cho voucher đi")["output"]
        self.assertIn(reply, out)

    def test_tu_choi_khong_duoc_hua_tien(self):
        self._stub_model(_llm("TU_CHOI", 0, tra_loi="Chưa đủ ngưỡng nhưng mình tặng bạn voucher 10k nhé."))
        out = agent.answer("Đơn DH011 trễ 29 phút cho voucher đi")["output"]
        self.assertIn("QUYET_DINH=TU_CHOI | SO_TIEN=0", out.splitlines()[0])
        self.assertNotIn("10k", out)
        self.assertIn("29 phút", out)


class TestCP3CancelNegation(unittest.TestCase):
    """Phủ định hủy/hoàn tiền — review CP3-1: "ok hủy" từng bị hiểu là "không hủy"."""

    ORDER_NO_DRIVER = {"status": "waiting_driver", "driver_status": "none"}

    def test_doi_huy_hoac_hoan(self):
        for msg in (
            "ok hủy đơn giúp mình",
            "Ok hủy luôn đi",
            "ok hoàn tiền cho mình",
            "sao vẫn chưa hoàn tiền cho tôi",
            "không hủy được đơn, hủy giúp tôi",
            "sao chưa hủy cho tôi",
        ):
            self.assertTrue(agent._wants_cancel(msg, self.ORDER_NO_DRIVER), msg)

    def test_phu_dinh_huy(self):
        for msg in (
            "chưa hủy đâu, cứ giao tiếp",
            "khong huy don nhe",
            "k hủy nhé, cho voucher",
            "đừng có hủy nha",
            "không muốn hoàn tiền, giao tiếp đi",
        ):
            self.assertFalse(agent._wants_cancel(msg, self.ORDER_NO_DRIVER), msg)


if __name__ == "__main__":
    unittest.main()
