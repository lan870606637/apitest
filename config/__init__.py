import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
_config_dir = Path(__file__).parent
load_dotenv(_config_dir / ".env")

# 读取 config.yaml
with open(_config_dir / "config.yaml", "r", encoding="utf-8") as f:
    _raw_config = yaml.safe_load(f)

# 根据环境变量 ENV 决定使用哪套配置，默认取 config.yaml 中的 current_env
_env = os.getenv("ENV", _raw_config.get("current_env", "dev"))
_env_config = _raw_config["environments"][_env]

# 对外暴露的配置项
BASE_URL: str = _env_config["base_url"]
API_VERSION: str = _env_config["api_version"]
TIMEOUT: int = _env_config["timeout"]
RETRY_COUNT: int = _env_config["retry_count"]
LOG_CONFIG: dict = _raw_config.get("logging", {})

# 签名密钥
APP_KEY: str = _raw_config["sign"]["app_key"]

# X-APPKEY header 值
X_APPKEY: str = _raw_config["sign"]["app_key"]

# 设备 IMEI（用于签名计算）
IMEI: str = str(_raw_config["device_imei"])

# 加密后的 X-DEVICE / X-CLIENT 密文
X_DEVICE_ENCRYPTED: str = _raw_config["x_device_encrypted"]
X_CLIENT_ENCRYPTED: str = _raw_config["x_client_encrypted"]

# 终端类型
BIZ: str = _raw_config["biz"]

# 敏感信息从环境变量读取
TEST_PHONE: str = os.getenv("TEST_PHONE", "13986903203")
TEST_SMS_PASSWORD: str = os.getenv("TEST_SMS_PASSWORD", "884569")
