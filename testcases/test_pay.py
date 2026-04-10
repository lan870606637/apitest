"""支付模块接口测试 - 覆盖接口 17,25,30。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("支付模块")
class TestPayFunction:
    """接口17: POST /pay-function.json - 用户支付购买功能。"""

    @allure.story("功能购买")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_function_list(self, client: HttpClient):
        """获取所有付费功能列表。"""
        resp = client.post("/pay-function.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("功能购买")
    def test_function_list_structure(self, client: HttpClient):
        """验证付费功能列表返回结构。"""
        resp = client.post("/pay-function.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        items = extract_jsonpath(resp, "$.context.list")
        if items:
            first = items[0]
            for field in ("id", "switch_id", "function_name", "display_name",
                          "description", "validity_date", "price",
                          "is_trial", "trial_days", "ios_product_id"):
                assert field in first, f"功能项缺少字段: {field}"

    @allure.story("功能购买")
    def test_get_my_functions(self, authed_client: HttpClient):
        """获取用户已购买的有效期内功能列表。"""
        resp = authed_client.post("/pay-function.json", json={
            "context": {
                "action_name": "my_func",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 1013)

    @allure.story("功能购买")
    def test_my_functions_fields(self, authed_client: HttpClient):
        """验证已购功能列表字段完整性。"""
        resp = authed_client.post("/pay-function.json", json={
            "context": {"action_name": "my_func"}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("my_functions"):
            item = data["context"]["my_functions"][0]
            for field in ("product_id", "switch_id", "function_name",
                          "display_name", "expire_date"):
                assert field in item, f"已购功能缺少字段: {field}"

    @allure.story("功能购买")
    def test_search_my_function(self, authed_client: HttpClient):
        """搜索用户购买的指定功能。"""
        resp = authed_client.post("/pay-function.json", json={
            "context": {
                "action_name": "search_my_func",
                "function_name": "connectPro",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 1013)

    @allure.story("功能购买")
    def test_search_my_function_with_hardware(self, authed_client: HttpClient):
        """车机二维码搜索（carPay + hardware_id）。"""
        resp = authed_client.post("/pay-function.json", json={
            "context": {
                "action_name": "search_my_func",
                "function_name": "carPay",
                "hardware_id": "ABCDEFG123456",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 1013)

    @allure.story("功能购买")
    def test_search_function(self, client: HttpClient):
        """搜索指定功能信息。"""
        resp = client.post("/pay-function.json", json={
            "context": {
                "action_name": "search",
                "function_name": "connectPro",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)


@allure.feature("支付模块")
class TestMapboxOrder:
    """接口25: POST /mapbox-order.json - Mapbox 支付。"""

    @allure.story("Mapbox支付")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_mapbox_create_order_android(self, authed_client: HttpClient):
        """Android 创建 Mapbox 订单。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "create_order",
                "data": {
                    "order_id": "GPA.3319-8913-4350-54013",
                    "package_name": "net.easyconn.carman.wws",
                    "product_id": "carbit_subscription",
                    "purchase_time": 1608883927246,
                    "purchase_state": 1,
                    "purchase_token": "test_purchase_token_autotest",
                    "purchase_device_type": "phone",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            ctx = data["context"]
            assert "is_valid" in ctx, "缺少 is_valid"
            assert ctx["is_valid"] in (0, 1, -1), "is_valid 值异常"

    @allure.story("Mapbox支付")
    def test_mapbox_create_order_ios(self, authed_client: HttpClient):
        """iOS 创建 Mapbox 订单。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "ios_create_order",
                "data": {
                    "order_id": "GPA.3319-8913-4350-IOS01",
                    "package_name": "net.easyconn.carman.wws",
                    "product_id": "carbit_subscription",
                    "purchase_time": 1608883927246,
                    "purchase_device_type": "phone",
                }
            }
        })
        assert_status(resp, 200)

    @allure.story("Mapbox支付")
    def test_mapbox_products_list(self, authed_client: HttpClient):
        """获取 Mapbox 商品列表。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "products_list",
                "language": "zh",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            products = data["context"].get("products_list", [])
            assert isinstance(products, list), "products_list 应为列表"
            if products:
                for field in ("product_id", "product_name", "product_price"):
                    assert field in products[0], f"商品缺少字段: {field}"

    @allure.story("Mapbox支付")
    @pytest.mark.parametrize("lang", ["zh", "en"])
    def test_mapbox_products_list_language(self, authed_client: HttpClient, lang):
        """不同语言获取商品列表。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "products_list",
                "language": lang,
            }
        })
        assert_status(resp, 200)

    @allure.story("Mapbox支付")
    def test_mapbox_check_sn(self, authed_client: HttpClient):
        """检查设备 SN 是否存在。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "check_sn",
                "data": {
                    "hardware_id": "hardware_id_1234",
                    "bluetooth_mac": "bluetooth_mac_test",
                    "bluetooth_uuid": "bluetooth_uuid_test",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "trial_days" in data["context"], "缺少 trial_days"

    @allure.story("Mapbox支付")
    def test_mapbox_trial(self, authed_client: HttpClient):
        """试用设备。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "trial",
                "data": {
                    "hardware_id": "hardware_id_1234",
                    "bluetooth_mac": "bluetooth_mac_test",
                    "bluetooth_uuid": "bluetooth_uuid_test",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "trial_days" in data["context"], "缺少 trial_days"

    @allure.story("Mapbox支付")
    def test_mapbox_record_device(self, authed_client: HttpClient):
        """新增设备记录。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "record",
                "data": {
                    "hardware_id": "hardware_id_autotest",
                    "bluetooth_mac": "bt_mac_autotest",
                    "bluetooth_uuid": "bt_uuid_autotest",
                    "channel_code": "autotest_channel",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3033, 3034), f"非预期返回码: {data['code']}"

    @allure.story("Mapbox支付")
    def test_mapbox_expired_date(self, authed_client: HttpClient):
        """获取用户过期日期。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "expired_date",
                "purchase_device_type": "phone",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            ctx = data["context"]
            assert "is_valid" in ctx, "缺少 is_valid"
            assert ctx["is_valid"] in (0, 1, -1)

    @allure.story("Mapbox支付")
    def test_mapbox_special_trial(self, authed_client: HttpClient):
        """检查用户是否体验过0.99商品。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "special_trial",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "can_trial" in data["context"], "缺少 can_trial"
            assert data["context"]["can_trial"] in (0, 1)

    @allure.story("Mapbox支付")
    def test_mapbox_get_function_list(self, authed_client: HttpClient):
        """获取设备功能列表。"""
        resp = authed_client.post("/mapbox-order.json", json={
            "context": {
                "action_name": "get_function_list",
                "data": {
                    "hardware_id": "123.12345678",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 1010, 3033)
        if data["code"] == 0 and data.get("context", {}).get("function_list"):
            item = data["context"]["function_list"][0]
            assert "right_name" in item, "缺少 right_name"
            assert "function_list" in item, "缺少 function_list"


@allure.feature("支付模块")
class TestUserPayFunction:
    """接口30: POST /user-pay-function.json - 显示用户购买功能数据。"""

    @allure.story("购买数据")
    @allure.severity(allure.severity_level.NORMAL)
    def test_user_pay_function_default(self, client: HttpClient):
        """默认返回付费功能列表。"""
        resp = client.post("/user-pay-function.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("pay_functions_list"):
            item = data["context"]["pay_functions_list"][0]
            for field in ("id", "switch_id", "function_name", "display_name",
                          "validity_date", "price"):
                assert field in item, f"付费功能缺少字段: {field}"

    @allure.story("购买数据")
    def test_user_pay_function_screen_mirror(self, authed_client: HttpClient):
        """查询屏幕镜像功能信息。"""
        resp = authed_client.post("/user-pay-function.json", json={
            "context": {
                "action_name": "screenMirror",
                "data": {
                    "conn_channel_code": "11111",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("pay_function"):
            pf = data["context"]["pay_function"]
            assert pf["function_name"] == "screenMirror"
            assert "switch_value" in pf, "缺少 switch_value"
            assert "is_paid" in pf, "缺少 is_paid"

    @allure.story("购买数据")
    def test_user_pay_function_switch_on_fields(self, authed_client: HttpClient):
        """功能开关为开时验证额外字段。"""
        resp = authed_client.post("/user-pay-function.json", json={
            "context": {
                "action_name": "screenMirror",
                "data": {"conn_channel_code": "11111"}
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            pf = data["context"].get("pay_function", {})
            if pf.get("switch_value") == 1:
                assert "is_paid" in pf, "开关开启时缺少 is_paid"
