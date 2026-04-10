"""平行世界模块接口测试 - 覆盖接口 32,42,43,44。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("平行世界模块")
class TestTwinSpace:
    """接口32: POST /twin-space.json - 平行世界相关接口。"""

    @allure.story("平行世界-App列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_twin_space_app_list(self, authed_client: HttpClient):
        """获取平行世界 App 列表。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("平行世界-App列表")
    def test_twin_space_app_list_fields(self, authed_client: HttpClient):
        """验证 App 列表条目字段。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("app_list"):
            item = data["context"]["app_list"][0]
            for field in ("app_name", "package_name", "icon_path"):
                assert field in item, f"App 列表缺少字段: {field}"

    @allure.story("平行世界-ROM")
    def test_twin_space_rom(self, authed_client: HttpClient):
        """查询 ROM 更新信息。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {
                "action_name": "rom",
                "data": {
                    "version_code": 12.1,
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("平行世界-ROM")
    def test_twin_space_rom_has_update(self, authed_client: HttpClient):
        """有更新时验证 ROM 信息字段。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {
                "action_name": "rom",
                "data": {"version_code": 1.0}
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("rom_update_info"):
            rom = data["context"]["rom_update_info"]
            for field in ("rom_name", "package_name", "md5_num",
                          "version_code", "rom_path", "force_update"):
                assert field in rom, f"ROM 信息缺少字段: {field}"

    @allure.story("平行世界-埋点")
    def test_twin_space_record(self, authed_client: HttpClient):
        """记录埋点数据。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {
                "action_name": "record",
                "data": {
                    "hardware_id": "10381.123456789",
                    "client_id": "217",
                    "client_ip": "192.168.9.30",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("平行世界-黑白名单")
    def test_twin_space_black_white_list(self, authed_client: HttpClient):
        """查询设备黑白名单。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {
                "action_name": "black_white_list",
                "data": {
                    "device_model": "SM-G9880",
                    "device_chip": "snapdragon888",
                    "device_os_version": "12",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            status = data["context"].get("device_valid_status")
            assert status in (0, 1), f"device_valid_status 值异常: {status}"

    @allure.story("平行世界-设备记录")
    def test_twin_space_record_valid_device(self, authed_client: HttpClient):
        """记录有效设备信息。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {
                "action_name": "record_valid_device",
                "data": {
                    "device_name": "HONOR V31",
                    "device_brand": "HONOR",
                    "device_model": "OXF-AN01",
                    "device_chip": "kirin991",
                    "device_os": "Harmony",
                    "device_os_version": "OXF-AN00 3.0.0.208(C00E195R3P6)",
                    "device_memory": "8GB",
                    "category": "home",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            level = data["context"].get("device_level")
            assert level in (-1, 1), f"device_level 值异常: {level}"

    @allure.story("平行世界-设备记录")
    @pytest.mark.parametrize("category", ["home", "abroad"])
    def test_twin_space_record_device_category(self, authed_client: HttpClient, category):
        """国内/海外设备记录。"""
        resp = authed_client.post("/twin-space.json", json={
            "context": {
                "action_name": "record_valid_device",
                "data": {
                    "device_name": "Test Device",
                    "device_brand": "TestBrand",
                    "device_model": "TestModel",
                    "device_chip": "test_chip",
                    "device_os": "Android",
                    "device_os_version": "13",
                    "device_memory": "8GB",
                    "category": category,
                }
            }
        })
        assert_status(resp, 200)


@allure.feature("平行世界模块")
class TestTwinSpaceV2:
    """接口42: POST /twin-space-v2.json - 平行世界 2.0。"""

    @allure.story("平行世界V2-App列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_twin_space_v2_app_list(self, client: HttpClient):
        """获取平行世界 V2 App 列表。"""
        resp = client.post("/twin-space-v2.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("平行世界V2-App列表")
    def test_twin_space_v2_app_fields(self, client: HttpClient):
        """验证 V2 App 列表条目字段。"""
        resp = client.post("/twin-space-v2.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("app_list"):
            item = data["context"]["app_list"][0]
            for field in ("app_name", "package_name", "software_category",
                          "import_from", "sort_index", "app_type"):
                assert field in item, f"V2 App 缺少字段: {field}"

    @allure.story("平行世界V2-App列表")
    def test_twin_space_v2_has_config_switch(self, client: HttpClient):
        """验证返回 app_config_open 开关。"""
        resp = client.post("/twin-space-v2.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "app_config_open" in data["context"], "缺少 app_config_open"

    @allure.story("平行世界V2-设备适配")
    def test_twin_space_v2_record_valid_device(self, client: HttpClient):
        """V2 记录设备信息返回适配状态。"""
        resp = client.post("/twin-space-v2.json", json={
            "context": {
                "action_name": "record_valid_device",
                "data": {
                    "device_name": "HONOR V31",
                    "device_brand": "HONOR",
                    "device_model": "OXF-AN01",
                    "device_chip": "kirin991",
                    "device_os": "Harmony",
                    "device_os_version": "OXF-AN00 3.0.0.208",
                    "device_memory": "8GB",
                    "category": "home",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            level = data["context"].get("device_level")
            assert level in (-1, 1), f"device_level 值异常: {level}"


@allure.feature("平行世界模块")
class TestYLSpace:
    """接口43: POST /yl-space.json - 亿连空间。"""

    @allure.story("亿连空间-Banner首页")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_yl_space_banner_index(self, client: HttpClient):
        """获取亿连空间首页 Banner 信息。"""
        resp = client.post("/yl-space.json", json={
            "context": {
                "action_name": "banner_index",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "recommend_banner_list" in data["context"], "缺少 recommend_banner_list"

    @allure.story("亿连空间-分类首页")
    def test_yl_space_category_app_index(self, client: HttpClient):
        """获取推荐分类首页信息。"""
        resp = client.post("/yl-space.json", json={
            "context": {
                "action_name": "category_app_index",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "recommend_app_list" in data["context"], "缺少 recommend_app_list"

    @allure.story("亿连空间-分类首页")
    def test_yl_space_category_app_fields(self, client: HttpClient):
        """验证分类 App 列表字段。"""
        resp = client.post("/yl-space.json", json={
            "context": {"action_name": "category_app_index"}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("recommend_app_list"):
            cat = data["context"]["recommend_app_list"][0]
            assert "software_category" in cat, "缺少 software_category"
            assert "software_category_name" in cat, "缺少 software_category_name"
            assert "app_list" in cat, "缺少 app_list"

    @allure.story("亿连空间-分类分页")
    def test_yl_space_category_app_page(self, client: HttpClient):
        """推荐分类分页查询。"""
        resp = client.post("/yl-space.json", json={
            "context": {
                "action_name": "category_app_page",
                "data": {
                    "page": 1,
                    "software_category": "6",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            for field in ("software_category", "page", "pagesize",
                          "total_count", "total_page", "app_list"):
                assert field in data["context"], f"分页缺少字段: {field}"

    @allure.story("亿连空间-浏览器开关")
    def test_yl_space_website_switch(self, client: HttpClient):
        """获取浏览器开关及 APP 安装白名单。"""
        resp = client.post("/yl-space.json", json={
            "context": {
                "action_name": "website_switch",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "data" in data["context"], "缺少 data（签名）"
            assert "list" in data["context"], "缺少 list（base64 数据）"

    @allure.story("亿连空间-浏览器热词")
    def test_yl_space_website_hot(self, client: HttpClient):
        """获取浏览器热词。"""
        resp = client.post("/yl-space.json", json={
            "context": {
                "action_name": "website_hot",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("list"):
            item = data["context"]["list"][0]
            assert "hot_name" in item, "热词缺少 hot_name"
            assert "hot_url" in item, "热词缺少 hot_url"


@allure.feature("平行世界模块")
class TestYLSpaceStandard:
    """接口44: POST /yl-space-standard.json - 亿连空间标准版。"""

    @allure.story("亿连空间标准版-浏览器开关")
    @allure.severity(allure.severity_level.NORMAL)
    def test_yl_space_standard_website_switch(self, client: HttpClient):
        """获取标准版浏览器开关及白名单。"""
        resp = client.post("/yl-space-standard.json", json={
            "context": {
                "action_name": "website_switch",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "data" in data["context"], "缺少 data"
            assert "list" in data["context"], "缺少 list"

    @allure.story("亿连空间标准版-应用推荐")
    def test_yl_space_standard_recommend_app(self, client: HttpClient):
        """获取标准版应用推荐。"""
        resp = client.post("/yl-space-standard.json", json={
            "context": {
                "action_name": "recommend_app",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("recommend_list"):
            item = data["context"]["recommend_list"][0]
            for field in ("app_name", "package_name", "icon_path"):
                assert field in item, f"推荐应用缺少字段: {field}"

    @allure.story("亿连空间标准版-分类首页")
    def test_yl_space_standard_category_index(self, client: HttpClient):
        """获取标准版推荐分类首页。"""
        resp = client.post("/yl-space-standard.json", json={
            "context": {
                "action_name": "category_app_index",
            }
        })
        assert_status(resp, 200)

    @allure.story("亿连空间标准版-分类分页")
    def test_yl_space_standard_category_page(self, client: HttpClient):
        """标准版推荐分类分页。"""
        resp = client.post("/yl-space-standard.json", json={
            "context": {
                "action_name": "category_app_page",
                "data": {
                    "page": 1,
                    "software_category": "6",
                }
            }
        })
        assert_status(resp, 200)
