"""HTTP 客户端封装 - 统一请求入口，自动注入 headers、日志、重试。"""

import logging
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from config import BASE_URL, TIMEOUT, RETRY_COUNT

logger = logging.getLogger(__name__)


class HttpClient:
    """基于 requests.Session 的封装，提供统一的请求方法。"""

    def __init__(self, base_url: str = BASE_URL, timeout: int = TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        # 配置重试策略
        retry = Retry(
            total=RETRY_COUNT,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def set_token(self, token: str):
        """设置 Authorization 头。"""
        self.session.headers["Authorization"] = f"Bearer {token}"

    def _build_url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _log_request(self, method: str, url: str, **kwargs):
        logger.debug(f">>> {method} {url}")
        if "json" in kwargs:
            logger.debug(f"    Body: {kwargs['json']}")
        if "params" in kwargs:
            logger.debug(f"    Params: {kwargs['params']}")

    def _log_response(self, resp: requests.Response):
        logger.debug(f"<<< {resp.status_code} ({resp.elapsed.total_seconds():.3f}s)")
        try:
            logger.debug(f"    Response: {resp.json()}")
        except ValueError:
            logger.debug(f"    Response: {resp.text[:500]}")

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """发送请求的统一入口。"""
        url = self._build_url(path)
        kwargs.setdefault("timeout", self.timeout)
        self._log_request(method, url, **kwargs)
        resp = self.session.request(method, url, **kwargs)
        self._log_response(resp)
        return resp

    def get(self, path: str, params: dict = None, **kwargs) -> requests.Response:
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: dict = None, **kwargs) -> requests.Response:
        return self.request("POST", path, json=json, **kwargs)

    def put(self, path: str, json: dict = None, **kwargs) -> requests.Response:
        return self.request("PUT", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
