import os
from typing import Any

from dotenv import set_key

from engines.contracts.settings import get_settings, ENV_FILE, Settings, reload_settings

ALLOWED_CONFIG_KEYS = [
    "DB_HOST", "DB_PORT", "DB_USER", "DB_NAME",
    "INSIGHT_ENGINE_API_KEY", "INSIGHT_ENGINE_BASE_URL", "INSIGHT_ENGINE_MODEL_NAME", "INSIGHT_ENGINE_MODEL_PROVIDER",
    "MEDIA_ENGINE_API_KEY", "MEDIA_ENGINE_BASE_URL", "MEDIA_ENGINE_MODEL_NAME", "MEDIA_ENGINE_MODEL_PROVIDER",
    "REPORT_ENGINE_API_KEY", "REPORT_ENGINE_BASE_URL", "REPORT_ENGINE_MODEL_NAME", "REPORT_ENGINE_MODEL_PROVIDER",
    "HOST_API_KEY", "HOST_BASE_URL", "HOST_MODEL_NAME", "HOST_MODEL_PROVIDER",
    "ANSPIRE_API_KEY", "ANSPIRE_BASE_URL"
]


def _mark_secret(value: str) -> str:
    """遮蔽敏感配置值并保留末四位"""
    if not value:
        return ""

    return f"****{value[-4:]}"


class SystemConfigService:

    def get_config_info(self) -> dict[str, Any]:
        """读取配置信息"""
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
        """修改配置信息"""
        unknown_keys = [key for key in config_info if key not in ALLOWED_CONFIG_KEYS]
        if unknown_keys:
            raise ValueError(f"不支持不允许的配置{'、'.join(unknown_keys)}")
        for key, value in config_info.items():
            set_key(ENV_FILE, key, value, quote_mode="never")
            os.environ[key] = value

        return reload_settings()
