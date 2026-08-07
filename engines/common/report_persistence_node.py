from typing import Any

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.research_graph_state import ResearchGraphState


class ReportPersistenceNode(ResearchNode):
    """将 Agent 独立报告落盘并注册到研究运行。"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        pass