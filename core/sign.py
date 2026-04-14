"""签名和加密模块 - 支持内网工具和本地 MD5 两种签名方式。

加密工具地址: http://datatools.carbit.lo
- encode.php: 加密/解密
- createsign3.php: 生成 X-SIGN
- createtimestamp.php: 生成时间戳

本地签名逻辑: MD5(token + imei + appkey + uri + timestamp)
"""

import hashlib
import time
import logging
import requests

logger = logging.getLogger(__name__)

# 内网加密工具地址
TOOL_BASE_URL = "http://datatools.carbit.lo"


def md5_encrypt(text: str) -> str:
    """MD5 加密，返回 32 位大写哈希值。

    Args:
        text: 待加密的字符串

    Returns:
        32 位大写 MD5 哈希值
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest().upper()


def _generate_sign_local(token: str, imei: str, app_key: str, uri: str, timestamp: str) -> str:
    """本地生成 X-SIGN（fallback 方式）。

    签名规则: MD5(token + imei + appkey + uri + timestamp),timestamp

    Args:
        token: 用户 token，未登录时传空字符串
        imei: 设备 IMEI
        app_key: 应用密钥
        uri: 请求 URI，如 /v3.0/login.json
        timestamp: 时间戳（秒）

    Returns:
        完整的 X-SIGN 值，格式: MD5_HASH,timestamp
    """
    s = str(token) + imei + app_key + uri + timestamp
    md5_hash = md5_encrypt(s)
    return f"{md5_hash},{timestamp}"


def generate_sign(token: str, imei: str, app_key: str, uri: str, timestamp: str = None) -> str:
    """生成 X-SIGN，优先使用内网工具，失败时 fallback 到本地计算。

    Args:
        token: 用户 token，未登录时传空字符串
        imei: 设备 IMEI
        app_key: 应用密钥
        uri: 请求 URI，如 /v3.0/login.json
        timestamp: 时间戳（秒），默认取当前时间

    Returns:
        完整的 X-SIGN 值，格式: MD5_HASH,timestamp
    """
    if timestamp is None:
        timestamp = str(int(time.time()))

    # 优先尝试内网工具
    try:
        resp = requests.post(
            f"{TOOL_BASE_URL}/createsign3.php",
            data={
                "uri": uri,
                "imei": imei,
                "appkey": app_key,
                "token": token,
                "timestamp": timestamp,
            },
            proxies={"http": None, "https": None},
            timeout=3,
        )
        result = resp.text.strip()
        if "error" not in result and "," in result:
            logger.debug(f"使用内网工具生成签名: {result[:20]}...")
            return result
        else:
            logger.warning(f"内网工具返回错误: {result}，切换到本地签名")
    except Exception as e:
        logger.warning(f"内网工具调用失败: {e}，切换到本地签名")

    # Fallback 到本地计算
    local_sign = _generate_sign_local(token, imei, app_key, uri, timestamp)
    logger.debug(f"使用本地计算生成签名: {local_sign[:20]}...")
    return local_sign


def encrypt_data(plain_text: str) -> str:
    """调用内网工具加密数据。

    Args:
        plain_text: 明文 JSON 字符串

    Returns:
        加密后的密文字符串
    """
    resp = requests.post(
        f"{TOOL_BASE_URL}/encode.php",
        data={"decodetxt": plain_text, "typeid": 0},
        proxies={"http": None, "https": None},
        timeout=10,
    )
    result = resp.text.strip()
    if "error" in result:
        raise RuntimeError(f"加密失败: {result}")
    return result


def decrypt_data(cipher_text: str) -> str:
    """调用内网工具解密数据。

    Args:
        cipher_text: 密文字符串

    Returns:
        解密后的明文字符串
    """
    resp = requests.post(
        f"{TOOL_BASE_URL}/encode.php",
        data={"decodetxt": cipher_text, "typeid": 1},
        proxies={"http": None, "https": None},
        timeout=10,
    )
    return resp.text.strip()
