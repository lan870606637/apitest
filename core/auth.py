"""鉴权模块 - 登录获取 Token。

每次调用 login() 都会重新获取最新 token，token 作为公共参数自动注入到 HttpClient。
"""

import logging
from core.http_client import HttpClient
from config import TEST_PHONE, TEST_SMS_PASSWORD

logger = logging.getLogger(__name__)


def login(client: HttpClient, phone_num: str = None, sms_password: str = None,
          login_type: str = "PHONE") -> str:
    """手机号+短信密码登录，返回 token。

    Args:
        client: HttpClient 实例
        phone_num: 手机号，默认从配置读取
        sms_password: 短信密码，默认从配置读取
        login_type: 登录方式，默认 PHONE

    Returns:
        token 字符串
    """
    phone_num = phone_num or TEST_PHONE
    sms_password = sms_password or TEST_SMS_PASSWORD

    context = {
        "login_type": login_type,
        "phone_num": phone_num,
        "sms_password": sms_password,
    }

    resp = client.post("login", context=context)
    data = resp.json()
    code = int(data.get("code", -1))

    assert code == 0, f"登录失败: code={code}, message={data.get('message')}"

    token = data["context"]["token"]
    client.set_token(token)
    logger.info(f"登录成功, phone={phone_num}, token={token[:8]}...")
    return token
