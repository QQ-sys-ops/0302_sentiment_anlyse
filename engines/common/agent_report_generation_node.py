import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import role_display_name
from engines.contracts.research_graph_state import ResearchGraphState
from engines.prompts.report import (
    AGENT_REPORT_GENERATION_SYSTEM_PROMPT,
    AGENT_REPORT_GENERATION_USER_PROMPT
)


class AgentReportGenerationNode(ResearchNode):
    """将 Agent 的章节正文整合为独立研究报告"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        """整合研究状态中的章节并生成独立报告"""
        agent_name = role_display_name(state["role"])
        self.context.report_progress("generating", f"{agent_name} 开始生成独立报告", 70)

        query = state["query"]
        sections = state["sections"]
        logger.info(f"开始生成独立报告,舆论话题: {query},待整合章节数: {len(sections)}")

        report_context = json.dumps(
            [{"title": section["title"], "body": section["body"]} for section in sections],
            ensure_ascii=False
        )

        report = await self._generate_report(report_context, query)

        self.context.report_progress("generating", f"{agent_name} 独立报告生成完成", 80)
        return {"final_report": report}

    async def _generate_report(self, report_context: str, query: str) -> str:
        """调用大模型生成独立研究报告正文"""
        prompt_template = PromptTemplate.from_template(template=AGENT_REPORT_GENERATION_USER_PROMPT)

        user_prompt = prompt_template.format(
            research_topic=query,
            report_context=report_context
        )

        raw_text = await self.context.llm_client.generate_text(
            system_prompt=AGENT_REPORT_GENERATION_SYSTEM_PROMPT,
            user_prompt=user_prompt
        )
        return raw_text
