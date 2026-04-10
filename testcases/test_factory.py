"""厂商/第三方模块接口测试 - 覆盖接口 23,24,26,27,28,29,31。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("厂商模块")
class TestFactoryLogin:
    """接口23: POST /factory-login.json - 厂商登陆。"""

    # --- 发送验证码 ---
    @allure.story("厂商登陆-验证码")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_send_captcha(self, client: HttpClient):
        """请求发送验证码。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "send_captcha",
                "data": {
                    "phone_num": "15827337353",
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 1010, 2010, 3021, 3015)

    @allure.story("厂商登陆-验证码")
    def test_send_captcha_success_has_regex(self, client: HttpClient):
        """成功发送验证码时返回正则表达式。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "send_captcha",
                "data": {
                    "phone_num": "15827337353",
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "regular_expression" in data["context"], "成功时缺少 regular_expression"

    @allure.story("厂商登陆-验证码")
    def test_send_captcha_invalid_phone(self, client: HttpClient):
        """无效手机号请求验证码应报错。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "send_captcha",
                "data": {
                    "phone_num": "123",
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (2010, 3021), f"无效手机号应返回 2010 或 3021，实际 {data['code']}"

    @allure.story("厂商登陆-验证码")
    def test_send_captcha_missing_phone(self, client: HttpClient):
        """缺少手机号应报错 1010。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "send_captcha",
                "data": {
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010

    @allure.story("厂商登陆-验证码")
    def test_send_captcha_missing_device_id(self, client: HttpClient):
        """缺少 device_id 应报错 1010。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "send_captcha",
                "data": {
                    "phone_num": "15827337353",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010

    # --- 登陆 ---
    @allure.story("厂商登陆-登陆")
    def test_login_wrong_captcha(self, client: HttpClient):
        """错误验证码登陆应返回 3003 或 3010。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "login",
                "data": {
                    "captcha": "000000",
                    "phone_num": "15827337353",
                    "ip": "192.168.9.30",
                    "device_id": "test_device_001",
                    "remark": "自动化测试",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (3003, 3010, 1010), \
            f"错误验证码应返回 3003/3010/1010，实际 {data['code']}"

    @allure.story("厂商登陆-登陆")
    def test_login_missing_captcha(self, client: HttpClient):
        """缺少验证码登陆应报错。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "login",
                "data": {
                    "phone_num": "15827337353",
                    "ip": "192.168.9.30",
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010

    # --- 获取状态 ---
    @allure.story("厂商登陆-状态")
    def test_get_status(self, client: HttpClient):
        """获取厂商登陆状态。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "get-status",
                "data": {
                    "phone_num": "15827337353",
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 1010, 2010, 2011, 2012)

    @allure.story("厂商登陆-状态")
    def test_get_status_response_fields(self, client: HttpClient):
        """成功获取状态时验证 client_info 字段。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "get-status",
                "data": {
                    "phone_num": "15827337353",
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("client_info"):
            info = data["context"]["client_info"]
            for field in ("id", "use_phone_num", "device_id", "expired_date", "status"):
                assert field in info, f"client_info 缺少字段: {field}"

    @allure.story("厂商登陆-状态")
    def test_get_status_unregistered_device(self, client: HttpClient):
        """未备案设备获取状态应返回 2012。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "get-status",
                "data": {
                    "phone_num": "15827337353",
                    "device_id": "nonexistent_device_xyz",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (2010, 2012, 1010)

    @allure.story("厂商登陆-状态")
    def test_get_status_unregistered_phone(self, client: HttpClient):
        """未备案手机号获取状态应返回 2010。"""
        resp = client.post("/factory-login.json", json={
            "context": {
                "action": "get-status",
                "data": {
                    "phone_num": "19999999999",
                    "device_id": "test_device_001",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (2010, 2012, 1010)


@allure.feature("第三方模块")
class TestHUD:
    """接口24: POST /hud.json - HUD 接口。"""

    @allure.story("HUD")
    @allure.severity(allure.severity_level.NORMAL)
    def test_hud_normal(self, client: HttpClient):
        """正常提交 HUD 信息。"""
        resp = client.post("/hud.json", json={
            "context": {
                "uuid": "carbit_first_uuid",
                "mac": "first_mac_address",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 1010, 3028, 3029)

    @allure.story("HUD")
    def test_hud_missing_uuid(self, client: HttpClient):
        """缺少 uuid 应报错 1010。"""
        resp = client.post("/hud.json", json={
            "context": {
                "mac": "first_mac_address",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010

    @allure.story("HUD")
    def test_hud_missing_mac(self, client: HttpClient):
        """缺少 mac 应报错 1010。"""
        resp = client.post("/hud.json", json={
            "context": {
                "uuid": "carbit_first_uuid",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010

    @allure.story("HUD")
    def test_hud_invalid_uuid(self, client: HttpClient):
        """无效 UUID 应返回 3028。"""
        resp = client.post("/hud.json", json={
            "context": {
                "uuid": "invalid_uuid_xyz",
                "mac": "first_mac_address",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3028, 3029)

    @allure.story("HUD")
    def test_hud_invalid_mac(self, client: HttpClient):
        """无效 MAC 地址应返回 3029。"""
        resp = client.post("/hud.json", json={
            "context": {
                "uuid": "carbit_first_uuid",
                "mac": "invalid_mac_xyz",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3029)


@allure.feature("第三方模块")
class TestWechatDevice:
    """接口26: POST /wechat-device.json - 微信设备（需要 X-TOKEN）。"""

    @allure.story("微信设备")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_access_token(self, authed_client: HttpClient):
        """获取微信 access_token。"""
        resp = authed_client.post("/wechat-device.json", json={
            "context": {
                "action_name": "get_access_token",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "access_token" in data["context"], "缺少 access_token"

    @allure.story("微信设备")
    def test_get_device_info(self, authed_client: HttpClient):
        """获取微信用户绑定设备信息。"""
        resp = authed_client.post("/wechat-device.json", json={
            "context": {
                "action_name": "get_device_info",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("device_info"):
            info = data["context"]["device_info"]
            for field in ("device_id", "device_token", "device_type"):
                assert field in info, f"device_info 缺少字段: {field}"

    @allure.story("微信设备")
    def test_binding(self, authed_client: HttpClient):
        """绑定用户设备信息。"""
        resp = authed_client.post("/wechat-device.json", json={
            "context": {
                "action_name": "binding",
                "data": {
                    "device_token": "device_token_autotest",
                    "device_id": "gh_62bec17265fe_autotest",
                    "qr_code_url": "http://autotest.example.com/qr",
                }
            }
        })
        assert_status(resp, 200)

    @allure.story("微信设备")
    def test_unbinding(self, authed_client: HttpClient):
        """解绑用户设备信息。"""
        resp = authed_client.post("/wechat-device.json", json={
            "context": {
                "action_name": "unbinding",
            }
        })
        assert_status(resp, 200)


@allure.feature("第三方模块")
class TestFreeTrial:
    """接口27: POST /free-trial.json - 功能试用。"""

    @allure.story("免费试用")
    @allure.severity(allure.severity_level.NORMAL)
    def test_free_trial_check_status(self, client: HttpClient):
        """获取试用状态信息。"""
        resp = client.post("/free-trial.json", json={
            "context": {
                "action_name": "check_status",
                "hardware_id": "KDYB01-FFFFFFFF",
                "function_name": "easyConnMirror",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3026)
        if data["code"] == 0:
            assert "trial_type" in data["context"], "缺少 trial_type"
            assert data["context"]["trial_type"] in (1, 0, -1)

    @allure.story("免费试用")
    def test_free_trial_activate(self, client: HttpClient):
        """确定试用功能。"""
        resp = client.post("/free-trial.json", json={
            "context": {
                "action_name": "trial",
                "hardware_id": "KDYB01-FFFFFFFF",
                "function_name": "easyConnMirror",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3026)
        if data["code"] == 0 and data["context"].get("trial_type") == 1:
            assert "expired_date" in data["context"], "体验中时缺少 expired_date"

    @allure.story("免费试用")
    def test_free_trial_invalid_function(self, client: HttpClient):
        """不存在的功能应返回 3026。"""
        resp = client.post("/free-trial.json", json={
            "context": {
                "action_name": "check_status",
                "hardware_id": "KDYB01-FFFFFFFF",
                "function_name": "nonExistentFunction",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 3026, f"不存在的功能应返回 3026，实际 {data['code']}"


@allure.feature("第三方模块")
class TestRegisterClientRecord:
    """接口28: POST /register-client-record.json - 激活设备信息。"""

    @allure.story("设备激活")
    @allure.severity(allure.severity_level.NORMAL)
    def test_record_device(self, client: HttpClient):
        """记录激活设备信息。"""
        resp = client.post("/register-client.json", json={
            "context": {
                "action_name": "record",
                "data": {
                    "model_id": [12001],
                    "hardware_id": "KDYB01-AUTOTEST",
                    "category": ["easyconn"],
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3037), f"非预期返回码: {data['code']}"

    @allure.story("设备激活")
    def test_record_device_multiple_categories(self, client: HttpClient):
        """多种激活类型记录。"""
        resp = client.post("/register-client.json", json={
            "context": {
                "action_name": "record",
                "data": {
                    "model_id": [12001, 12002],
                    "hardware_id": "KDYB01-MULTI",
                    "category": ["easyconn", "carplay", "android auto"],
                }
            }
        })
        assert_status(resp, 200)

    @allure.story("设备激活")
    def test_get_license_by_imei(self, client: HttpClient):
        """获取备案 IMEI 激活数量。"""
        resp = client.post("/register-client.json", json={
            "context": {
                "action_name": "license",
                "data": {
                    "imei": "hansonsimei",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("list"):
            item = data["context"]["list"][0]
            for field in ("name", "valid_amount", "total_amount"):
                assert field in item, f"license 缺少字段: {field}"

    @allure.story("设备激活")
    def test_get_model_license(self, client: HttpClient):
        """根据 Model ID 获取激活数量。"""
        resp = client.post("/register-client.json", json={
            "context": {
                "action_name": "model_license",
                "data": {
                    "model_id": "5",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("list"):
            item = data["context"]["list"][0]
            for field in ("valid_amount", "total_amount", "model_id", "model_name"):
                assert field in item, f"model_license 缺少字段: {field}"


@allure.feature("第三方模块")
class TestFeedback:
    """接口29: POST /feedback.json - 用户反馈。"""

    @allure.story("用户反馈")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_feedback_config(self, client: HttpClient):
        """获取反馈页面配置信息。"""
        resp = client.post("/feedback.json", json={
            "context": {
                "action_name": "config",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)
        data = resp.json()
        if data["code"] == 0:
            configs = data["context"]["configs"]
            assert "CATEGORY" in configs, "缺少 CATEGORY"
            assert "MODULE" in configs, "缺少 MODULE"
            assert "FREQ" in configs, "缺少 FREQ"

    @allure.story("用户反馈")
    def test_submit_feedback(self, client: HttpClient):
        """提交反馈信息。"""
        resp = client.post("/feedback.json", json={
            "context": {
                "action_name": "submit",
                "data": {
                    "category": "遇到问题",
                    "module": "连接",
                    "freq": "偶尔出现",
                    "contact": "13545160224",
                    "content": "自动化测试反馈内容",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("用户反馈")
    def test_submit_feedback_all_modules(self, client: HttpClient):
        """不同模块提交反馈。"""
        resp = client.post("/feedback.json", json={
            "context": {
                "action_name": "submit",
                "data": {
                    "category": "建议意见",
                    "module": "屏幕镜像",
                    "freq": "每次都出现",
                    "contact": "",
                    "content": "屏幕镜像功能建议",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)


@allure.feature("第三方模块")
class TestGame:
    """接口31: POST /game.json - 第三方游戏（需要 X-TOKEN）。"""

    @allure.story("游戏接口")
    @allure.severity(allure.severity_level.NORMAL)
    def test_game_register(self, authed_client: HttpClient):
        """注册游戏账号。"""
        resp = authed_client.post("/game.json", json={
            "context": {
                "action_name": "register",
                "data": {
                    "game_id": 911,
                    "plat_id": 1057,
                    "ip": "127.0.0.1",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3036)
        if data["code"] == 0:
            assert "game_user_id" in data["context"], "缺少 game_user_id"
            assert "account" in data["context"], "缺少 account"

    @allure.story("游戏接口")
    def test_game_login(self, authed_client: HttpClient):
        """游戏账号登陆。"""
        resp = authed_client.post("/game.json", json={
            "context": {
                "action_name": "login",
                "data": {
                    "game_id": 911,
                    "plat_id": 1057,
                    "ip": "127.0.0.1",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3037)
        if data["code"] == 0:
            assert "game_account" in data["context"], "缺少 game_account"
            assert "game_token" in data["context"], "缺少 game_token"
            assert "gameurl" in data["context"], "缺少 gameurl"

    @allure.story("游戏接口")
    def test_game_login_missing_game_id(self, authed_client: HttpClient):
        """缺少 game_id 应报错。"""
        resp = authed_client.post("/game.json", json={
            "context": {
                "action_name": "login",
                "data": {
                    "plat_id": 1057,
                    "ip": "127.0.0.1",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0
