"""全局 Fixture - 提供 HTTP 客户端、登录态等共享资源。"""

import json
import logging
import os
import time
from pathlib import Path

import pytest
from config import LOG_CONFIG, TEST_PHONE
from core.http_client import HttpClient
from core.auth import login


_TOKEN_CACHE_FILE = Path(__file__).resolve().parent.parent / ".cache" / "session_token.json"
_TOKEN_CACHE_TTL = 6 * 3600  # 6 小时


def _load_cached_token() -> str | None:
    """从本地缓存读取 session token；phone 不匹配、TTL 过期、服务端校验失败时返回 None。"""
    try:
        data = json.loads(_TOKEN_CACHE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if data.get("phone") != TEST_PHONE:
        return None
    if time.time() - data.get("created_at", 0) > _TOKEN_CACHE_TTL:
        return None
    token = data.get("token")
    if not token or not _verify_token(token):
        return None
    return token


def _save_cached_token(token: str) -> None:
    _TOKEN_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _TOKEN_CACHE_FILE.write_text(
        json.dumps({"token": token, "phone": TEST_PHONE, "created_at": time.time()},
                   ensure_ascii=False),
        encoding="utf-8",
    )


def _verify_token(token: str) -> bool:
    """用一次轻量的 user-info 请求校验 token 是否仍有效。"""
    try:
        c = HttpClient()
        c.set_token(token)
        resp = c.post("user-info", context={})
        return int(resp.json().get("code", -1)) == 0
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    """把"会作废 session token"的用例挪到整个 session 最尾。

    使用 fresh_authed_client（logout / 破坏性登录类用例）的独立 login 会把共享 token
    作废。跨文件 alphabetical 下 test_api_v3_plain.py::TestLogout 会在 V4 之前跑，
    之后所有 authed_client 用例都会 1015。这里按 fixturenames 识别并推到最后。
    """
    def _is_destructive(item) -> bool:
        return "fresh_authed_client" in getattr(item, "fixturenames", ())
    items.sort(key=_is_destructive)  # False < True → 破坏性用例排到最后


def pytest_configure(config):
    """pytest 启动时配置日志。"""
    log_file = LOG_CONFIG.get("file", "reports/test.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG.get("level", "DEBUG")),
        format=LOG_CONFIG.get("format", "%(asctime)s [%(levelname)s] %(message)s"),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


@pytest.fixture(scope="session")
def client() -> HttpClient:
    """全局 HTTP 客户端（未登录状态，整个会话共享）。"""
    return HttpClient()


@pytest.fixture(scope="session", autouse=True)
def _session_token() -> dict:
    """整个测试会话只登录一次，并通过本地文件跨会话复用 token。

    返回可变 dict（而非 str）：服务端"同手机号单 token 激活"，任何用例里再次
    login 本号都会把此前 token 作废；这些用例需把新 token 塞回 _session_token["token"]，
    后续 authed_client 下次读取就能无感续上。

    读取 .cache/session_token.json：phone 一致、TTL 未过期、服务端校验通过时直接复用，
    避免每次运行都触发 login，绕开服务端对真实号码的登录频率限制（3001）。

    autouse：必须在所有 TestLogin 失败用例累积服务端限流计数之前先把 token 锁定。
    """
    cached = _load_cached_token()
    if cached:
        return {"token": cached}
    c = HttpClient()
    token = login(c)
    _save_cached_token(token)
    return {"token": token}


def _refresh_session_token(holder: dict, new_token: str) -> None:
    """被 TestLogin.test_login_success 等用例调用，更新共享 token 并持久化。"""
    holder["token"] = new_token
    _save_cached_token(new_token)


@pytest.fixture(scope="function")
def authed_client(_session_token) -> HttpClient:
    """带 token 的客户端，token 全会话复用。

    注意：不要在此 client 上调用会销毁 token 的接口（如 /logout），
    会破坏其它用例。销毁类用例请使用 fresh_authed_client。
    """
    c = HttpClient()
    c.set_token(_session_token["token"])
    return c


@pytest.fixture(scope="function")
def fresh_authed_client() -> HttpClient:
    """独立登录的客户端，每条用例重新登录，不与其它用例共享 token。

    适用于会破坏 token 的接口（logout、release-3rd 等），避免污染 session token。

    服务端"同手机号单 token 激活"：此次独立 login 会把 _session_token holder 里的
    旧 token 作废，后续 authed_client 会 1015。解决方式不是 teardown 补登（会撞
    3001 IP 限流），而是通过 pytest_collection_modifyitems 把使用本 fixture 的
    用例重排到整个 session 最后，让它在所有共享 token 的用例跑完后再作废。
    """
    c = HttpClient()
    login(c)
    return c


@pytest.fixture(scope="function")
def fresh_token(client) -> str:
    """每次获取最新 token 并设置到 client。"""
    return login(client)


# ==================== 多版本客户端 ====================
# V3.3.3 / V4.0 新接口的路由版本与 config.yaml 默认 V3.0 不同，
# 通过 HttpClient(api_version=...) 参数覆盖，复用同一套签名/加密管道。

@pytest.fixture(scope="session")
def client_v3_3_3() -> HttpClient:
    return HttpClient(api_version="v3.3.3")


@pytest.fixture(scope="function")
def authed_client_v3_3_3(_session_token) -> HttpClient:
    c = HttpClient(api_version="v3.3.3")
    c.set_token(_session_token["token"])
    return c


@pytest.fixture(scope="session")
def client_v4() -> HttpClient:
    return HttpClient(api_version="v4.0")


@pytest.fixture(scope="function")
def authed_client_v4(_session_token) -> HttpClient:
    c = HttpClient(api_version="v4.0")
    c.set_token(_session_token["token"])
    return c
