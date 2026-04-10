"""音频模块接口测试 - 覆盖接口 1,2,4,5,8,9,10,19。"""

import allure
import pytest
from core.http_client import HttpClient
from core.assert_helper import assert_status, assert_json_key, assert_json_list_not_empty
from core.extractor import extract_jsonpath


@allure.feature("音频模块")
class TestAudioInfos:
    """接口1: POST /audio-infos.json - 音频专辑下内容列表（分页）。"""

    @allure.story("音频内容列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_audio_infos_normal(self, client: HttpClient):
        """正常查询专辑下音频列表。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "source": "ximalaya",
                "album_id": 28,
                "page": 1,
                "sort": "desc",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("音频内容列表")
    def test_audio_infos_asc_sort(self, client: HttpClient):
        """按发布时间正序排列。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "album_id": 28,
                "page": 1,
                "sort": "asc",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("音频内容列表")
    def test_audio_infos_with_episode_id(self, client: HttpClient):
        """传入 episode_id 定位到所属页面。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "album_id": 28,
                "episode_id": 16662,
                "page": 1,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("音频内容列表")
    def test_audio_infos_page2(self, client: HttpClient):
        """翻页查询第2页。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "album_id": 28,
                "page": 2,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("音频内容列表")
    @pytest.mark.parametrize("source", ["ximalaya", "duotin", "kaola", "qingting"])
    def test_audio_infos_different_sources(self, client: HttpClient, source):
        """不同音源查询。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "source": source,
                "album_id": 28,
                "page": 1,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("音频内容列表")
    def test_audio_infos_empty_source(self, client: HttpClient):
        """source 为空时查询。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "source": "",
                "album_id": 28,
                "page": 1,
            }
        })
        assert_status(resp, 200)

    @allure.story("音频内容列表")
    def test_audio_infos_pagination_fields(self, client: HttpClient):
        """验证分页返回字段完整性（total, size, total_page, previous_page, next_page）。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "source": "ximalaya",
                "album_id": 28,
                "page": 1,
                "sort": "desc",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            pagination = data["context"]["pagination"]
            for field in ("total", "size", "total_page", "previous_page", "next_page"):
                assert field in pagination, f"分页缺少字段: {field}"

    @allure.story("音频内容列表")
    def test_audio_infos_item_fields(self, client: HttpClient):
        """验证音频条目返回字段完整性。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "source": "ximalaya",
                "album_id": 28,
                "page": 1,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("infos"):
            item = data["context"]["infos"][0]
            for field in ("id", "title", "play_url", "file_size", "duration", "can_download"):
                assert field in item, f"音频条目缺少字段: {field}"

    @allure.story("音频内容列表")
    def test_audio_infos_first_page_previous(self, client: HttpClient):
        """第一页 previous_page 应返回 -1 或 1。"""
        resp = client.post("/audio-infos.json", json={
            "context": {
                "album_id": 28,
                "page": 1,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            prev = data["context"]["pagination"].get("previous_page")
            assert prev is not None, "缺少 previous_page"


@allure.feature("音频模块")
class TestAudioAlbums:
    """接口2: POST /audio-albums.json - 音乐专辑搜索/列表/推荐。"""

    # --- 搜索 ---
    @allure.story("专辑搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_album_search(self, client: HttpClient):
        """关键字搜索专辑。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "search",
                "keyword": "头条",
                "source_name": "ximalaya",
                "current_page": 1,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑搜索")
    def test_album_search_all_sources(self, client: HttpClient):
        """不指定音源搜索（返回所有源数据）。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "search",
                "keyword": "音乐",
                "source_name": "",
                "current_page": 1,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑搜索")
    def test_album_search_empty_keyword(self, client: HttpClient):
        """空关键字搜索。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "search",
                "keyword": "",
                "current_page": 1,
            }
        })
        assert_status(resp, 200)

    @allure.story("专辑搜索")
    def test_album_search_page2(self, client: HttpClient):
        """搜索结果翻页。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "search",
                "keyword": "头条",
                "current_page": 2,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑搜索")
    def test_album_search_result_fields(self, client: HttpClient):
        """验证搜索结果专辑字段完整性。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "search",
                "keyword": "头条",
                "source_name": "ximalaya",
                "current_page": 1,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("albums"):
            album = data["context"]["albums"][0]
            for field in ("id", "name", "source", "cover", "total_episode",
                          "listen_num", "is_actived", "show_order", "can_download"):
                assert field in album, f"专辑缺少字段: {field}"

    @allure.story("专辑搜索")
    @pytest.mark.parametrize("source", ["ximalaya", "duotin", "kaola", "qingting"])
    def test_album_search_by_source(self, client: HttpClient, source):
        """按不同音源搜索。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "search",
                "keyword": "新闻",
                "source_name": source,
                "current_page": 1,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    # --- 列表 ---
    @allure.story("专辑列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_album_list(self, client: HttpClient):
        """按分类获取专辑列表。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "source": "ximalaya",
                "category_id": 34,
                "page": 1,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑列表")
    def test_album_list_page2(self, client: HttpClient):
        """专辑列表翻页。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "source": "ximalaya",
                "category_id": 34,
                "page": 2,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑列表")
    def test_album_list_has_order_id(self, client: HttpClient):
        """专辑列表返回 order_id 字段。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "source": "ximalaya",
                "category_id": 34,
                "page": 1,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("albums"):
            assert "order_id" in data["context"]["albums"][0], "专辑列表缺少 order_id"

    # --- 推荐 ---
    @allure.story("专辑推荐")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_album_recommend(self, client: HttpClient):
        """获取推荐专辑列表。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "recommend",
                "page": 1,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑推荐")
    def test_album_recommend_has_source_info(self, client: HttpClient):
        """推荐专辑应包含 source 和 source_name。"""
        resp = client.post("/audio-albums.json", json={
            "context": {
                "actions": "recommend",
                "page": 1,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("albums"):
            album = data["context"]["albums"][0]
            assert "source" in album, "推荐专辑缺少 source"
            assert "source_name" in album, "推荐专辑缺少 source_name"


@allure.feature("音频模块")
class TestAudioHotWord:
    """接口4: POST /audio-hot-word.json - 专辑搜索热词。"""

    @allure.story("搜索热词")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_get_hot_words(self, client: HttpClient):
        """获取搜索热词列表。"""
        resp = client.post("/audio-hot-word.json", json={"context": {}})
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("搜索热词")
    def test_hot_words_has_data(self, client: HttpClient):
        """验证热词列表返回非空。"""
        resp = client.post("/audio-hot-word.json", json={"context": {}})
        assert_status(resp, 200)
        hot_words = extract_jsonpath(resp, "$.context.hot_words")
        assert hot_words is not None, "hot_words 字段不存在"

    @allure.story("搜索热词")
    def test_hot_words_item_fields(self, client: HttpClient):
        """验证热词条目包含 id, hot_word, order_id。"""
        resp = client.post("/audio-hot-word.json", json={"context": {}})
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("hot_words"):
            item = data["context"]["hot_words"][0]
            for field in ("id", "hot_word", "order_id"):
                assert field in item, f"热词缺少字段: {field}"


@allure.feature("音频模块")
class TestAudioSectionAlbums:
    """接口5: POST /audio-section-albums.json - 下载分段歌曲列表。"""

    @allure.story("分段下载")
    @allure.severity(allure.severity_level.NORMAL)
    def test_section_albums_normal(self, client: HttpClient):
        """正常获取分段歌曲列表。"""
        resp = client.post("/audio-section-albums.json", json={
            "context": {
                "album_id": "43237",
                "offset": 0,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("分段下载")
    def test_section_albums_with_offset(self, client: HttpClient):
        """带 offset 分段查询。"""
        resp = client.post("/audio-section-albums.json", json={
            "context": {
                "album_id": "43237",
                "offset": 50,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("分段下载")
    def test_section_albums_response_structure(self, client: HttpClient):
        """验证分段列表返回 total_episode_num 和 list。"""
        resp = client.post("/audio-section-albums.json", json={
            "context": {
                "album_id": "43237",
                "offset": 0,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "total_episode_num" in data["context"], "缺少 total_episode_num"
            assert "list" in data["context"], "缺少 list"

    @allure.story("分段下载")
    def test_section_albums_item_fields(self, client: HttpClient):
        """验证分段歌曲条目字段。"""
        resp = client.post("/audio-section-albums.json", json={
            "context": {
                "album_id": "43237",
                "offset": 0,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("list"):
            item = data["context"]["list"][0]
            for field in ("id", "title", "play_url", "file_size", "duration"):
                assert field in item, f"歌曲条目缺少字段: {field}"


@allure.feature("音频模块")
class TestAudioRecommend:
    """接口8: POST /audio-recommend.json - 音乐专辑推荐列表。"""

    @allure.story("专辑推荐V2")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_recommend_home(self, client: HttpClient):
        """获取推荐首页数据。"""
        resp = client.post("/audio-recommend.json", json={
            "context": {
                "actions": "recommend",
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑推荐V2")
    def test_recommend_home_structure(self, client: HttpClient):
        """验证首页返回 list 和 tags 结构。"""
        resp = client.post("/audio-recommend.json", json={
            "context": {
                "actions": "recommend",
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            ctx = data["context"]
            assert "list" in ctx, "推荐首页缺少 list"
            assert "tags" in ctx, "推荐首页缺少 tags"
            assert "hot" in ctx["list"], "list 缺少 hot 推荐栏目"
            assert "normal" in ctx["list"], "list 缺少 normal 关联分类"

    @allure.story("专辑推荐V2")
    def test_recommend_more_rec_tab(self, client: HttpClient):
        """获取推荐栏目更多数据（tab=rec）。"""
        resp = client.post("/audio-recommend.json", json={
            "context": {
                "actions": "more",
                "data": {
                    "cate_id": 1,
                    "tab": "rec",
                    "current_page": 1,
                    "page_size": 5,
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑推荐V2")
    def test_recommend_more_normal_tab(self, client: HttpClient):
        """获取一般栏目更多数据（tab=normal）。"""
        resp = client.post("/audio-recommend.json", json={
            "context": {
                "actions": "more",
                "data": {
                    "cate_id": 1,
                    "tab": "normal",
                    "current_page": 1,
                    "page_size": 5,
                }
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("专辑推荐V2")
    def test_recommend_more_pagination(self, client: HttpClient):
        """更多数据翻页返回 total_page 和 page_size。"""
        resp = client.post("/audio-recommend.json", json={
            "context": {
                "actions": "more",
                "data": {
                    "cate_id": 1,
                    "tab": "rec",
                    "current_page": 1,
                    "page_size": 10,
                }
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "total_page" in data["context"], "缺少 total_page"
            assert "page_size" in data["context"], "缺少 page_size"


@allure.feature("音频模块")
class TestAudioSmartDownload:
    """接口9: POST /audio-smart-download.json - 音乐专辑智能下载。"""

    @allure.story("智能下载")
    @allure.severity(allure.severity_level.NORMAL)
    def test_smart_download(self, client: HttpClient):
        """批量智能下载请求。"""
        resp = client.post("/audio-smart-download.json", json={
            "context": {
                "list": [
                    {
                        "album_id": 1894,
                        "episode_id": 201514,
                        "sort": "desc",
                        "page_size": 5,
                    }
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("智能下载")
    def test_smart_download_without_episode(self, client: HttpClient):
        """episode_id 传 0 时的智能下载。"""
        resp = client.post("/audio-smart-download.json", json={
            "context": {
                "list": [
                    {
                        "album_id": 1894,
                        "episode_id": 0,
                        "sort": "desc",
                        "page_size": 5,
                    }
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("智能下载")
    def test_smart_download_multiple_albums(self, client: HttpClient):
        """批量多个专辑智能下载。"""
        resp = client.post("/audio-smart-download.json", json={
            "context": {
                "list": [
                    {"album_id": 1894, "episode_id": 201514, "sort": "desc", "page_size": 5},
                    {"album_id": 1895, "episode_id": 0, "sort": "asc", "page_size": 3},
                ]
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("智能下载")
    def test_smart_download_response_structure(self, client: HttpClient):
        """验证智能下载返回包含 album 和 tracks。"""
        resp = client.post("/audio-smart-download.json", json={
            "context": {
                "list": [
                    {"album_id": 1894, "episode_id": 201514, "sort": "desc", "page_size": 5}
                ]
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("list"):
            item = data["context"]["list"][0]
            assert "album" in item, "智能下载缺少 album"
            assert "tracks" in item, "智能下载缺少 tracks"


@allure.feature("音频模块")
class TestAudioTags:
    """接口10: POST /audio-tags.json - 音乐详情。"""

    @allure.story("音乐详情")
    @allure.severity(allure.severity_level.NORMAL)
    def test_audio_tags(self, client: HttpClient):
        """获取音乐分类详情。"""
        resp = client.post("/audio-tags.json", json={
            "context": {"id": 36}
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("音乐详情")
    def test_audio_tags_response_structure(self, client: HttpClient):
        """验证详情返回包含 data, total_page, page_size。"""
        resp = client.post("/audio-tags.json", json={
            "context": {"id": 36}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0:
            assert "data" in data["context"], "缺少 data"
            assert "total_page" in data["context"], "缺少 total_page"
            assert "page_size" in data["context"], "缺少 page_size"

    @allure.story("音乐详情")
    def test_audio_tags_item_fields(self, client: HttpClient):
        """验证详情数据项字段。"""
        resp = client.post("/audio-tags.json", json={
            "context": {"id": 36}
        })
        assert_status(resp, 200)
        data = resp.json()
        if data["code"] == 0 and data["context"].get("data"):
            item = data["context"]["data"][0]
            for field in ("id", "source", "category_id", "name", "cover",
                          "listen_num", "is_actived", "total_episode",
                          "show_order", "source_name", "can_download"):
                assert field in item, f"详情缺少字段: {field}"

    @allure.story("音乐详情")
    def test_audio_tags_invalid_id(self, client: HttpClient):
        """无效 ID 查询。"""
        resp = client.post("/audio-tags.json", json={
            "context": {"id": 999999}
        })
        assert_status(resp, 200)


@allure.feature("音频模块")
class TestAudioRecord:
    """接口19: POST /audio-record.json - 喜马拉雅播放回传。"""

    @allure.story("播放回传")
    @allure.severity(allure.severity_level.NORMAL)
    def test_audio_record_normal(self, client: HttpClient):
        """正常上报播放记录。"""
        resp = client.post("/audio-record.json", json={
            "context": {
                "device_id": "866479028246931",
                "track_id": 222,
                "played_secs": 800.1,
                "duration": 222.00,
                "started_at": 1567567800000,
            }
        })
        assert_status(resp, 200)
        assert_json_key(resp, "code", 0)

    @allure.story("播放回传")
    def test_audio_record_missing_device_id(self, client: HttpClient):
        """缺少 device_id 应返回错误码 1010。"""
        resp = client.post("/audio-record.json", json={
            "context": {
                "track_id": 222,
                "played_secs": 800.1,
                "duration": 222.00,
                "started_at": 1567567800000,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010, f"缺少必填字段应返回 1010，实际 {data['code']}"

    @allure.story("播放回传")
    def test_audio_record_missing_track_id(self, client: HttpClient):
        """缺少 track_id 应返回错误码 1010。"""
        resp = client.post("/audio-record.json", json={
            "context": {
                "device_id": "866479028246931",
                "played_secs": 800.1,
                "duration": 222.00,
                "started_at": 1567567800000,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] == 1010

    @allure.story("播放回传")
    def test_audio_record_missing_played_secs(self, client: HttpClient):
        """缺少 played_secs 应返回错误码。"""
        resp = client.post("/audio-record.json", json={
            "context": {
                "device_id": "866479028246931",
                "track_id": 222,
                "duration": 222.00,
                "started_at": 1567567800000,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0, "缺少 played_secs 应返回错误"

    @allure.story("播放回传")
    def test_audio_record_missing_duration(self, client: HttpClient):
        """缺少 duration 应返回错误码。"""
        resp = client.post("/audio-record.json", json={
            "context": {
                "device_id": "866479028246931",
                "track_id": 222,
                "played_secs": 800.1,
                "started_at": 1567567800000,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0, "缺少 duration 应返回错误"

    @allure.story("播放回传")
    def test_audio_record_missing_started_at(self, client: HttpClient):
        """缺少 started_at 应返回错误码。"""
        resp = client.post("/audio-record.json", json={
            "context": {
                "device_id": "866479028246931",
                "track_id": 222,
                "played_secs": 800.1,
                "duration": 222.00,
            }
        })
        assert_status(resp, 200)
        data = resp.json()
        assert data["code"] != 0, "缺少 started_at 应返回错误"
