"""亿驾 V3.0 客户端接口测试用例 - 裸写模式（对比数据驱动）。

本文件与 test_api_v3.py 覆盖同一批接口，但采用"每个用例一个函数 + 上下文硬编码"的
朴素写法：
- 不从 YAML 读数据，输入/期望值直接写在用例里
- 不使用 parametrize，一个场景一个独立函数
- 仍复用 core.http_client.HttpClient 做请求（签名、加密是平台能力，无法裸写）

通过 `pytest -m plain` 选中，`pytest -m data_driven` 可切换到数据驱动版。
"""

import pytest
from core.http_client import HttpClient
from core.auth import login

pytestmark = pytest.mark.plain


def _assert_ok(resp, case_name: str):
    """HTTP 200 + code==0 的简单成功断言。"""
    assert resp.status_code == 200, f"[{case_name}] HTTP 错误: {resp.status_code}"
    data = resp.json()
    code = int(data.get("code", -1))
    assert code == 0, f"[{case_name}] 期望 code=0, 实际 code={code}, msg={data.get('message')}"
    return data


def _assert_code_in(resp, expected: list, case_name: str):
    """HTTP 200 + code 在期望集合中。"""
    assert resp.status_code == 200, f"[{case_name}] HTTP 错误: {resp.status_code}"
    data = resp.json()
    code = int(data.get("code", -1))
    assert code in expected, f"[{case_name}] 期望 code 在 {expected}, 实际 {code}, msg={data.get('message')}"
    return data


# ==================== 登录接口 ====================

class TestLogin:
    """POST /login"""

    def test_login_success(self, client):
        # 先发短信密码，再使用固定验证码登录
        client.post("send-sms-password", context={"phone_num": "13877073541"})
        resp = client.post("login", context={
            "login_type": "PHONE",
            "phone_num": "19098545562",
            "sms_password": "884569",
        })
        data = _assert_ok(resp, "LOGIN_success")
        ctx = data["context"]
        assert "user_id" in ctx
        assert "token" in ctx
        assert "user_info" in ctx

    def test_login_phone_empty(self, client):
        resp = client.post("login", context={
            "login_type": "PHONE",
            "phone_num": "",
            "sms_password": "884569",
        })
        _assert_code_in(resp, [3001, 1010], "LOGIN_phone_empty")

    def test_login_sms_empty(self, client):
        resp = client.post("login", context={
            "login_type": "PHONE",
            "phone_num": "19098545562",
            "sms_password": "",
        })
        _assert_code_in(resp, [3001, 1010, 3010], "LOGIN_sms_empty")

    def test_login_wrong_sms(self, client):
        resp = client.post("login", context={
            "login_type": "PHONE",
            "phone_num": "19098545562",
            "sms_password": "999999",
        })
        _assert_code_in(resp, [3010, 3001], "LOGIN_wrong_sms")

    def test_login_invalid_phone_format(self, client):
        resp = client.post("login", context={
            "login_type": "PHONE",
            "phone_num": "123",
            "sms_password": "884569",
        })
        _assert_code_in(resp, [3018, 3003, 3001], "LOGIN_invalid_phone")

    def test_login_non_exist_phone(self, client):
        resp = client.post("login", context={
            "login_type": "PHONE",
            "phone_num": "19999999999",
            "sms_password": "884569",
        })
        _assert_code_in(resp, [3001, 3003], "LOGIN_non_exist_phone")


# ==================== 检查更新 ====================

class TestCheckForUpdates:
    """POST /check-for-updates"""

    def test_check_for_updates(self, client):
        resp = client.post("check-for-updates")
        data = _assert_ok(resp, "UPDATE_001")
        ctx = data["context"]
        # 实际服务端仅返回 client_version/client_settings，文档中的 user_settings 已废弃
        assert "client_version" in ctx
        assert "client_settings" in ctx


# ==================== 意见反馈 ====================

class TestFeedback:
    """POST /feedback"""

    def test_feedback_normal(self, client):
        resp = client.post("feedback", context={
            "name": "feedback",
            "data": {
                "contract": "13545160224",
                "content": "plain mode feedback",
                "country_name": "China",
                "area": "WuHan",
            },
            "time": "2026-04-22 10:00:00",
        })
        _assert_ok(resp, "FEEDBACK_normal")

    def test_feedback_empty_content(self, client):
        resp = client.post("feedback", context={
            "name": "feedback",
            "data": {
                "contract": "13545160224",
                "content": "",
                "country_name": "China",
                "area": "WuHan",
            },
            "time": "2026-04-22 10:00:00",
        })
        _assert_ok(resp, "FEEDBACK_empty_content")

    def test_feedback_special_chars(self, client):
        resp = client.post("feedback", context={
            "name": "feedback",
            "data": {
                "contract": "13877073541",
                "content": "<script>alert('x')</script> & \"quotes\" 特殊字符",
                "country_name": "China",
                "area": "WuHan",
            },
            "time": "2026-04-22 10:00:00",
        })
        _assert_ok(resp, "FEEDBACK_special_chars")


# ==================== 发送短信密码 ====================

class TestSendSmsPassword:
    """POST /send-sms-password"""

    def test_send_sms_normal(self, client):
        resp = client.post("send-sms-password", context={"phone_num": "13877073541"})
        _assert_ok(resp, "SMS_normal")

    def test_send_sms_empty_phone(self, client):
        resp = client.post("send-sms-password", context={"phone_num": ""})
        data = resp.json()
        code = int(data.get("code", -1))
        assert code != 0, f"[SMS_empty_phone] 期望 code!=0, 实际 code={code}"

    def test_send_sms_letters_only(self, client):
        resp = client.post("send-sms-password", context={"phone_num": "abcdefghijk"})
        data = resp.json()
        assert int(data.get("code", -1)) != 0

    def test_send_sms_too_short(self, client):
        resp = client.post("send-sms-password", context={"phone_num": "138"})
        data = resp.json()
        assert int(data.get("code", -1)) != 0

    def test_send_sms_too_long(self, client):
        resp = client.post("send-sms-password", context={"phone_num": "138770735411234"})
        data = resp.json()
        assert int(data.get("code", -1)) != 0


# ==================== 用户完善资料（需要登录） ====================

class TestEditUserInfo:
    """POST /edit-user-info"""

    def test_edit_nick_name(self, authed_client):
        resp = authed_client.post("edit-user-info", context={
            "actions": [{"field_name": "nick_name", "val": "autotest_plain"}]
        })
        data = _assert_ok(resp, "EDIT_nick_name")
        assert "user_info" in data["context"]

    def test_edit_gender(self, authed_client):
        resp = authed_client.post("edit-user-info", context={
            "actions": [{"field_name": "gender", "val": "女"}]
        })
        _assert_ok(resp, "EDIT_gender")

    def test_edit_birth_year(self, authed_client):
        resp = authed_client.post("edit-user-info", context={
            "actions": [{"field_name": "birth_year", "val": "1995-05-20"}]
        })
        _assert_ok(resp, "EDIT_birth_year")

    def test_edit_multi_fields(self, authed_client):
        resp = authed_client.post("edit-user-info", context={
            "actions": [
                {"field_name": "nick_name", "val": "autotest_multi"},
                {"field_name": "gender", "val": "男"},
                {"field_name": "my_car", "val": "4#69#3560"},
            ]
        })
        _assert_ok(resp, "EDIT_multi")

    def test_edit_invalid_field(self, authed_client):
        resp = authed_client.post("edit-user-info", context={
            "actions": [{"field_name": "not_exist_field", "val": "xxx"}]
        })
        _assert_code_in(resp, [0, 3012], "EDIT_invalid_field")


# ==================== 用户登出 ====================

class TestLogout:
    """POST /logout"""

    def test_logout_normal(self, fresh_authed_client):
        # 使用独立登录的 client，避免 logout 销毁共享的 session token
        resp = fresh_authed_client.post("logout", context={"action": "logout"})
        _assert_ok(resp, "LOGOUT_normal")

    def test_logout_no_token(self, client):
        resp = client.post("logout", context={"action": "logout"})
        _assert_code_in(resp, [1013, 1014, 1015], "LOGOUT_no_token")


# ==================== 路况上报 ====================

class TestReportTrafficInfo:
    """POST /report-traffic-info"""

    def test_report_congestion(self, authed_client):
        resp = authed_client.post("report-traffic-info", context={
            "traffic_type": "1",
            "mph": 85,
            "direction": 48.5,
            "time": "2026-04-22 10:00:00",
        })
        _assert_code_in(resp, [0, 5009, 5010, 5016], "REPORT_congestion")

    def test_report_accident(self, authed_client):
        resp = authed_client.post("report-traffic-info", context={
            "traffic_type": "2",
            "mph": 0,
            "direction": 90,
            "time": "2026-04-22 10:00:00",
        })
        _assert_code_in(resp, [0, 5009, 5010, 5016], "REPORT_accident")

    def test_report_missing_type(self, authed_client):
        resp = authed_client.post("report-traffic-info", context={
            "mph": 85,
            "direction": 48.5,
            "time": "2026-04-22 10:00:00",
        })
        data = resp.json()
        assert int(data.get("code", -1)) != 0


# ==================== 常用目的地 ====================

class TestUserDestinations:
    """POST /user-destinations"""

    def test_showlist(self, authed_client):
        resp = authed_client.post("user-destinations", context={"actions": "showlist"})
        data = _assert_ok(resp, "DEST_showlist")
        assert "user_destinations" in data["context"]

    def test_edit(self, authed_client):
        resp = authed_client.post("user-destinations", context={
            "actions": "edit",
            "data": [
                {
                    "dest_name": "家",
                    "dest_address": "裸写模式测试地址",
                    "location": {"longitude": 114.51005, "latitude": 30.561933},
                    "order_id": "0",
                },
            ],
        })
        _assert_ok(resp, "DEST_edit")

    def test_invalid_action(self, authed_client):
        resp = authed_client.post("user-destinations", context={"actions": "invalid_action"})
        _assert_code_in(resp, [3013, 1010], "DEST_invalid_action")

    def test_edit_missing_data(self, authed_client):
        resp = authed_client.post("user-destinations", context={"actions": "edit"})
        _assert_code_in(resp, [1010, 3013], "DEST_edit_missing_data")


# ==================== 用户设置 ====================

class TestUserSettings:
    """POST /user-settings"""

    def test_showlist(self, authed_client):
        resp = authed_client.post("user-settings", context={"actions": "showlist"})
        data = _assert_ok(resp, "SETTING_showlist")
        assert "user_settings" in data["context"]

    def test_edit_single(self, authed_client):
        resp = authed_client.post("user-settings", context={
            "actions": "edit",
            "data": [
                {"id": "1", "setting_name": "screen_always_light", "setting_value": "1"},
            ],
        })
        _assert_ok(resp, "SETTING_edit_single")

    def test_edit_batch(self, authed_client):
        resp = authed_client.post("user-settings", context={
            "actions": "edit",
            "data": [
                {"id": "3", "setting_name": "current_traffic", "setting_value": "1"},
                {"id": "8", "setting_name": "voice_broadcast", "setting_value": "0"},
                {"id": "10", "setting_name": "map_model", "setting_value": "1"},
            ],
        })
        _assert_ok(resp, "SETTING_edit_batch")


# ==================== 签到 ====================

class TestSignIn:
    """POST /sign-in"""

    def test_sign_in(self, authed_client):
        resp = authed_client.post("sign-in", context={"actions": "signin"})
        _assert_code_in(resp, [0, 3014], "SIGNIN")

    def test_sign_in_missing_actions(self, authed_client):
        resp = authed_client.post("sign-in", context={})
        _assert_code_in(resp, [1010, 3013], "SIGNIN_missing_actions")


# ==================== 天气 ====================

class TestWeather:
    """POST /weather"""

    def test_weather_wuhan(self, client):
        resp = client.post("weather", context={
            "location": {"longitude": 114.51005, "latitude": 30.561933}
        })
        _assert_ok(resp, "WEATHER_wuhan")


# ==================== 节假日 ====================

class TestHoliday:
    """POST /holiday"""

    def test_holiday_new_year(self, client):
        resp = client.post("holiday", context={"date": "2026-01-01"})
        _assert_ok(resp, "HOLIDAY_new_year")

    def test_holiday_workday(self, client):
        resp = client.post("holiday", context={"date": "2026-04-22"})
        _assert_ok(resp, "HOLIDAY_workday")


# ==================== 用户资料数据 ====================

class TestUserInfo:
    """POST /user-info"""

    def test_get_user_info(self, authed_client):
        resp = authed_client.post("user-info", context={})
        _assert_ok(resp, "USER_INFO")


# ==================== 车型信息 ====================

class TestCarBrand:
    """POST /car-brand"""

    def test_car_brand_list(self, client):
        resp = client.post("car-brand")
        _assert_ok(resp, "CAR_BRAND")


# ==================== 推荐应用 ====================

class TestRecommendApps:
    """POST /recommend-apps"""

    def test_recommend_apps(self, client):
        resp = client.post("recommend-apps")
        _assert_ok(resp, "RECOMMEND_APPS")


# ==================== 音乐频道 ====================

class TestMusicChannels:
    """POST /music-channels"""

    def test_music_channels(self, client):
        resp = client.post("music-channels")
        _assert_ok(resp, "MUSIC_CHANNELS")


# ==================== 好友列表 ====================

class TestFriendList:
    """POST /friend_list"""

    def test_friend_list(self, authed_client):
        resp = authed_client.post("friend_list", context={})
        _assert_ok(resp, "FRIEND_LIST")


# ==================== 添加好友 ====================

class TestAddFriend:
    """POST /add-friend"""

    def test_add_self_as_friend(self, authed_client):
        resp = authed_client.post("add-friend", context={
            "friend_id": "2000001",
            "word": "认识一下",
        })
        data = resp.json()
        assert int(data.get("code", -1)) != 0, "添加自己应失败"

    def test_add_friend_missing_id(self, authed_client):
        resp = authed_client.post("add-friend", context={"word": "Hi"})
        _assert_code_in(resp, [1010, 6001], "ADD_FRIEND_missing_id")


# ==================== 搜索好友 ====================

class TestSearchFriend:
    """POST /search-friend"""

    def test_search_by_phone(self, authed_client):
        resp = authed_client.post("search-friend", context={"phone_num": "19098545562"})
        _assert_ok(resp, "SEARCH_FRIEND_by_phone")

    def test_search_non_exist_phone(self, authed_client):
        resp = authed_client.post("search-friend", context={"phone_num": "19999999999"})
        _assert_code_in(resp, [0, 4002], "SEARCH_FRIEND_non_exist")


# ==================== 足迹 ====================

class TestFootmark:
    """POST /footmark"""

    def test_show_list(self, authed_client):
        resp = authed_client.post("footmark", context={"actions": "show_list"})
        _assert_ok(resp, "FOOTMARK_show_list")

    def test_unknown_action(self, authed_client):
        resp = authed_client.post("footmark", context={"actions": "unknown_action"})
        _assert_code_in(resp, [3013, 1010], "FOOTMARK_unknown_action")


# ==================== 应用列表上传 ====================

class TestAppList:
    """POST /app-list"""

    def test_upload_normal(self, client):
        resp = client.post("app-list", context={
            "apps": [
                {"name": "手机QQ", "package_name": "com.tencent.qq",
                 "version_name": "v5.6", "version_code": "45"},
                {"name": "微信", "package_name": "com.tencent.weixin",
                 "version_name": "v5.0", "version_code": "45"},
            ]
        })
        _assert_ok(resp, "APP_LIST_normal")

    def test_upload_empty(self, client):
        resp = client.post("app-list", context={"apps": []})
        _assert_ok(resp, "APP_LIST_empty")


# ==================== 行为记录 ====================

class TestRecord:
    """POST /record"""

    def test_startup(self, client):
        resp = client.post("record", context={
            "actions": [{
                "name": "startup",
                "data": {
                    "network": "wifi",
                    "location": {"longitude": 114.51005, "latitude": 30.561933},
                },
                "time": "2026-04-22 10:00:00",
            }]
        })
        _assert_ok(resp, "RECORD_startup")

    def test_client_use_duration(self, client):
        resp = client.post("record", context={
            "actions": [{
                "name": "client_use_duration",
                "data": {"duration": 120},
                "time": "2026-04-22 10:10:00",
            }]
        })
        _assert_ok(resp, "RECORD_use_duration")
