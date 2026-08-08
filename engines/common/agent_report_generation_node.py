import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS
from engines.contracts.research_graph_state import ResearchGraphState
from engines.prompts.report import (
    AGENT_REPORT_GENERATION_SYSTEM_PROMPT,
    AGENT_REPORT_GENERATION_USER_PROMPT,
)


class AgentReportGenerationNode(ResearchNode):
    """将 Agent 的章节正文整合为独立研究报告。"""

    async def __call__(self, state: ResearchGraphState[Any]) -> dict[str, Any]:
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始将章节正文整合为独立研究报告")


        query = state["query"]
        sections = state["sections"]
        logger.info(f"开始生成独立报告,舆论话题: {query},待整合章节数: {len(sections)}")

        report_context = json.dumps(
            [{"title": section["title"], "body": section["body"]} for section in sections],
            ensure_ascii=False,
        )

        report = await self._generate_report(report_context, query)
        logger.info(f"{role_info.agent_name} 章节正文整合为独立研究报告完成")
        return {"final_report": report}

    async def _generate_report(self, report_context: str, query: str) -> str:
        prompt_template = PromptTemplate.from_template(template=AGENT_REPORT_GENERATION_USER_PROMPT)

        user_prompt = prompt_template.format(
            research_topic=query,
            report_context=report_context,
        )

        raw_text = await self.context.llm_client.generate_text(
            system_prompt=AGENT_REPORT_GENERATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return raw_text
