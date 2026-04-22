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
def _session_token() -> str:
    """整个测试会话只登录一次，并通过本地文件跨会话复用 token。

    读取 .cache/session_token.json：phone 一致、TTL 未过期、服务端校验通过时直接复用，
    从而避免每次运行都触发 login，绕开服务端对 13986903203 的登录频率限制（3001）。

    autouse：必须在所有 TestLogin 类的失败用例累积服务端限流计数之前先把 token 锁定，
    否则 authed 用例首次触发 fixture 时会撞上 3001「过度中断」。
    """
    cached = _load_cached_token()
    if cached:
        return cached
    c = HttpClient()
    token = login(c)
    _save_cached_token(token)
    return token


@pytest.fixture(scope="function")
def authed_client(_session_token) -> HttpClient:
    """带 token 的客户端，token 全会话复用。

    注意：不要在此 client 上调用会销毁 token 的接口（如 /logout），
    会破坏其它用例。销毁类用例请使用 fresh_authed_client。
    """
    c = HttpClient()
    c.set_token(_session_token)
    return c


@pytest.fixture(scope="function")
def fresh_authed_client() -> HttpClient:
    """独立登录的客户端，每条用例重新登录，不与其它用例共享 token。

    适用于会破坏 token 的接口（logout、release-3rd 等），避免污染 session token。
    注意：频繁使用会被服务端限流。
    """
    c = HttpClient()
    login(c)
    return c


@pytest.fixture(scope="function")
def fresh_token(client) -> str:
    """每次获取最新 token 并设置到 client。"""
    return login(client)
