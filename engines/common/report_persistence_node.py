from typing import Any

from loguru import logger

from engines.common.reports import save_report
from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS
from engines.contracts.research_graph_state import ResearchGraphState


class ReportPersistenceNode(ResearchNode):
    """将 Agent 独立报告落盘并注册到研究运行。"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始进行独立报告落盘")


        final_report = state["final_report"]

        md_path = save_report(
            self.context.output_dir,
            f"{state['query']}_report.md",
            final_report,
        )

        logger.info(f"{role_info.agent_name} 独立报告落盘完成：{md_path}")
        return {}
