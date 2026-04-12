"""全局 Fixture - 提供 HTTP 客户端、公共 headers 等共享资源。"""

import logging
import os
import pytest
from config import LOG_CONFIG
from core.http_client import HttpClient


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
    """全局 HTTP 客户端（整个测试会话共享）。

    亿驾接口使用 POST + JSON body，鉴权通过 X-TOKEN header 传递。
    """
    c = HttpClient()
    # 亿驾接口通过 X-BIZ / X-CHANNEL / X-LANGUAGE 等 header 传递公共参数
    c.session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    return c


@pytest.fixture(scope="session")
def authed_client(client) -> HttpClient:
    """带 X-TOKEN 的客户端（用于需要登录的接口）。

    注意：需要先获取有效 Token，此处使用占位值，
    实际使用时替换为真实 Token 或通过登录接口获取。
    """
    import os
    token = os.getenv("API_TOKEN", "")
    if token:
        client.session.headers["X-TOKEN"] = token
    else:
        pytest.skip("未配置 API_TOKEN，跳过需要鉴权的用例")
    return client
