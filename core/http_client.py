"""HTTP 客户端封装 - 适配亿驾 V3.0 接口规范。

自动注入 X-SIGN、X-DEVICE、X-CLIENT、X-BIZ、X-TOKEN headers。
Request Body 通过内网工具自动加密后发送。
"""

import json
import logging
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from config import (
    BASE_URL, API_VERSION, TIMEOUT, RETRY_COUNT,
    APP_KEY, IMEI, X_DEVICE_ENCRYPTED, X_CLIENT_ENCRYPTED, BIZ,
    X_APPKEY,
)
from core.sign import generate_sign, encrypt_data

logger = logging.getLogger(__name__)


class HttpClient:
    """亿驾 V3.0 接口 HTTP 客户端。"""

    def __init__(self, base_url: str = BASE_URL, api_version: str = API_VERSION,
                 timeout: int = TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.timeout = timeout
        self.token: str = ""  # 未登录时为空
        self.session = requests.Session()

        # 配置重试策略
        retry = Retry(
            total=RETRY_COUNT,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def set_token(self, token: str):
        """设置登录 token。"""
        self.token = token

    def _build_url(self, api_name: str) -> str:
        """构建完整的请求 URL。"""
        return f"{self.base_url}/{self.api_version}/{api_name}.json"

    def _build_uri(self, api_name: str) -> str:
        """构建 URI（用于签名）。"""
        return f"/{self.api_version}/{api_name}.json"

    def _build_headers(self, api_name: str) -> dict:
        """构建请求头，包含所有公共 header。"""
        uri = self._build_uri(api_name)
        x_sign = generate_sign(
            token=self.token,
            imei=IMEI,
            app_key=APP_KEY,
            uri=uri,
        )

        headers = {
            "X-SIGN": x_sign,
            "X-BIZ": BIZ,
            "X-DEVICE": X_DEVICE_ENCRYPTED,
            "X-CLIENT": X_CLIENT_ENCRYPTED,
            "X-APPKEY": X_APPKEY,
        }

        if self.token:
            headers["X-TOKEN"] = self.token

        return headers

    def _log_request(self, url: str, headers: dict, body_plain: dict):
        logger.debug(f">>> POST {url}")
        logger.debug(f"    X-SIGN={headers.get('X-SIGN')}, X-BIZ={headers.get('X-BIZ')}, X-TOKEN={headers.get('X-TOKEN', '(empty)')}")
        logger.debug(f"    Body(plain): {json.dumps(body_plain, ensure_ascii=False)[:500]}")

    def _log_response(self, resp: requests.Response):
        logger.debug(f"<<< {resp.status_code} ({resp.elapsed.total_seconds():.3f}s)")
        try:
            logger.debug(f"    Response: {json.dumps(resp.json(), ensure_ascii=False)[:500]}")
        except ValueError:
            logger.debug(f"    Response: {resp.text[:500]}")

    def post(self, api_name: str, context: dict = None, extra_headers: dict = None) -> requests.Response:
        """发送 POST 请求（V3.0 接口只支持 POST）。

        Body 会自动加密后以密文形式发送。

        Args:
            api_name: 接口名称，如 "login"、"check-for-updates"
            context: 请求体中的 context 内容
            extra_headers: 额外的自定义 headers

        Returns:
            requests.Response 响应对象
        """
        url = self._build_url(api_name)
        headers = self._build_headers(api_name)
        if extra_headers:
            headers.update(extra_headers)

        # 构建明文 body：服务端要求 body 必须包含 context 键，None 时使用空对象
        body = {"context": context if context is not None else {}}

        self._log_request(url, headers, body)

        # 加密 body
        body_json = json.dumps(body, ensure_ascii=False)
        encrypted_body = encrypt_data(body_json)

        # 发送加密后的密文作为 body（非 JSON 格式）
        resp = self.session.post(
            url,
            data=encrypted_body,
            headers=headers,
            timeout=self.timeout,
            proxies={"http": None, "https": None},
        )
        self._log_response(resp)
        return resp
