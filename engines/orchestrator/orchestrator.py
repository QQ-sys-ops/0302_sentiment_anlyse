from typing import Callable, Awaitable
from loguru import logger

from engines.common.events import (
    RoleErrorEvent,
    publish_role_error,
    publish_role_result,
    RoleResultEvent,
    publish_role_progress, RoleProgressEvent
)
from engines.common.llm import LLMClient
from engines.common.logger import router_log_by_role
from engines.common.research_graph_runtime import ProgressCallback, ProgressUpdate
from engines.contracts.agent_roles import RoleKey
from engines.common.task_manager import research_task_manager
from engines.common.reports import get_output_dir
from engines.media_agent.agent import media_agent_handler
from engines.insight_agent.agent import insight_agent_handler

AGENT_HANDLER = Callable[
    [RoleKey, str, str, LLMClient, str, ProgressCallback | None], Awaitable[None]]


class OrchestratorAgent:

    def __init__(self):
        """初始化各研究角色对应的任务处理器"""
        self._agent_handlers: dict[RoleKey, AGENT_HANDLER] = {
            "insight": insight_agent_handler,
            "media": media_agent_handler
        }

    def dispatch_task(self, query: str, task_id: str):
        """向所有研究角色分发指定研究任务"""
        for role in self._agent_handlers:
            research_task_manager.submit_task(self.execute_research_task(query, task_id, role))

    async def execute_research_task(self, query: str, task_id: str, role: RoleKey):
        """执行两个角色研究智能体"""

        with router_log_by_role(role):
            self._publish_progress(
                task_id,
                role,
                ProgressUpdate(status="starting", message="开始执行研究", progress_pct=0)
            )
            try:
                llm_client = LLMClient.from_role(role)
                output_dir = get_output_dir(task_id, role)
                await self._agent_handlers[role](
                    role,
                    query,
                    task_id,
                    llm_client,
                    output_dir,
                    lambda update: self._publish_progress(task_id, role, update)
                )
            except Exception as exec:
                logger.error(f"{role} 研究智能体执行期间出现了异常: {exec}")
                publish_role_error(
                    RoleErrorEvent(task_id=task_id, role=role, error=str(exec))
                )
                return
            publish_role_result(RoleResultEvent(task_id=task_id, role=role))

    @staticmethod
    def _publish_progress(
            task_id: str, role: RoleKey, update: ProgressUpdate
    ) -> None:
        """发布指定研究角色的进度事件。"""
        publish_role_progress(
            RoleProgressEvent(
                task_id=task_id,
                role=role,
                status=update.status,
                message=update.message,
                progress_pct=update.progress_pct
            )
        )


def   main(text:str):
    print("xxx")