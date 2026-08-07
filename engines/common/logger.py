from contextlib import contextmanager
from pathlib import Path

from loguru import logger

from engines.contracts.agent_roles import RoleKey
from engines.contracts.settings import get_settings


@contextmanager  # 让方法成为上下文管理器对象
def router_log_by_role(role: RoleKey):
    """
    根据Agent的角色分发日志
    日志级别：
    DEBUG:日志看的比较细: 10
    INFO:日志看的没有DeBug细:20
    WARNING:日志看的没有INFO细:30
    ERROR: 日志看的没有WARNING细:40
    日志级别<当前日志级别的日志看不到，比当前日志级别大的能看到
    :param role:
    :return:
    """
    log_handler_id = None
    settings = get_settings()
    LOG_DIR = Path(settings.LOG_DIR)


    with logger.contextualize(role=role):    # 给日志对象添加一个固定的上下文  extra:{"role":role}
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            log_handler_id = logger.add(
                str(LOG_DIR / f"{role}.log"),
                level="INFO",
                # format="{time: YYYY-MM-DD HH:mm:ss} | {level} | [{extra[role]}] | {name} - {message}",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{extra[role]}] {name} - {message}",
                rotation="1MB",
                encoding="utf-8",
                # filter=lambda record: record['extra'].get('role') == role
            )
            yield      #  分界线：with 代码块执行之前以及
        finally:
            if log_handler_id is not None:
                logger.remove(log_handler_id)  # 防止内存泄漏



if __name__ == '__main__':

    with router_log_by_role(role="media"):
        logger.info(f"Hello World")
        logger.info(f"Hello World")


