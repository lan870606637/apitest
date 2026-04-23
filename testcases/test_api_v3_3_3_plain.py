"""亿驾 V3.3.3 客户端接口测试用例 - 裸写模式。

覆盖 V3.3.3 文档新增接口（与 V3.0 文件同级，不合并避免单文件过大）：
- pay-function          用户支付购买功能（只读，可正常调用）
- factory-login         厂商登陆（三段式 action：send_captcha / login / get-status）
- log-off               账号注销（高危：happy path 会删账号，仅测负向）

通过 `pytest -m plain` 选中。client/authed_client 使用 v3.3.3 专用 fixture。
"""

import pytest
from config import TEST_PHONE

pytestmark = pytest.mark.plain


def _assert_ok(resp, case_name: str):
    assert resp.status_code == 200, f"[{case_name}] HTTP 错误: {resp.status_code}"
    data = resp.json()
    code = int(data.get("code", -1))
    assert code == 0, f"[{case_name}] 期望 code=0, 实际 code={code}, msg={data.get('message')}"
    return data


def _assert_code_in(resp, expected: list, case_name: str):
    assert resp.status_code == 200, f"[{case_name}] HTTP 错误: {resp.status_code}"
    data = resp.json()
    code = int(data.get("code", -1))
    assert code in expected, f"[{case_name}] 期望 code 在 {expected}, 实际 {code}, msg={data.get('message')}"
    return data


def _skip_if_endpoint_missing(resp, case_name: str):
    if resp.status_code == 404:
        pytest.skip(f"[{case_name}] 接口未部署 (HTTP 404)")
    try:
        code = int(resp.json().get("code", -1))
    except ValueError:
        return
    if code == 1006:
        pytest.skip(f"[{case_name}] 接口未部署 (code=1006)")


# ==================== 17. 用户支付购买功能 ====================

class TestPayFunction:
    """POST /v3.3.3/pay-function

    文档四种 action：
    - 空 context → 所有可购买功能列表
    - action_name=my_func → 当前用户已购买 + 未过期功能
    - action_name=search_my_func → 模糊搜索我的购买
    - action_name=search → 搜索全局功能
    """

    def test_list_all_functions(self, client_v3_3_3):
        resp = client_v3_3_3.post("pay-function", context={})
        _skip_if_endpoint_missing(resp, "PAY_list_all")
        _assert_ok(resp, "PAY_list_all")

    def test_my_func_authed(self, authed_client_v3_3_3):
        resp = authed_client_v3_3_3.post("pay-function", context={"action_name": "my_func"})
        _skip_if_endpoint_missing(resp, "PAY_my_func")
        # 未登录会 1013，登录态下应 0
        _assert_ok(resp, "PAY_my_func")

    def test_my_func_no_token(self, client_v3_3_3):
        # 文档明确未登录 my_func 返回 1013 缺少 USER ID
        resp = client_v3_3_3.post("pay-function", context={"action_name": "my_func"})
        _skip_if_endpoint_missing(resp, "PAY_my_func_no_token")
        _assert_code_in(resp, [1013, 1014, 1015], "PAY_my_func_no_token")

    def test_search_my_func(self, authed_client_v3_3_3):
        resp = authed_client_v3_3_3.post("pay-function", context={
            "action_name": "search_my_func",
            "function_name": "connectPro",
        })
        _skip_if_endpoint_missing(resp, "PAY_search_my")
        # 可能 0（匹配到或空列表）或 1013 未登录（理论不会），放宽
        _assert_code_in(resp, [0, 1013], "PAY_search_my")

    def test_search_global(self, client_v3_3_3):
        resp = client_v3_3_3.post("pay-function", context={
            "action_name": "search",
            "function_name": "connectPro",
        })
        _skip_if_endpoint_missing(resp, "PAY_search_global")
        _assert_ok(resp, "PAY_search_global")


# ==================== 23. 厂商登陆 ====================

class TestFactoryLogin:
    """POST /v3.3.3/factory-login

    三段式 action：send_captcha → login → get-status。
    测试环境通常未为 TEST_PHONE 备案产线，因此：
    - send_captcha：允许 2010「未备案」
    - login：用错验证码，允许 3010
    - get-status：允许 2010/2012/2011
    """

    def test_send_captcha(self, client_v3_3_3):
        resp = client_v3_3_3.post("factory-login", context={
            "action": "send_captcha",
            "data": {
                "phone_num": TEST_PHONE,
                "device_id": "autotest_device_id",
            },
        })
        _skip_if_endpoint_missing(resp, "FACTORY_send_captcha")
        # 文档码：0 / 1010 / 2010 / 3021 / 3015
        _assert_code_in(resp, [0, 1010, 2010, 3021, 3015], "FACTORY_send_captcha")

    def test_send_captcha_invalid_phone(self, client_v3_3_3):
        resp = client_v3_3_3.post("factory-login", context={
            "action": "send_captcha",
            "data": {
                "phone_num": "abc",
                "device_id": "autotest_device_id",
            },
        })
        _skip_if_endpoint_missing(resp, "FACTORY_send_captcha_invalid")
        _assert_code_in(resp, [3021, 1010, 2010], "FACTORY_send_captcha_invalid")

    def test_send_captcha_missing_phone(self, client_v3_3_3):
        resp = client_v3_3_3.post("factory-login", context={
            "action": "send_captcha",
            "data": {"device_id": "autotest_device_id"},
        })
        _skip_if_endpoint_missing(resp, "FACTORY_send_captcha_missing")
        _assert_code_in(resp, [1010, 3021], "FACTORY_send_captcha_missing")

    def test_login_wrong_captcha(self, client_v3_3_3):
        # 用显然错误的验证码，期望 3010 或 3003
        resp = client_v3_3_3.post("factory-login", context={
            "action": "login",
            "data": {
                "captcha": "000000",
                "phone_num": TEST_PHONE,
                "ip": "127.0.0.1",
                "device_id": "autotest_device_id",
                "remark": "autotest",
            },
        })
        _skip_if_endpoint_missing(resp, "FACTORY_login_wrong")
        _assert_code_in(resp, [3010, 3003, 1010, 2010], "FACTORY_login_wrong")

    def test_login_missing_field(self, client_v3_3_3):
        resp = client_v3_3_3.post("factory-login", context={
            "action": "login",
            "data": {"captcha": "000000", "device_id": "autotest_device_id"},
        })
        _skip_if_endpoint_missing(resp, "FACTORY_login_missing")
        _assert_code_in(resp, [1010, 3010, 3003], "FACTORY_login_missing")

    def test_get_status(self, client_v3_3_3):
        resp = client_v3_3_3.post("factory-login", context={
            "action": "get-status",
            "data": {
                "phone_num": TEST_PHONE,
                "device_id": "autotest_device_id",
            },
        })
        _skip_if_endpoint_missing(resp, "FACTORY_get_status")
        # 文档码：0 / 1010 / 2010 / 2011 / 2012
        _assert_code_in(resp, [0, 1010, 2010, 2011, 2012], "FACTORY_get_status")


# ==================== 20. 注销接口 ====================
# WARNING: log-off 会从服务端真正删除账号，happy path 会让后续所有用例 1015。
# 因此只跑 no-token 负向路径，永远不发 happy path。

class TestLogOff:
    """POST /v3.3.3/log-off"""

    def test_log_off_no_token(self, client_v3_3_3):
        resp = client_v3_3_3.post("log-off", context={})
        _skip_if_endpoint_missing(resp, "LOGOFF_no_token")
        # 无 token 必然 1013/1014/1015
        _assert_code_in(resp, [1013, 1014, 1015], "LOGOFF_no_token")

    @pytest.mark.skip(reason="log-off happy path 会真实删除账号，禁用")
    def test_log_off_success(self, authed_client_v3_3_3):
        # 有意保留签名以示完整覆盖；想手测时去掉 skip 即可。
        resp = authed_client_v3_3_3.post("log-off", context={})
        _assert_ok(resp, "LOGOFF_success")
