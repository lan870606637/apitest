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
TIMEOUT: int = _env_config["timeout"]
RETRY_COUNT: int = _env_config["retry_count"]
LOG_CONFIG: dict = _raw_config.get("logging", {})

# 敏感信息从环境变量读取
USERNAME: str = os.getenv("TEST_USERNAME", "")
PASSWORD: str = os.getenv("TEST_PASSWORD", "")
API_TOKEN: str = os.getenv("API_TOKEN", "")
