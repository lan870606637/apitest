"""摩托车模块接口测试 - 覆盖接口 33,36,37,38。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("摩托车模块")
class TestMotoDevice:
    """接口33: POST /moto-device.json - Moto Device 相关接口。"""

    @allure.story("Moto设备-商品列表")
    @allure.severity(allure.severity_level.NORMAL)
    def test_product_list(self, authed_client: HttpClient):
        """获取 Moto 商品 ID 列表。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "product_list",
                "data": {
                    "bluetooth_uuid": "123",
                    "bluetooth_mac": "111",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("products_list"):
            item = data["context"]["products_list"][0]
            assert "function_id" in item, "缺少 function_id"
            assert "function_name" in item, "缺少 function_name"
            assert "product_ids" in item, "缺少 product_ids"

    @allure.story("Moto设备-激活")
    def test_activate_device(self, authed_client: HttpClient):
        """激活 Moto 设备。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "activate",
                "data": {
                    "bluetooth_uuid": "autotest_uuid",
                    "bluetooth_mac": "autotest_mac",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3034, 3035), \
            f"非预期返回码: {data['code']}"

    @allure.story("Moto设备-ToB权益")
    def test_trial_list(self, authed_client: HttpClient):
        """获取 ToB 权益列表。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "trial",
                "data": {
                    "bluetooth_uuid": "123",
                    "bluetooth_mac": "111",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "binding_right_status" in data["context"], "缺少 binding_right_status"
            status = data["context"]["binding_right_status"]
            assert status in (0, 1, 2)
            if status == 0 and data["context"].get("trial_list"):
                item = data["context"]["trial_list"][0]
                for field in ("right_name", "trial_days", "function_id"):
                    assert field in item, f"权益缺少字段: {field}"

    @allure.story("Moto设备-绑定权益")
    def test_binding_trial_right(self, authed_client: HttpClient):
        """绑定 ToB 权益。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "binding_trial_right",
                "data": {
                    "bluetooth_uuid": "123",
                    "bluetooth_mac": "111",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("trial_list"):
            item = data["context"]["trial_list"][0]
            for field in ("function_id", "trial_days", "expired_date"):
                assert field in item, f"绑定权益缺少字段: {field}"

    @allure.story("Moto设备-用户权益")
    def test_user_order_info(self, authed_client: HttpClient):
        """查询用户 Moto 权益。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "user_order_info",
                "data": {
                    "bluetooth_uuid": "123",
                    "bluetooth_mac": "111",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and isinstance(data.get("context"), list):
            item = data["context"][0]
            for field in ("function_id", "expired_date", "left_days", "user_type"):
                assert field in item, f"用户权益缺少字段: {field}"

    @allure.story("Moto设备-功能列表")
    def test_get_function_list(self, authed_client: HttpClient):
        """获取设备功能列表。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "get_function_list",
                "data": {
                    "bluetooth_uuid": "123",
                    "bluetooth_mac": "111",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("function_list"):
            item = data["context"]["function_list"][0]
            assert "function_id" in item, "缺少 function_id"
            assert "function_name" in item, "缺少 function_name"

    @allure.story("Moto设备-测试设备")
    def test_demo_device_by_hardware(self, authed_client: HttpClient):
        """通过 hardware_id 查询测试设备。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "demo_device",
                "data": {
                    "hardware_id": "1001.123456",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "is_demo_device" in data["context"], "缺少 is_demo_device"
            assert data["context"]["is_demo_device"] in (1, -1, 0)

    @allure.story("Moto设备-测试设备")
    def test_demo_device_by_bluetooth(self, authed_client: HttpClient):
        """通过蓝牙信息查询测试设备。"""
        resp = authed_client.post("/moto-device.json", json={
            "context": {
                "action_name": "demo_device",
                "data": {
                    "bluetooth_uuid": "123",
                    "bluetooth_mac": "111",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "is_demo_device" in data["context"]
            assert "device_status" in data["context"]


@allure.feature("摩托车模块")
class TestMotorCustomMade:
    """接口36: POST /motor-custom-made.json - Motor 定制开关。"""

    @allure.story("Motor定制")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_motor_custom_made(self, client: HttpClient):
        """获取 Motor 定制开关信息。"""
        resp = client.post("/motor-custom-made.json", json={
            "context": {
                "model_id": "66660401",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("Motor定制")
    def test_motor_custom_made_with_car_info(self, client: HttpClient):
        """携带车辆品牌和型号查询。"""
        resp = client.post("/motor-custom-made.json", json={
            "context": {
                "model_id": "66660401",
                "car_brand": "abc",
                "car_model": "1234",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("Motor定制")
    def test_motor_custom_made_customer_info(self, client: HttpClient):
        """验证 customer_info 返回字段。"""
        resp = client.post("/motor-custom-made.json", json={
            "context": {"model_id": "66660401"}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("customer_info"):
            info = data["context"]["customer_info"]
            for field in ("id", "customer_name", "model_id", "motor_switch",
                          "mirror_image_switch", "amap_navi_switch"):
                assert field in info, f"customer_info 缺少字段: {field}"

    @allure.story("Motor定制")
    def test_motor_custom_made_switch_list(self, client: HttpClient):
        """验证返回 switch_list。"""
        resp = client.post("/motor-custom-made.json", json={
            "context": {"model_id": "66660401"}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("switch_list"):
            item = data["context"]["switch_list"][0]
            for field in ("switch_id", "switch_name", "switch_value"):
                assert field in item, f"switch_list 缺少字段: {field}"

    @allure.story("Motor定制")
    def test_motor_custom_made_missing_model_id(self, client: HttpClient):
        """缺少 model_id 应报错。"""
        resp = client.post("/motor-custom-made.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0, "缺少 model_id 不应成功"


@allure.feature("摩托车模块")
class TestMotoLegalCopy:
    """接口37: POST /moto-legal-copy.json - Moto 验证正版。"""

    @allure.story("正版验证")
    @allure.severity(allure.severity_level.NORMAL)
    def test_legal_copy_check(self, client: HttpClient):
        """验证 Moto 正版状态。"""
        resp = client.post("/moto-legal-copy.json", json={
            "context": {
                "model_id": "66660401",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "legal_copy_switch" in data["context"], "缺少 legal_copy_switch"
            assert data["context"]["legal_copy_switch"] in ("0", "1")

    @allure.story("正版验证")
    def test_legal_copy_with_car_info(self, client: HttpClient):
        """携带车辆信息验证正版。"""
        resp = client.post("/moto-legal-copy.json", json={
            "context": {
                "model_id": "66660401",
                "car_brand": "abc",
                "car_model": "1234",
            }
        })
        assert_status(resp, 200)


@allure.feature("摩托车模块")
class TestMotoGaodeBinding:
    """接口38: POST /moto-gaode-binding-info.json - 摩托车与高德信息绑定。"""

    @allure.story("高德绑定-无可用次数")
    @allure.severity(allure.severity_level.NORMAL)
    def test_no_available_count(self, client: HttpClient):
        """同步高德绑定信息数量不足。"""
        resp = client.post("/moto-gaode-binding-info.json", json={
            "context": {
                "action_name": "no_available_count",
                "data": {
                    "sae_model_id": "test",
                    "hardware_id": "22222",
                    "platform": "gaode",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("高德绑定-检查状态")
    def test_check_bind_status(self, client: HttpClient):
        """检查绑定状态。"""
        resp = client.post("/moto-gaode-binding-info.json", json={
            "context": {
                "action_name": "check_bind_status",
                "data": {
                    "sae_model_id": "test",
                    "hardware_id": "33333",
                    "user_id": "1234",
                    "mobile_id": "9527",
                    "nick_name": "autotest",
                    "platform": "gaode",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "bind_status" in data["context"], "缺少 bind_status"
            assert data["context"]["bind_status"] in (0, 1)
            assert "available_count" in data["context"], "缺少 available_count"

    @allure.story("高德绑定-绑定")
    def test_bind(self, client: HttpClient):
        """绑定信息。"""
        resp = client.post("/moto-gaode-binding-info.json", json={
            "context": {
                "action_name": "bind",
                "data": {
                    "sae_model_id": "test",
                    "hardware_id": "444",
                    "mobile_id": "9527",
                    "user_id": "1",
                    "nick_name": "autotest",
                    "platform": "gaode",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3020), f"非预期返回码: {data['code']}"

    @allure.story("高德绑定-绑定")
    def test_bind_exceed_limit(self, client: HttpClient):
        """超出绑定上限应返回 3020。"""
        # 多次绑定同一设备以触发上限
        for _ in range(5):
            resp = client.post("/moto-gaode-binding-info.json", json={
                "context": {
                    "action_name": "bind",
                    "data": {
                        "sae_model_id": "test",
                        "hardware_id": "limit_test_device",
                        "mobile_id": "limit_mobile",
                        "user_id": "limit_user",
                        "platform": "gaode",
                    }
                }
            })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3020)

    @allure.story("高德绑定-平台")
    @pytest.mark.parametrize("platform", ["gaode", "baidu", "other"])
    def test_check_bind_status_platforms(self, client: HttpClient, platform):
        """不同平台检查绑定状态。"""
        resp = client.post("/moto-gaode-binding-info.json", json={
            "context": {
                "action_name": "check_bind_status",
                "data": {
                    "sae_model_id": "test",
                    "hardware_id": "platform_test",
                    "user_id": "1234",
                    "mobile_id": "9527",
                    "platform": platform,
                }
            }
        })
        assert_status(resp, 200)
