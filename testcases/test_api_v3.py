"""亿驾 V3.0 客户端接口测试用例 - 数据驱动。

共 10 条用例，覆盖：
- 登录接口（4条）：正常登录、手机号为空、密码为空、密码错误
- 检查更新接口（1条）：正常检查更新
- 意见反馈接口（2条）：正常反馈、反馈内容为空
- 请求短信密码接口（2条）：正常请求、手机号为空
- 用户完善资料接口（1条）：修改昵称
"""

import pytest
from core.http_client import HttpClient
from data import yaml_parametrize


def _code(data: dict) -> int:
    """统一取 code 为 int，服务端可能返回字符串或整数。"""
    return int(data.get("code", -1))


# 业务状态码说明
CODE_MESSAGES = {
    0: "请求成功",
    1001: "缺少签名参数",
    1002: "签名错误",
    1003: "缺少设备信息",
    1004: "缺少客户端信息",
    1005: "服务内部错误",
    1006: "接口不存在",
    1007: "不合的返回格式",
    1008: "不合法的JSON请求",
    1009: "请求方式不支持",
    1010: "字段xx不能为空",
    1011: "缺少APPKEY",
    1012: "错误客户端",
    1013: "缺少USER ID",
    1014: "缺少TOKEN",
    1015: "非法TOKEN",
    1016: "非法USERID",
    1017: "签名格式错误",
    1021: "过期的token",
    2001: "注册失败",
    3001: "登录失败",
    3002: "超过每天发送短信条数最大值",
    3003: "短信密码已失效",
    3004: "此QQ账号已绑定其他帐号",
    3005: "此微信账号已绑定其他帐号",
    3006: "不支持的第三方帐号",
    3007: "无法解绑唯一的第三方帐号",
    3008: "上传头像失败",
    3009: "超出用户保存目的地数量",
    3010: "输入的验证码错误",
    3011: "此手机号已绑定其他帐号",
    3012: "编辑的列名不正确",
    3013: "ACTION NAME不正确",
    3014: "一天只能签到一次",
    3015: "发送短信失败",
    3016: "解绑的帐户不存在",
    3017: "第三方帐户open id 不合法",
    3018: "非法的手机号码格式",
    4001: "%s插入数据失败",
    4002: "%s查询数据失败",
    5001: "错误的导航策略类型",
    5002: "错误的导航结束类型",
    5003: "缺少导航编号",
    5004: "缺少路况编号",
    5005: "路况信息不存在",
    5006: "不存在的路况评价行为",
    5007: "用户与导航用户不匹配",
    5008: "已经评价过该路况",
    5009: "不合法的 location 数据",
    5010: "上报位置不在道路上",
    5011: "缺少导航编码",
    5012: "导航编码已存在",
    5013: "错误的导航路线格式",
    5014: "不存在的行程规划",
    5015: "导航已结束",
    5016: "路况上报过于频繁",
    6001: "添加好友失败",
    6002: "删除好友失败",
    6003: "已经添加过该好友",
    6004: "已经是该用户的好友",
    6005: "不能添加自己为好友",
    7001: "非法的音乐源",
    7002: "缺少音乐频道标识",
}


def _assert_code(case: dict, code: int, message: str):
    """根据测试数据断言业务状态码。"""
    if "expect_code_in" in case:
        assert code in case["expect_code_in"], (
            f"[{case['case_id']}] {case['title']}: "
            f"期望 code 在 {case['expect_code_in']} 中, 实际 code={code}, "
            f"message={message}"
        )

    if "expect_code" in case:
        assert code == case["expect_code"], (
            f"[{case['case_id']}] {case['title']}: "
            f"期望 code={case['expect_code']}, 实际 code={code}, "
            f"message={message}"
        )

    if "expect_code_not" in case:
        assert code != case["expect_code_not"], (
            f"[{case['case_id']}] {case['title']}: "
            f"期望 code 不为 {case['expect_code_not']}, 实际 code={code}"
        )


def _log_code_info(case_id: str, code: int, message: str):
    """打印业务状态码信息。"""
    code_desc = CODE_MESSAGES.get(code, "未知状态码")
    print(f"[{case_id}] code: {code}, message: {message}, 说明: {code_desc}")


# ==================== 登录接口测试 ====================

_login_cases, _login_ids = yaml_parametrize("login_phone")


@pytest.mark.parametrize("case", _login_cases, ids=_login_ids)
class TestLogin:
    """用户登录接口 POST /login"""

    def test_login(self, client, case):
        # 如果需要在登录前发送短信验证码
        if case.get("need_send_sms_before_login"):
            phone_num = case["context"].get("phone_num", "")
            if phone_num:
                # 调用发送短信接口
                sms_resp = client.post("send-sms-password", context={"phone_num": phone_num})
                sms_data = sms_resp.json()
                sms_code = _code(sms_data)
                _log_code_info(case["case_id"] + "-SMS", sms_code, sms_data.get("message", ""))
                # 无论发送成功失败都继续，因为使用的是固定验证码
        
        resp = client.post("login", context=case["context"])
        
        # 断言 HTTP 状态码
        assert resp.status_code == 200, (
            f"[{case['case_id']}] HTTP 状态码错误: 期望 200, 实际 {resp.status_code}"
        )
        
        data = resp.json()
        code = _code(data)
        message = data.get("message", "")
        
        # 打印业务状态码信息
        _log_code_info(case["case_id"], code, message)
        
        # 业务状态码断言
        _assert_code(case, code, message)

        # 登录成功时验证返回字段
        if code == 0 and "expect_fields_on_success" in case:
            ctx = data.get("context", {})
            for field in case["expect_fields_on_success"]:
                assert field in ctx, (
                    f"[{case['case_id']}] 登录成功响应缺少字段: {field}"
                )


# ==================== 检查更新接口测试 ====================

_update_cases, _update_ids = yaml_parametrize("check_for_updates")


@pytest.mark.parametrize("case", _update_cases, ids=_update_ids)
class TestCheckForUpdates:
    """检查更新接口 POST /check-for-updates"""

    def test_check_for_updates(self, client, case):
        resp = client.post("check-for-updates", context=case.get("context"))
        
        # 断言 HTTP 状态码
        assert resp.status_code == 200, (
            f"[{case['case_id']}] HTTP 状态码错误: 期望 200, 实际 {resp.status_code}"
        )
        
        data = resp.json()
        code = _code(data)
        message = data.get("message", "")
        
        # 打印业务状态码信息
        _log_code_info(case["case_id"], code, message)
        
        # 业务状态码断言
        _assert_code(case, code, message)

        if code == 0 and "expect_fields" in case:
            ctx = data.get("context", {})
            for field in case["expect_fields"]:
                assert field in ctx, (
                    f"[{case['case_id']}] 响应缺少字段: {field}"
                )


# ==================== 意见反馈接口测试 ====================

_feedback_cases, _feedback_ids = yaml_parametrize("feedback")


@pytest.mark.parametrize("case", _feedback_cases, ids=_feedback_ids)
class TestFeedback:
    """意见反馈接口 POST /feedback"""

    def test_feedback(self, client, case):
        resp = client.post("feedback", context=case["context"])
        
        # 断言 HTTP 状态码
        assert resp.status_code == 200, (
            f"[{case['case_id']}] HTTP 状态码错误: 期望 200, 实际 {resp.status_code}"
        )
        
        data = resp.json()
        code = _code(data)
        message = data.get("message", "")
        
        # 打印业务状态码信息
        _log_code_info(case["case_id"], code, message)
        
        # 业务状态码断言
        _assert_code(case, code, message)


# ==================== 请求短信密码接口测试 ====================

_sms_cases, _sms_ids = yaml_parametrize("send_sms_password")


@pytest.mark.parametrize("case", _sms_cases, ids=_sms_ids)
class TestSendSmsPassword:
    """请求短信密码接口 POST /send-sms-password"""

    def test_send_sms_password(self, client, case):
        resp = client.post("send-sms-password", context=case["context"])
        
        # 断言 HTTP 状态码
        assert resp.status_code == 200, (
            f"[{case['case_id']}] HTTP 状态码错误: 期望 200, 实际 {resp.status_code}"
        )
        
        data = resp.json()
        code = _code(data)
        message = data.get("message", "")
        
        # 打印业务状态码信息
        _log_code_info(case["case_id"], code, message)
        
        # 业务状态码断言
        _assert_code(case, code, message)


# ==================== 用户完善资料接口测试（需要登录） ====================

_edit_cases, _edit_ids = yaml_parametrize("edit_user_info")


@pytest.mark.parametrize("case", _edit_cases, ids=_edit_ids)
class TestEditUserInfo:
    """用户完善资料接口 POST /edit-user-info（需要 token）"""

    def test_edit_user_info(self, authed_client, case):
        resp = authed_client.post("edit-user-info", context=case["context"])
        
        # 断言 HTTP 状态码
        assert resp.status_code == 200, (
            f"[{case['case_id']}] HTTP 状态码错误: 期望 200, 实际 {resp.status_code}"
        )
        
        data = resp.json()
        code = _code(data)
        message = data.get("message", "")
        
        # 打印业务状态码信息
        _log_code_info(case["case_id"], code, message)
        
        # 业务状态码断言
        _assert_code(case, code, message)

        if code == 0 and "expect_fields" in case:
            ctx = data.get("context", {})
            for field in case["expect_fields"]:
                assert field in ctx, (
                    f"[{case['case_id']}] 响应缺少字段: {field}"
                )
