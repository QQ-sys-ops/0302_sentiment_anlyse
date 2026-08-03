import os
from typing import Any

from dotenv import set_key

from enginess.contracts.setttings import get_settings, ENV_FILE, Settings, reload_settings

ALLOWED_CONFIG_KEYS = [
    "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
    "INSIGHT_ENGINE_API_KEY", "INSIGHT_ENGINE_BASE_URL", "INSIGHT_ENGINE_MODEL_NAME", "INSIGHT_ENGINE_MODEL_PROVIDER",
    "MEDIA_ENGINE_API_KEY", "MEDIA_ENGINE_BASE_URL", "MEDIA_ENGINE_MODEL_NAME", "MEDIA_ENGINE_MODEL_PROVIDER",
    "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
    "HOST_API_KEY", "HOST_BASE_URL", "HOST_MODEL_NAME", "HOST_MODEL_PROVIDER",
    "SEARCH_SWITCH", "TAVILY_API_KEY",
    "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
]


def _mark_secret(value: str) -> str:
    if not value:
        return ""

    return f"****{value[-4:]}"  # 加铭


class SystemConfigService:

    def get_config_info(self) -> dict[str, Any]:
        """
        读取配置信息
        :return:
        """
        config_info: dict[str, Any] = {}

        setting = get_settings()
        for key in ALLOWED_CONFIG_KEYS:
            raw_value = getattr(setting, key, None)
            value = "" if raw_value is None else str(raw_value)

            if key.endswith("_API_KEY"):
                value = _mark_secret(value)

            config_info[key] = value

        return config_info

    def update_config_info(self, config_info: dict[str, Any]) -> Settings:
        """
        修改配置信息
        :param config_info:
        :return:
        """

        # 1. 白名单校验
        unknown_keys = [key for key in config_info if key not in ALLOWED_CONFIG_KEYS]

        if unknown_keys:
            raise ValueError(f"不支持不允许的配置{'、'.join(unknown_keys)}")

        # 2. 修改配置信息
        for key, value in config_info.items():
            # 2.1 更新到.env文件中
            set_key(ENV_FILE, key, value,quote_mode="never")
            # 2.2 更新到环境变量中
            os.environ[key] = value

        # 3.  重新读取更新之后的
        return  reload_settings()
