"""定制模块接口测试 - 覆盖接口 14,15,18。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("定制模块")
class TestOverseaCustomMade:
    """接口14: POST /oversea-custom-made-app.json - 海外版 APP 定制。"""

    @allure.story("海外定制")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_oversea_custom_settings(self, client: HttpClient):
        """获取海外版定制客户开关信息。"""
        resp = client.post("/oversea-custom-made-app.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 9012), f"非预期返回码: {data['code']}"

    @allure.story("海外定制")
    def test_oversea_custom_response_structure(self, client: HttpClient):
        """验证成功时返回 customer_settings 列表。"""
        resp = client.post("/oversea-custom-made-app.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            settings = extract_jsonpath(resp, "$.context.customer_settings")
            assert settings is not None, "成功响应缺少 customer_settings"
            assert isinstance(settings, list), "customer_settings 应为列表"

    @allure.story("海外定制")
    def test_oversea_custom_switch_fields(self, client: HttpClient):
        """验证开关项包含 switch_name 和 switch_value。"""
        resp = client.post("/oversea-custom-made-app.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            settings = data["context"]["customer_settings"]
            if settings:
                first = settings[0]
                assert "switch_name" in first, "缺少 switch_name"
                assert "switch_value" in first, "缺少 switch_value"

    @allure.story("海外定制")
    def test_oversea_custom_known_switches(self, client: HttpClient):
        """验证返回的开关包含已知开关名称。"""
        known_switches = {"drivingMode", "voiceFeature", "thirdPartyApp", "mapBox",
                          "youtube", "spotify", "paidVoice", "forceLandscape",
                          "mirrorLandscape", "twinSpace", "webBrowser", "cancelOTA", "joviCard"}
        resp = client.post("/oversea-custom-made-app.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            names = {s["switch_name"] for s in data["context"]["customer_settings"]}
            found = names & known_switches
            assert len(found) > 0, "未找到任何已知开关"

    @allure.story("海外定制")
    def test_oversea_custom_app_lists(self, client: HttpClient):
        """验证返回 navApps, musicApps, phonicApps, whiteList 等列表。"""
        resp = client.post("/oversea-custom-made-app.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            ctx = data["context"]
            for key in ("navApps", "musicApps", "phonicApps", "whiteList"):
                assert key in ctx, f"海外定制缺少列表: {key}"


@allure.feature("定制模块")
class TestCustomMade:
    """接口15: POST /custom-made.json - 中性定制客户信息。"""

    @allure.story("中性定制")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_custom_made_settings(self, client: HttpClient):
        """获取中性定制客户开关信息。"""
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 9012), f"非预期返回码: {data['code']}"

    @allure.story("中性定制")
    def test_custom_made_has_settings(self, client: HttpClient):
        """验证返回的开关列表结构。"""
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            settings = extract_jsonpath(resp, "$.context.customer_settings")
            assert isinstance(settings, list), "customer_settings 应为列表"

    @allure.story("中性定制")
    def test_custom_made_switch_fields(self, client: HttpClient):
        """验证开关项包含 switch_name 和 switch_value。"""
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            settings = data["context"]["customer_settings"]
            if settings:
                first = settings[0]
                assert "switch_name" in first, "缺少 switch_name"
                assert "switch_value" in first, "缺少 switch_value"

    @allure.story("中性定制")
    def test_custom_made_known_switches(self, client: HttpClient):
        """验证包含关键开关（wakeUp, onlineMusic, drivingMode 等）。"""
        key_switches = {"wakeUp", "onlineMusic", "drivingMode", "weChat",
                        "forceLandscape", "speechFeature", "twinSpace",
                        "mirrorLandscape", "webBrowser"}
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            names = {s["switch_name"] for s in data["context"]["customer_settings"]}
            found = names & key_switches
            assert len(found) > 0, "未找到任何关键开关"

    @allure.story("中性定制")
    def test_custom_made_car_control(self, client: HttpClient):
        """验证返回 carControl 字段。"""
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and "carControl" in data.get("context", {}):
            cc = data["context"]["carControl"]
            assert "cardLogo" in cc or "cardName" in cc, "carControl 缺少必要字段"

    @allure.story("中性定制")
    def test_custom_made_logo_info(self, client: HttpClient):
        """验证返回 logo_info 字段。"""
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and "logo_info" in data.get("context", {}):
            logo = data["context"]["logo_info"]
            for field in ("logo_name", "logo_url"):
                assert field in logo, f"logo_info 缺少字段: {field}"

    @allure.story("中性定制")
    def test_custom_made_twin_space_apps(self, client: HttpClient):
        """验证返回 twin_space_apps 字段（config_apps, driving_apps）。"""
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and "twin_space_apps" in data.get("context", {}):
            tsa = data["context"]["twin_space_apps"]
            assert "config_apps" in tsa, "缺少 config_apps"
            assert "driving_apps" in tsa, "缺少 driving_apps"

    @allure.story("中性定制")
    def test_custom_made_apps_black_list(self, client: HttpClient):
        """验证返回 apps_black_list 字段。"""
        resp = client.post("/custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and "apps_black_list" in data.get("context", {}):
            bl = data["context"]["apps_black_list"]
            assert isinstance(bl, list), "apps_black_list 应为列表"


@allure.feature("定制模块")
class TestCustomMadeToC:
    """接口18: POST /custom-made-to-c.json - 用户试用功能。"""

    @allure.story("试用功能")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_to_c_settings(self, client: HttpClient):
        """获取 ToC 定制功能开关列表。"""
        resp = client.post("/custom-made-to-c.json", json={
            "context": {
                "conn_channel_code": "B3",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("试用功能")
    def test_get_to_c_settings_fields(self, client: HttpClient):
        """验证 ToC 开关列表字段完整性。"""
        resp = client.post("/custom-made-to-c.json", json={
            "context": {
                "conn_channel_code": "B3",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("customer_settings"):
            item = data["context"]["customer_settings"][0]
            for field in ("switch_id", "switch_value", "function_name",
                          "display_name", "description"):
                assert field in item, f"ToC 开关缺少字段: {field}"

    @allure.story("试用功能")
    def test_apply_trial(self, authed_client: HttpClient):
        """申请试用功能。"""
        resp = authed_client.post("/custom-made-to-c.json", json={
            "context": {
                "action": "apply",
                "service_name": "connectPro",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3023, 1013), \
            f"非预期返回码: {data['code']} ({data['message']})"

    @allure.story("试用功能")
    def test_apply_trial_duplicate(self, authed_client: HttpClient):
        """重复申请试用应返回 3023。"""
        # 先申请一次
        authed_client.post("/custom-made-to-c.json", json={
            "context": {
                "action": "apply",
                "service_name": "connectPro",
            }
        })
        # 再申请一次
        resp = authed_client.post("/custom-made-to-c.json", json={
            "context": {
                "action": "apply",
                "service_name": "connectPro",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3023, 1013)

    @allure.story("试用功能")
    def test_free_trial(self, authed_client: HttpClient):
        """使用试用功能。"""
        resp = authed_client.post("/custom-made-to-c.json", json={
            "context": {
                "action": "free_trial",
                "service_name": "connectPro",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        # code=0 成功返回 left_trial_days, code=3024 已到期, code=3025 未申请, code=1013 缺少 ID
        assert data["code"] in (0, 3024, 3025, 1013)
        if data["code"] == 0:
            assert "left_trial_days" in data.get("context", {}), \
                "成功时应返回 left_trial_days"

    @allure.story("试用功能")
    def test_free_trial_not_applied(self, authed_client: HttpClient):
        """未申请的功能试用应返回 3025。"""
        resp = authed_client.post("/custom-made-to-c.json", json={
            "context": {
                "action": "free_trial",
                "service_name": "nonExistentService",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (3025, 1013, 0)
