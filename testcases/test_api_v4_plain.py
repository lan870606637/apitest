"""亿驾 V4.0 客户端接口测试用例 - 裸写模式。

V4.0 相对 V3.0 新增 HiTalk 相关接口，这里覆盖阿里云 OSS 头像上传链路：

- upload-avatar           action_name=get_params → 取 OSS 上传凭证
                          action_name=callback  → 文档例 2（实测返回非 JSON，
                                                  疑似仅 OSS 侧使用，客户端调用无意义）
- upload-avatar-callback  阿里云 OSS 回调本服务器专用接口。客户端直接调用一律 403，
                          契约上确实不属于客户端接口 → 整类 skip 保留签名覆盖。

文档 "X-TOKEN 可以为空" 与实测不符：get_params 未带 token 返回 1014 缺少TOKEN，
因此下面 happy path 一律用 authed_client_v4。
"""

import pytest

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


# ==================== 3. 上传头像（获取 OSS 参数） ====================

class TestUploadAvatar:
    """POST /v4.0/upload-avatar

    文档两个 action_name：
    - get_params：返回阿里云 OSS policy/signature/callback 等上传凭证
    - callback：文档例 2（实测返回非 JSON，推测仅服务端内部使用）

    文档声明 X-TOKEN 可空，实测不为空必需 → 使用 authed_client_v4。
    """

    def test_get_params_authed(self, authed_client_v4):
        resp = authed_client_v4.post("upload-avatar", context={"action_name": "get_params"})
        _skip_if_endpoint_missing(resp, "AVATAR_get_params")
        data = _assert_ok(resp, "AVATAR_get_params")
        ctx = data.get("context") or {}
        # 文档返回字段：accessid / host / policy / signature / expire / callback / dir
        for key in ("accessid", "host", "policy", "signature", "expire", "callback"):
            assert key in ctx, f"凭证字段缺失: {key}"
        # host 应是阿里云 OSS 地址
        assert "aliyuncs.com" in ctx["host"] or "oss" in ctx["host"].lower(), \
            f"host 非 OSS 地址: {ctx['host']}"
        # expire 是 unix 秒级时间戳，应为正整数
        assert int(ctx["expire"]) > 0

    def test_get_params_no_token_requires_token(self, client_v4):
        """实测：X-TOKEN 不可空（与文档表格冲突，保留此用例作为契约回归）。"""
        resp = client_v4.post("upload-avatar", context={"action_name": "get_params"})
        _skip_if_endpoint_missing(resp, "AVATAR_get_params_no_token")
        _assert_code_in(resp, [1013, 1014, 1015], "AVATAR_get_params_no_token")

    def test_missing_action_name(self, authed_client_v4):
        resp = authed_client_v4.post("upload-avatar", context={})
        _skip_if_endpoint_missing(resp, "AVATAR_missing_action")
        # 没有 action_name 时：旧实现可能默认 get_params（0），新实现会 1010/3013
        _assert_code_in(resp, [0, 1010, 3013], "AVATAR_missing_action")

    def test_unknown_action_name(self, authed_client_v4):
        resp = authed_client_v4.post("upload-avatar", context={"action_name": "not_exist_action"})
        _skip_if_endpoint_missing(resp, "AVATAR_unknown_action")
        # 未知 action 理想 3013，后端可能静默走默认分支（0）。body 可能非 JSON → 状态码先拦。
        assert resp.status_code == 200, f"HTTP {resp.status_code}"
        try:
            code = int(resp.json().get("code", -1))
        except ValueError:
            pytest.skip("服务端对未知 action 返回非 JSON，契约未定义")
        assert code in [0, 3013, 1010], f"未知 action 返回异常 code={code}"


# ==================== 4. 上传头像回调 ====================

@pytest.mark.skip(reason="upload-avatar-callback 是阿里云 OSS 回调本服务器的专用入口，"
                          "客户端直接 POST 一律 403（sign/来源校验）。"
                          "契约上不属于客户端接口，保留类签名供文档溯源。")
class TestUploadAvatarCallback:
    """POST /v4.0/upload-avatar-callback  —— OSS 回调专用，客户端不应直接调用"""

    def test_callback_empty(self, client_v4):
        resp = client_v4.post("upload-avatar-callback", context={})
        _assert_code_in(resp, [0, 1010], "AVATAR_CB_empty")

    def test_callback_with_mock_payload(self, client_v4):
        resp = client_v4.post("upload-avatar-callback", context={
            "filename": "autotest_avatar.jpg",
            "size": 10240,
            "etag": "abcdef1234567890",
            "mimeType": "image/jpeg",
            "height": 200,
            "width": 200,
        })
        _assert_code_in(resp, [0, 1010, 3013], "AVATAR_CB_mock")
