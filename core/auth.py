"""鉴权模块 - 登录获取 Token、Token 刷新。"""

import logging
from core.http_client import HttpClient
from core.extractor import extract_jsonpath
from config import USERNAME, PASSWORD

logger = logging.getLogger(__name__)


class AuthManager:
    """管理登录态和 Token 生命周期。"""

    def __init__(self, client: HttpClient):
        self.client = client
        self.token: str | None = None

    def login(self, username: str = None, password: str = None) -> str:
        """登录并返回 Token。

        默认使用 config 中的测试账号，也可传入自定义账号。
        """
        username = username or USERNAME
        password = password or PASSWORD

        resp = self.client.post("/auth/login", json={
            "username": username,
            "password": password,
        })
        assert resp.status_code == 200, (
            f"登录失败: {resp.status_code} {resp.text[:300]}"
        )

        # 从响应中提取 Token（根据实际接口调整 JSONPath）
        self.token = extract_jsonpath(resp, "$.data.token") or \
                     extract_jsonpath(resp, "$.token")

        if not self.token:
            raise ValueError(f"登录响应中未找到 token: {resp.json()}")

        # 设置到 client 的 headers 中
        self.client.set_token(self.token)
        logger.info(f"登录成功，用户: {username}")
        return self.token

    def refresh_token(self) -> str:
        """刷新 Token（根据实际接口调整）。"""
        resp = self.client.post("/auth/refresh")
        assert resp.status_code == 200, (
            f"Token 刷新失败: {resp.status_code} {resp.text[:300]}"
        )
        self.token = extract_jsonpath(resp, "$.data.token") or \
                     extract_jsonpath(resp, "$.token")
        self.client.set_token(self.token)
        logger.info("Token 刷新成功")
        return self.token

    def get_token(self) -> str:
        """获取当前 Token，如果没有则先登录。"""
        if not self.token:
            self.login()
        return self.token
