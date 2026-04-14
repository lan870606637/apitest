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


@pytest.fixture(scope="function")
def authed_client() -> HttpClient:
    """带 token 的客户端（每条用例重新登录获取最新 token）。"""
    c = HttpClient()
    login(c)
    return c


@pytest.fixture(scope="function")
def fresh_token(client) -> str:
    """每次获取最新 token 并设置到 client。"""
    token = login(client)
    return token
