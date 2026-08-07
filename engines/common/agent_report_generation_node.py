from typing import Any
from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.research_graph_state import ResearchGraphState


class AgentReportGenerationNode(ResearchNode):
    """将 Agent 的章节正文整合为独立研究报告。"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        pass