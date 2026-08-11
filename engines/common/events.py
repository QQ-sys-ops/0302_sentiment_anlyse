from enum import Enum
from typing import Any, Callable, Literal, Mapping

from loguru import logger
from pydantic import BaseModel

from engines.contracts.agent_roles import role_display_name


class EventType(str, Enum):
    """研究流程中可发布的事件类型。"""

    ROLE_PROGRESS = "role_progress"
    ROLE_ERROR = "role_error"
    ROLE_RESULT = "role_result"
    SECTION_READY = "section_ready"
    HOST_DISCUSSION_MESSAGE = "host_discussion_message"


class SectionReadyEvent(BaseModel):
    task_id: str
    source: str
    section_key: str
    body: str


class HostDiscussionMessageEvent(BaseModel):
    task_id: str
    source: Literal["insight", "media", "host"]
    content: str
    section_key: str


EventCallback = Callable[[EventType, dict[str, Any]], None]
_subscribers: dict[EventType, set[EventCallback]] = {}


def subscribe(event_type: EventType, callback: EventCallback):
    _subscribers.setdefault(event_type, set()).add(callback)


def publish(event_type: EventType, data: dict[str, Any]):
    for callback in list(_subscribers.get(event_type)):
        try:
            callback(event_type, data)
        except Exception as exc:
            logger.error(f"事件订阅者执行失败：{exc}")


def unsubscribe(callback: EventCallback):
    for subscribers in _subscribers.values():
        subscribers.discard(callback)


def publish_section_ready(
        state: Mapping[str, Any],
        section: Mapping[str, Any]
):
    """从研究 Agent 图状态构造并发布章节就绪事件"""
    role = state["role"]
    agent_name = role_display_name(role)
    event = SectionReadyEvent(
        task_id=state["task_id"],
        source=role,
        section_key=section["section_key"],
        body=section.get("body")
    )
    publish(EventType.SECTION_READY, event.model_dump())
    logger.info(f"【{agent_name}】 发布 [章节{event.section_key}] 事件")


def publish_host_discussion_message(event: HostDiscussionMessageEvent):
    publish(EventType.HOST_DISCUSSION_MESSAGE, event.model_dump())
