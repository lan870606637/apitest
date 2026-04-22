"""全局 Fixture - 提供 HTTP 客户端、登录态等共享资源。"""

import logging
import os
import pytest
from config import LOG_CONFIG
from core.http_client import HttpClient
from core.auth import login


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


@pytest.fixture(scope="session")
def _session_token() -> str:
    """整个测试会话只登录一次，复用同一个 token，避免服务端短信/登录限流。"""
    c = HttpClient()
    return login(c)


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
