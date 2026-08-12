import json

from langchain_core.prompts import PromptTemplate

from engines.common.llm import LLMClient
from engines.contracts.judgement import SectionJudgement
from engines.host_agent.models import AgentSectionPair
from engines.prompts.host import (
    HOST_SECTION_JUDGE_SYSTEM_PROMPT,
    HOST_SECTION_JUDGE_USER_PROMPT
)


class HostSectionJudge:
    """调用 Host LLM 对 Insight 与 Media 的同章节输出进行研判"""

    llm_client: LLMClient = LLMClient.from_role("host")

    async def judge_section(
            self,
            section_pair: AgentSectionPair
    ) -> SectionJudgement:
        """生成单章节结构化研判"""

        judgement_evidence = self._build_judgement_context(section_pair)


        prompt = PromptTemplate.from_template(HOST_SECTION_JUDGE_USER_PROMPT).format(
            judgement_evidence=judgement_evidence
        )

        judgement = await self.llm_client.generate_object(
            HOST_SECTION_JUDGE_SYSTEM_PROMPT,
            prompt,
            SectionJudgement,
        )
        return judgement.model_copy(update={"section_key": section_pair.section_key})

    def _build_judgement_context(
            self,
            section_pair: AgentSectionPair,
    ) -> str:
        """组装当前双 Agent 的同章节输出"""
        judgement_context = {
            "section": {
                "key": section_pair.section_key,
                "title": section_pair.title,
            },
            "insight": {"body": section_pair.insight.body[:3000]},
            "media": {"body": section_pair.media.body[:3000]},
        }
        return json.dumps(judgement_context, ensure_ascii=False)
