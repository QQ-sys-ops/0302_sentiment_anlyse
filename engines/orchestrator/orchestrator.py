from typing import Callable, Awaitable

from engines.common.llm import LLMClient
from engines.common.logger import router_log_by_role
from engines.contracts.role_rules import RoleKey
from engines.common.task_manager import research_task_manager
from engines.common.reports import get_output_dir
from engines.media_agent.agent import media_agent_handler
from engines.insight_agent.agent import insight_agent_handler

AGENT_HANDLER = Callable[[str, str, str, LLMClient, str], Awaitable[None]]  # 第一个参数放的是方法的参数，第二个参数方法的返回值


class OrchestratorAgent:

    def __init__(self):
        self._agent_handlers: dict[RoleKey, AGENT_HANDLER] = {
            "insight": insight_agent_handler,
            "media": media_agent_handler
        }

    def dispatch_task(self, query: str, task_id: str):
        for role in self._agent_handlers:
            # 异步启动两个协程对象给我并发的执行
            research_task_manager.submit_task(self.execute_research_task(query, task_id, role))

    async def execute_research_task(self, query: str, task_id: str, role: RoleKey):
        """

        :param query:
        :param task_id:
        :param role:
        :return:
        """

        with router_log_by_role(role):
            # 1. 获取角色对应的LLM客户端
            llm_client = LLMClient.from_role(role)

            # 2. 获取角色对应的报告输出目录
            output_dir = get_output_dir(task_id, role)

            # 3. 执行指定角色Agent的逻辑
            self._agent_handlers[role](
                role,
                query,
                task_id,
                llm_client,
                output_dir
            )
