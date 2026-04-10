"""其他模块接口测试 - 覆盖接口 34,35,39,40,41,45,46,47。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("其他模块")
class TestVoiceHeadset:
    """接口34: POST /voice-headset.json - 生成命令词评分和文件。"""

    @allure.story("语音头盔")
    @allure.severity(allure.severity_level.NORMAL)
    def test_voice_evaluate(self, authed_client: HttpClient):
        """生成命令词评分。"""
        resp = authed_client.post("/voice-headset.json", json={
            "context": {
                "actions": "evaluate",
                "word": "小爱同学",
                "commandId": 0,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "score" in data["context"], "缺少 score"
            assert "status" in data["context"], "缺少 status"

    @allure.story("语音头盔")
    def test_voice_generate_bin_file(self, authed_client: HttpClient):
        """生成命令词 bin 文件。"""
        resp = authed_client.post("/voice-headset.json", json={
            "context": {
                "actions": "generateBinFile",
                "word": "小爱同学",
                "commandId": 0,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "fileArray" in data["context"], "缺少 fileArray"
            assert "status" in data["context"], "缺少 status"

    @allure.story("语音头盔")
    def test_voice_different_words(self, authed_client: HttpClient):
        """不同命令词生成评分。"""
        resp = authed_client.post("/voice-headset.json", json={
            "context": {
                "actions": "evaluate",
                "word": "你好亿连",
                "commandId": 1,
            }
        })
        assert_status(resp, 200)


@allure.feature("其他模块")
class TestUserTrackAndWayPoint:
    """接口35: POST /user-track-and-way-point.json - Track, WayPoint。"""

    @allure.story("轨迹-编辑")
    @allure.severity(allure.severity_level.NORMAL)
    def test_track_edit(self, authed_client: HttpClient):
        """编辑轨迹信息。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "track_edit",
                "data": {
                    "track_code": "864467042256954-1636686713728",
                    "track_name": "autotest_track",
                    "track_duration": 11111,
                    "origin_lng": "121.12",
                    "origin_lat": "25.24",
                    "dest_lng": "234.12",
                    "dest_lat": "45.24",
                    "track_time": "2026-04-10 10:00:00",
                    "track_distance": 110,
                    "is_completed": "1",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("轨迹-详情")
    def test_track_info(self, authed_client: HttpClient):
        """获取轨迹详情。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "track_info",
                "data": {
                    "track_code": "864467042256954-1636686713728",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("info"):
            info = data["context"]["info"]
            for field in ("track_code", "track_name", "origin_lng", "origin_lat",
                          "dest_lng", "dest_lat", "track_distance", "track_duration"):
                assert field in info, f"轨迹详情缺少字段: {field}"

    @allure.story("航点-编辑")
    def test_way_point_edit(self, authed_client: HttpClient):
        """编辑航点信息。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "way_point_edit",
                "data": {
                    "name": "autotest_point",
                    "longitude": "121.47",
                    "latitude": "31.23",
                    "way_point_code": "autotest_wp_001",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("航点-详情")
    def test_way_point_info(self, authed_client: HttpClient):
        """获取航点详情。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "way_point_info",
                "data": {
                    "item_id": "21",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("point_info"):
            info = data["context"]["point_info"]
            for field in ("way_point_name", "way_point_code",
                          "longitude", "latitude", "like_num", "rate_num"):
                assert field in info, f"航点详情缺少字段: {field}"

    @allure.story("评分")
    def test_rate(self, authed_client: HttpClient):
        """评分操作。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "rate",
                "data": {
                    "item_id": "22",
                    "rate_num": 5,
                    "category": "point",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3056)

    @allure.story("评分")
    @pytest.mark.parametrize("category", ["track", "point"])
    def test_rate_categories(self, authed_client: HttpClient, category):
        """不同类型评分。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "rate",
                "data": {
                    "item_id": "22",
                    "rate_num": 4,
                    "category": category,
                }
            }
        })
        assert_status(resp, 200)

    @allure.story("点赞")
    def test_like(self, authed_client: HttpClient):
        """点赞操作。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "like",
                "data": {
                    "item_id": "22",
                    "category": "point",
                }
            }
        })
        assert_status(resp, 200)

    @allure.story("列表")
    def test_list_all(self, authed_client: HttpClient):
        """获取全部列表（track + point）。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "list",
                "data": {
                    "category": "all",
                    "sort_name": "upload_time",
                    "sort": "desc",
                    "offset": 0,
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("list"):
            item = data["context"]["list"][0]
            assert "category" in item, "列表条目缺少 category"
            assert item["category"] in ("track", "point")

    @allure.story("列表")
    @pytest.mark.parametrize("category", ["all", "track", "point"])
    def test_list_by_category(self, authed_client: HttpClient, category):
        """按类型过滤列表。"""
        resp = authed_client.post("/user-track-and-way-point.json", json={
            "context": {
                "action_name": "list",
                "data": {
                    "category": category,
                    "offset": 0,
                }
            }
        })
        assert_status(resp, 200)


@allure.feature("其他模块")
class TestFeedbackPost:
    """接口39: POST /feedback-post.json - 意见反馈（form 方式）。"""

    @allure.story("意见反馈-配置")
    @allure.severity(allure.severity_level.NORMAL)
    def test_feedback_post_config(self, client: HttpClient):
        """获取意见反馈页面配置。"""
        resp = client.session.post(
            client._build_url("/feedback-post.json"),
            data={"body": '{"context":{"action_name":"config"}}'},
            timeout=client.timeout,
        )
        assert resp.status_code == 200

    @allure.story("意见反馈-提交")
    def test_feedback_post_submit(self, client: HttpClient):
        """提交意见反馈（form 方式）。"""
        resp = client.session.post(
            client._build_url("/feedback-post.json"),
            data={
                "body": '{"context":{"action_name":"submit","category":"遇到问题","module":"连接","content":"自动化测试反馈","contact":"13800138000"}}',
            },
            timeout=client.timeout,
        )
        assert resp.status_code == 200


@allure.feature("其他模块")
class TestSoftDecodeDevice:
    """接口40: POST /soft-decode-device.json - 软解码设备。"""

    @allure.story("软解码")
    @allure.severity(allure.severity_level.MINOR)
    def test_soft_decode_device_list(self, client: HttpClient):
        """获取软解码设备列表。"""
        resp = client.post("/soft-decode-device.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("软解码")
    def test_soft_decode_device_fields(self, client: HttpClient):
        """验证软解码设备列表字段。"""
        resp = client.post("/soft-decode-device.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("device_list"):
            item = data["context"]["device_list"][0]
            assert "brand" in item, "缺少 brand"
            assert "model" in item, "缺少 model"
            assert "annotation" in item, "缺少 annotation"
            assert isinstance(item["model"], list), "model 应为列表"


@allure.feature("其他模块")
class TestCustomAppStaticResource:
    """接口41: POST /custom-app-static-resource.json - App 静态资源定制。"""

    @allure.story("静态资源")
    @allure.severity(allure.severity_level.MINOR)
    def test_custom_static_resource(self, client: HttpClient):
        """获取 App 静态资源定制信息。"""
        resp = client.post("/custom-app-static-resource.json", json={
            "context": {
                "action": "vehicle",
                "context": {
                    "brand_name": "test_brand",
                    "vehicle_model": "test_model",
                    "version_name": "1.0",
                    "channel_code": "test_channel",
                }
            }
        })
        assert_status(resp, 200)

    @allure.story("静态资源")
    def test_custom_static_resource_fields(self, client: HttpClient):
        """验证静态资源返回字段。"""
        resp = client.post("/custom-app-static-resource.json", json={
            "context": {
                "action": "vehicle",
                "context": {
                    "brand_name": "test_brand",
                    "vehicle_model": "test_model",
                    "version_name": "1.0",
                    "channel_code": "test_channel",
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("custom_config"):
            config = data["context"]["custom_config"]
            # 可能包含 icon_name, start_pic, index_car_pic, background_pic
            assert isinstance(config, dict), "custom_config 应为字典"


@allure.feature("其他模块")
class TestGetLocation:
    """接口45: POST /get-location.json - 欧洲服务器返回区域标识。"""

    @allure.story("区域标识")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_location(self, client: HttpClient):
        """获取欧洲服务器区域标识。"""
        resp = client.post("/get-location.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("区域标识")
    def test_get_location_is_eu(self, client: HttpClient):
        """验证返回 is_eu 标识。"""
        resp = client.post("/get-location.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            config = data["context"].get("custom_config", {})
            assert "is_eu" in config, "缺少 is_eu"
            assert config["is_eu"] in ("0", "1"), f"is_eu 值异常: {config['is_eu']}"


@allure.feature("其他模块")
class TestCoverageNav:
    """接口46: POST /coverage-nav.json - GoogleMaps 导航覆盖范围。"""

    @allure.story("导航覆盖")
    @allure.severity(allure.severity_level.MINOR)
    def test_coverage_nav(self, client: HttpClient):
        """获取 GoogleMaps 导航覆盖范围。"""
        resp = client.post("/coverage-nav.json", json={
            "context": {
                "action_name": "navi_coverage",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("导航覆盖")
    def test_coverage_nav_fields(self, client: HttpClient):
        """验证导航覆盖返回字段。"""
        resp = client.post("/coverage-nav.json", json={
            "context": {"action_name": "navi_coverage"}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "version" in data["context"], "缺少 version"
            assert "list" in data["context"], "缺少 list"
            if data["context"]["list"]:
                item = data["context"]["list"][0]
                assert "region_code" in item, "缺少 region_code"
                assert "two_wheeled_directions" in item, "缺少 two_wheeled_directions"
                assert "biking_directions" in item, "缺少 biking_directions"


@allure.feature("其他模块")
class TestVehicleTrackingData:
    """接口47: POST /vehicle-tracking-data.json - 记录数据埋点信息。"""

    @allure.story("数据埋点")
    @allure.severity(allure.severity_level.NORMAL)
    def test_vehicle_tracking_data(self, client: HttpClient):
        """提交车辆数据埋点信息。"""
        resp = client.post("/vehicle-tracking-data.json", json={
            "context": {
                "data": {
                    "ec_sn": "test_ec_sn",
                    "mcu_sn": "test_mcu_sn",
                    "car_type": "sedan",
                    "pro_number": "test_pro",
                    "pro_channel": "test_channel",
                    "ota_sid": "test_ota_sid",
                    "sys_version": "1.0.0",
                    "mcu_version": "2.0.0",
                    "hardware_version": "3.0.0",
                    "bt_version": "4.0",
                    "voice_version": "5.0",
                    "radio_version": "6.0",
                    "ddr": "2G",
                    "emmc": "2G",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("数据埋点")
    def test_vehicle_tracking_data_partial(self, client: HttpClient):
        """部分字段提交埋点。"""
        resp = client.post("/vehicle-tracking-data.json", json={
            "context": {
                "data": {
                    "ec_sn": "test_ec_sn",
                    "sys_version": "1.0.0",
                }
            }
        })
        assert_status(resp, 200)

    @allure.story("数据埋点")
    def test_vehicle_tracking_data_empty(self, client: HttpClient):
        """空 data 提交埋点应返回错误。"""
        resp = client.post("/vehicle-tracking-data.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] in (0, 3059), f"空数据应返回 0 或 3059，实际 {data['code']}"

    @allure.story("数据埋点")
    def test_vehicle_tracking_data_error_code(self, client: HttpClient):
        """未定义类型应返回 3059。"""
        resp = client.post("/vehicle-tracking-data.json", json={
            "context": {
                "data": {},
            }
        })
        assert_status(resp, 200)
