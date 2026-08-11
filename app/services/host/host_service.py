from loguru import logger
from typing import Any

from engines.common.events import EventType, subscribe, unsubscribe
from engines.host_agent.section_ready_listener import SectionReadyListener
from app.services.host.discuss_buffer import DiscussionBuffer


class HostService:

    def __init__(self):
        self._listener = SectionReadyListener()
        self.discussion_buffer = DiscussionBuffer()

    def register_discussion_buffer(self):
        subscribe(EventType.HOST_DISCUSSION_MESSAGE, self._on_discussion_message)

    def stop_discussion_buffer(self):
        unsubscribe(self._on_discussion_message)

    def _on_discussion_message(self, _event_type: EventType, data: dict[str, Any]):
        logger.info(f"收到讨论消息...")
        self.discussion_buffer.append_message(data)

    def get_discussion_records(self, task_id: str) -> dict[str, Any]:
        return self.discussion_buffer.read_messages(task_id)

    def register_host_listener(self):
        """注册并启动 Host 研判监听器。"""
        self._listener.start()
        logger.info("HostService: 研判引擎启动成功")

    def stop_host_listener(self):
        """停止 Host 研判监听器。"""
        self._listener.stop()
        logger.info("HostService: 研判引擎已停止")
