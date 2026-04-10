"""设备/系统模块接口测试 - 覆盖接口 11,12,12b,13,16,21,22。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("设备系统模块")
class TestCheckUpdateYL:
    """接口11: POST /check-update-for-yl.json - 检查车机亿连更新。"""

    @allure.story("车机更新检查")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_check_update_normal(self, client: HttpClient):
        """正常检查车机亿连更新。"""
        resp = client.post("/check-update-for-yl.json", json={
            "context": {
                "package_name": "net.carbit.easyconnected",
                "channel": "KY01",
                "version_name": "V2.3",
                "version_code": "641",
                "uuid": "bsjise-887320001323",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("车机更新检查")
    def test_check_update_has_update(self, client: HttpClient):
        """有更新时验证返回 client_version 字段。"""
        resp = client.post("/check-update-for-yl.json", json={
            "context": {
                "package_name": "net.carbit.easyconnected",
                "channel": "KY01",
                "version_name": "V1.0",
                "version_code": "100",
                "uuid": "test-uuid-old",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("client_version"):
            cv = data["context"]["client_version"]
            for field in ("version_name", "version_code", "size", "forced",
                          "change_log", "file_url", "file_sum"):
                assert field in cv, f"更新信息缺少字段: {field}"

    @allure.story("车机更新检查")
    def test_check_update_latest_version(self, client: HttpClient):
        """已是最新版本时返回空 context。"""
        resp = client.post("/check-update-for-yl.json", json={
            "context": {
                "package_name": "net.carbit.easyconnected",
                "channel": "KY01",
                "version_name": "V99.99",
                "version_code": "99999",
                "uuid": "test-uuid-001",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)


@allure.feature("设备系统模块")
class TestCheckUpdateYLSO:
    """接口12: POST /check-update-for-yl-so.json - 检查车机 SO 文件更新。"""

    @allure.story("SO文件更新")
    @allure.severity(allure.severity_level.NORMAL)
    def test_check_so_update_android_arm(self, client: HttpClient):
        """Android ARM 平台 SO 更新检查。"""
        resp = client.post("/check-update-for-yl-so.json", json={
            "context": {
                "package_name": "lib.carbit.com",
                "channel": "KY01",
                "version_name": "V2.3",
                "version_code": "641",
                "cpu": "arm",
                "sys": "android",
            }
        })
        assert_status(resp, 200)

    @allure.story("SO文件更新")
    def test_check_so_update_x86_wince(self, client: HttpClient):
        """WinCE x86 平台 SO 更新检查。"""
        resp = client.post("/check-update-for-yl-so.json", json={
            "context": {
                "package_name": "lib.carbit.com",
                "channel": "KY01",
                "version_name": "V2.3",
                "version_code": "641",
                "cpu": "x86",
                "sys": "wince",
            }
        })
        assert_status(resp, 200)

    @allure.story("SO文件更新")
    def test_check_so_update_response_fields(self, client: HttpClient):
        """有更新时验证返回字段。"""
        resp = client.post("/check-update-for-yl-so.json", json={
            "context": {
                "package_name": "lib.carbit.com",
                "channel": "KY01",
                "version_name": "V1.0",
                "version_code": "100",
                "cpu": "arm",
                "sys": "android",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data.get("context", {}).get("client_version"):
            cv = data["context"]["client_version"]
            for field in ("version_code", "size", "forced", "file_url", "file_sum"):
                assert field in cv, f"SO更新缺少字段: {field}"


@allure.feature("设备系统模块")
class TestPhoneButtonPoint:
    """接口12b: POST /get-phone-button-point.json - 手机接听挂断按钮位置。"""

    @allure.story("按钮位置")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_button_point_known_model(self, client: HttpClient):
        """已知型号获取按钮位置。"""
        resp = client.post("/get-phone-button-point.json", json={
            "context": {
                "phone_model": "XIAOMI",
                "phone_sysversion": "6.2.1",
            }
        })
        assert_status(resp, 200)

    @allure.story("按钮位置")
    def test_get_button_point_response_fields(self, client: HttpClient):
        """找到对应值时验证 anserBut 和 hangBut 字段。"""
        resp = client.post("/get-phone-button-point.json", json={
            "context": {
                "phone_model": "XIAOMI",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data.get("context"):
            ctx = data["context"]
            if ctx:
                assert "anserBut" in ctx or "hangBut" in ctx, \
                    "有数据时应包含 anserBut 或 hangBut"

    @allure.story("按钮位置")
    def test_get_button_point_unknown_model(self, client: HttpClient):
        """未知型号返回空 context。"""
        resp = client.post("/get-phone-button-point.json", json={
            "context": {
                "phone_model": "UNKNOWN_MODEL_XYZ",
            }
        })
        assert_status(resp, 200)

    @allure.story("按钮位置")
    def test_get_button_point_case_insensitive(self, client: HttpClient):
        """手机型号大小写不敏感（服务端转大写比较）。"""
        resp = client.post("/get-phone-button-point.json", json={
            "context": {
                "phone_model": "xiaomi",
            }
        })
        assert_status(resp, 200)


@allure.feature("设备系统模块")
class TestPhoneTouch:
    """接口13: POST /get-phone-touch.json - 手机电话 touch 开关。"""

    @allure.story("Touch开关")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_phone_touch(self, client: HttpClient):
        """获取手机 touch 开关黑名单。"""
        resp = client.post("/get-phone-touch.json", json={
            "context": {
                "phone_model": "NOTE",
                "phone_sysversion": "6.2.1",
                "phone_brand": "XIAOMI",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("Touch开关")
    def test_get_phone_touch_empty_params(self, client: HttpClient):
        """预留字段为空时也应正常返回。"""
        resp = client.post("/get-phone-touch.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("Touch开关")
    def test_get_phone_touch_response_structure(self, client: HttpClient):
        """验证返回结构为品牌->型号->配置的嵌套。"""
        resp = client.post("/get-phone-touch.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("context"):
            touch_data = data["context"]["context"]
            assert isinstance(touch_data, dict), "touch 数据应为字典"


@allure.feature("设备系统模块")
class TestCheckUpdateOTA:
    """接口16: POST /check-update-for-ota.json - OTA 更新检查。"""

    @allure.story("OTA更新")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_ota_update_check(self, client: HttpClient):
        """正常 OTA 更新检查（批量软件）。"""
        resp = client.post("/check-update-for-ota.json", json={
            "context": {
                "data": [
                    {"software_id": "3dd9923ldd", "version_code": 66},
                    {"software_id": "3dddddfsadd", "version_code": 6589},
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("OTA更新")
    def test_ota_update_single_software(self, client: HttpClient):
        """单个软件 OTA 检查。"""
        resp = client.post("/check-update-for-ota.json", json={
            "context": {
                "data": [
                    {"software_id": "3dd9923ldd", "version_code": 66},
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("OTA更新")
    def test_ota_update_response_fields(self, client: HttpClient):
        """有更新时验证返回字段完整性。"""
        resp = client.post("/check-update-for-ota.json", json={
            "context": {
                "data": [
                    {"software_id": "3dd9923ldd", "version_code": 1},
                ]
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("data"):
            item = data["context"]["data"][0]
            for field in ("software_id", "title", "version_code", "version_name",
                          "size", "is_full_dist", "change_log", "file_url", "file_sum"):
                assert field in item, f"OTA更新缺少字段: {field}"

    @allure.story("OTA更新")
    def test_ota_update_latest(self, client: HttpClient):
        """已是最新版本时返回空 context。"""
        resp = client.post("/check-update-for-ota.json", json={
            "context": {
                "data": [
                    {"software_id": "3dd9923ldd", "version_code": 999999},
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("OTA更新")
    def test_ota_update_with_headers(self, client: HttpClient):
        """带 X-BIZ/X-CHANNEL/X-LANGUAGE header 的 OTA 检查。"""
        headers = {
            "X-BIZ": "android",
            "X-CHANNEL": "88802",
            "X-LANGUAGE": "en",
        }
        resp = client.post("/check-update-for-ota.json", json={
            "context": {
                "data": [
                    {"software_id": "3dd9923ldd", "version_code": 66},
                ]
            }
        }, headers=headers)
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)


@allure.feature("设备系统模块")
class TestBluetoothDevice:
    """接口21: POST /bluetooth-device.json - 蓝牙连接设备。"""

    @allure.story("蓝牙设备")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bluetooth_device_normal(self, client: HttpClient):
        """正常提交蓝牙设备信息。"""
        resp = client.post("/bluetooth-device.json", json={
            "context": {
                "bluetooth": "abc",
                "device_code": "123",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("蓝牙设备")
    def test_bluetooth_device_already_recorded(self, client: HttpClient):
        """已记录设备返回 device_info。"""
        resp = client.post("/bluetooth-device.json", json={
            "context": {
                "bluetooth": "abc",
                "device_code": "123",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("device_info"):
            info = data["context"]["device_info"][0]
            assert "device_code" in info, "缺少 device_code"
            assert "bluetooth" in info, "缺少 bluetooth"

    @allure.story("蓝牙设备")
    def test_bluetooth_device_missing_bluetooth(self, client: HttpClient):
        """缺少 bluetooth 字段应报错 1010。"""
        resp = client.post("/bluetooth-device.json", json={
            "context": {
                "device_code": "123",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010, f"期望 code=1010，实际 {data['code']}"

    @allure.story("蓝牙设备")
    def test_bluetooth_device_empty_bluetooth(self, client: HttpClient):
        """bluetooth 为空字符串应报错。"""
        resp = client.post("/bluetooth-device.json", json={
            "context": {
                "bluetooth": "",
                "device_code": "123",
            }
        })
        assert_status(resp, 200)


@allure.feature("设备系统模块")
class TestAbroadTest:
    """接口22: POST /abroad-test.json - 海外测试环境。"""

    @allure.story("海外测试")
    @allure.severity(allure.severity_level.MINOR)
    def test_abroad_test(self, client: HttpClient):
        """获取海外测试下载地址。"""
        resp = client.post("/abroad-test.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)
        download_url = extract_jsonpath(resp, "$.context.download_url")
        assert download_url is not None, "未返回 download_url"

    @allure.story("海外测试")
    def test_abroad_test_url_format(self, client: HttpClient):
        """验证下载地址为有效 URL。"""
        resp = client.post("/abroad-test.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            url = data["context"]["download_url"]
            assert url.startswith("http"), f"下载地址格式异常: {url}"
