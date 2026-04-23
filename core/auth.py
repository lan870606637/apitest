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

    通用验证码并非"免短信直登"——服务端要求先 /send-sms-password 建立 SMS 会话，
    再在窗口内用通用码 /login。直接登录会返回 3003「短信密码已失效」。
    send-sms 返回 3002（当日配额已满）属合法业务状态，不阻断登录；其它错误码
    仅记录日志，不提前 assert，让真正的失败暴露在 /login 的返回上。

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

    sms_resp = client.post("send-sms-password", context={"phone_num": phone_num})
    sms_code = int(sms_resp.json().get("code", -1))
    if sms_code not in (0, 3002):
        logger.warning(f"send-sms-password 返回异常 code={sms_code}, 继续尝试登录")

    resp = client.post("login", context={
        "login_type": login_type,
        "phone_num": phone_num,
        "sms_password": sms_password,
    })
    data = resp.json()
    code = int(data.get("code", -1))

    assert code == 0, f"登录失败: code={code}, message={data.get('message')}"

    token = data["context"]["token"]
    client.set_token(token)
    logger.info(f"登录成功, phone={phone_num}, token={token[:8]}...")
    return token
