import asyncio
from typing import Any

from loguru import logger

from engines.common.events import (
    EventType,
    publish_host_discussion_message,
    subscribe,
    unsubscribe
)
from engines.common.task_manager import research_task_manager
from engines.contracts.agent_roles import role_display_name
from engines.host_agent.graph import build_graph
from engines.host_agent.section_judge import HostSectionJudge
from engines.host_agent.section_pair_store import SectionPairStore
from engines.host_agent.state import HostState


class SectionReadyListener:
    """串行消费章节就绪事件并驱动 Host LangGraph"""

    def __init__(self):
        """初始化 Host 图及任务状态存储"""
        self._graph = build_graph(HostSectionJudge())
        self._host_states: dict[str, HostState] = {}
        self._event_queue: asyncio.Queue[dict[str, Any]]

    def start(self):
        """订阅章节就绪事件并启动消费任务"""
        self._event_queue = asyncio.Queue()
        subscribe(EventType.SECTION_READY, self._enqueue_event)
        research_task_manager.submit_task(self._process_events())
        logger.info("SectionReadyListener: 已启动 Host 章节研判")

    def stop(self):
        """取消事件订阅并释放运行状态"""
        unsubscribe(self._enqueue_event)
        self._host_states.clear()
        logger.info("SectionReadyListener: 已停止")

    def _enqueue_event(
            self,
            _event_type: EventType,
            event_payload: dict[str, Any]
    ):
        """将章节就绪事件加入串行消费队列"""
        self._event_queue.put_nowait(event_payload)

    async def _process_events(self):
        """持续消费章节就绪事件并发布 Host 讨论事件"""

        while True:
            event_payload = await self._event_queue.get()
            task_id = event_payload["task_id"]
            host_state = self._host_states.get(task_id)
            if host_state is None:
                host_state = {
                    "task_id": task_id,
                    "section_pair_store": SectionPairStore(),
                    "judgements": []
                }
            invocation_state: HostState = {
                **host_state,
                "event_payload": event_payload
            }
            updated_state: HostState = await self._graph.ainvoke(invocation_state)
            discussion_events = updated_state["discussion_events"]
            self._host_states[task_id] = {
                "task_id": task_id,
                "section_pair_store": updated_state["section_pair_store"],
                "judgements": updated_state["judgements"]
            }
            for discussion_event in discussion_events:
                logger.info(
                    f"【{role_display_name('host')}】发送讨论事件 "
                    f"来源={role_display_name(discussion_event.source)} "
                    f"章节={discussion_event.section_key} "
                    f"内容={discussion_event.content[:20]}..."
                )
                publish_host_discussion_message(discussion_event)
