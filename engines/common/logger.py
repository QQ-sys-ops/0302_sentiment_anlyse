from contextlib import contextmanager
from pathlib import Path

from loguru import logger

from engines.contracts.agent_roles import RoleKey
from engines.contracts.settings import get_settings


@contextmanager
def router_log_by_role(role: RoleKey):
    """根据Agent的角色分发日志"""
    log_handler_id = None
    settings = get_settings()
    LOG_DIR = Path(settings.LOG_DIR)

    with logger.contextualize(role=role):
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_handler_id = logger.add(
                str(LOG_DIR / f"{role}.log"),
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{extra[role]}] {name} - {message}",
                rotation="1MB",
                encoding="utf-8",
                filter=lambda record: record['extra'].get('role') == role
            )
            yield
        finally:
            if log_handler_id is not None:
                logger.remove(log_handler_id)
