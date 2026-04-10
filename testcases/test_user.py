"""用户模块接口测试 - 覆盖接口 3,6,7,20。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key
from core.extractor import extract_jsonpath


@allure.feature("用户模块")
class TestUserRescueInfo:
    """接口3: POST /user-rescue-info.json - 用户救援信息（需要 X-TOKEN）。"""

    @allure.story("救援信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_get_rescue_info(self, authed_client: HttpClient):
        """获取用户救援信息。"""
        resp = authed_client.post("/user-rescue-info.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("救援信息")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_rescue_info(self, authed_client: HttpClient):
        """编辑用户救援信息。"""
        resp = authed_client.post("/user-rescue-info.json", json={
            "context": {
                "actions": "edit",
                "data": {
                    "true_name": "测试用户",
                    "tel_num": "13800138000",
                    "plate_num": "京A-TEST1",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("救援信息")
    def test_edit_rescue_info_then_get(self, authed_client: HttpClient):
        """编辑后再获取，验证数据一致。"""
        test_data = {
            "true_name": "接口测试",
            "tel_num": "13900139000",
            "plate_num": "沪B-AUTO1",
        }
        # 编辑
        authed_client.post("/user-rescue-info.json", json={
            "context": {
                "actions": "edit",
                "data": test_data,
            }
        })
        # 获取
        resp = authed_client.post("/user-rescue-info.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)
        rescue_info = extract_jsonpath(resp, "$.context.rescue_info")
        assert rescue_info is not None, "未返回救援信息"
        if rescue_info:
            info = rescue_info[0]
            assert info["true_name"] == test_data["true_name"], "姓名不一致"
            assert info["tel_num"] == test_data["tel_num"], "电话不一致"
            assert info["plate_num"] == test_data["plate_num"], "车牌不一致"

    @allure.story("救援信息")
    def test_get_rescue_info_response_fields(self, authed_client: HttpClient):
        """验证救援信息返回字段：true_name, tel_num, plate_num。"""
        resp = authed_client.post("/user-rescue-info.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("rescue_info"):
            info = data["context"]["rescue_info"][0]
            for field in ("true_name", "tel_num", "plate_num"):
                assert field in info, f"救援信息缺少字段: {field}"

    @allure.story("救援信息")
    def test_rescue_info_without_token(self, client: HttpClient):
        """未登录获取救援信息应失败。"""
        resp = client.post("/user-rescue-info.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0, "未登录不应成功获取救援信息"


@allure.feature("用户模块")
class TestUserExtraInfo:
    """接口6: POST /user-extra-info.json - 用户扩展信息（需要 X-TOKEN）。"""

    @allure.story("扩展信息")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_extra_info(self, authed_client: HttpClient):
        """获取用户扩展信息。"""
        resp = authed_client.post("/user-extra-info.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("扩展信息")
    def test_edit_extra_info(self, authed_client: HttpClient):
        """编辑用户扩展信息。"""
        resp = authed_client.post("/user-extra-info.json", json={
            "context": {
                "actions": "edit",
                "data": {
                    "extra_info": "自动化测试扩展信息",
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("扩展信息")
    def test_edit_then_get_extra_info(self, authed_client: HttpClient):
        """编辑后获取，验证扩展信息一致。"""
        test_info = "测试扩展数据_202604"
        authed_client.post("/user-extra-info.json", json={
            "context": {
                "actions": "edit",
                "data": {"extra_info": test_info}
            }
        })
        resp = authed_client.post("/user-extra-info.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)
        extra = extract_jsonpath(resp, "$.context.extra_info")
        assert extra == test_info, f"扩展信息不一致: 期望 {test_info}, 实际 {extra}"

    @allure.story("扩展信息")
    def test_extra_info_without_token(self, client: HttpClient):
        """未登录获取扩展信息应失败。"""
        resp = client.post("/user-extra-info.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0, "未登录不应成功获取扩展信息"


@allure.feature("用户模块")
class TestUserFavoriteAlbum:
    """接口7: POST /user-favorite-album.json - 用户收藏音乐专辑（需要 X-TOKEN）。"""

    @allure.story("专辑收藏")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_favorite_list(self, authed_client: HttpClient):
        """获取收藏列表。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "list",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑收藏")
    def test_favorite_list_fields(self, authed_client: HttpClient):
        """验证收藏列表条目字段。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {"actions": "list"}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data.get("context", {}).get("favorite_albums"):
            album = data["context"]["favorite_albums"][0]
            for field in ("id", "album_id", "source", "name", "cover",
                          "listen_num", "total_episode", "can_download"):
                assert field in album, f"收藏专辑缺少字段: {field}"

    @allure.story("专辑收藏")
    def test_favorite_add(self, authed_client: HttpClient):
        """添加收藏。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "add",
                "data": [
                    {"album_id": "23"},
                    {"album_id": "24"},
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑收藏")
    def test_favorite_add_single(self, authed_client: HttpClient):
        """添加单个收藏。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "add",
                "data": [{"album_id": "100"}]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑收藏")
    def test_favorite_add_missing_album_id(self, authed_client: HttpClient):
        """收藏缺少专辑 ID 应返回 1010。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "add",
                "data": [],
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010, f"期望 code=1010，实际 {data['code']}"

    @allure.story("专辑收藏")
    def test_favorite_delete(self, authed_client: HttpClient):
        """删除收藏。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "delete",
                "data": [
                    {"album_id": "23"},
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑收藏")
    def test_favorite_delete_multiple(self, authed_client: HttpClient):
        """批量删除收藏。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "delete",
                "data": [
                    {"album_id": "23"},
                    {"album_id": "24"},
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑收藏")
    def test_favorite_delete_missing_album_id(self, authed_client: HttpClient):
        """删除缺少专辑 ID 应返回 1010。"""
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "delete",
                "data": [],
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010

    @allure.story("专辑收藏")
    def test_favorite_add_then_list(self, authed_client: HttpClient):
        """添加收藏后查询列表验证。"""
        # 添加
        authed_client.post("/user-favorite-album.json", json={
            "context": {
                "actions": "add",
                "data": [{"album_id": "50"}]
            }
        })
        # 查询
        resp = authed_client.post("/user-favorite-album.json", json={
            "context": {"actions": "list"}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)


@allure.feature("用户模块")
class TestLogOff:
    """接口20: POST /log-off.json - 用户注销（需要 X-TOKEN）。"""

    @allure.story("用户注销")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_log_off(self, authed_client: HttpClient):
        """注销用户账号。"""
        resp = authed_client.post("/log-off.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("用户注销")
    def test_log_off_without_token(self, client: HttpClient):
        """未登录注销应失败。"""
        resp = client.post("/log-off.json", json={
            "context": {}
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0, "未登录不应成功注销"
