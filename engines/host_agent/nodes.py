import json
from typing import Any

from loguru import logger

from engines.common.reports import get_output_dir, save_report
from engines.contracts.agent_roles import role_display_name
from engines.host_agent.discussion_events import (
    build_agent_discussion_event,
    build_judgement_discussion_event
)
from engines.host_agent.models import AgentSectionOutput
from engines.host_agent.section_judge import HostSectionJudge
from engines.host_agent.state import HostState


class HostNodes:
    """Host LangGraph 的章节收集、研判、记录与持久化节点。"""

    def __init__(self, section_judge: HostSectionJudge) -> None:
        self._section_judge = section_judge

    async def collect_agent_output(self, state: HostState) -> dict[str, Any]:
        """保存当前 Agent 章节输出并生成对应讨论事件。"""
        agent_output = AgentSectionOutput.from_section_ready_event(
            state["event_payload"]
        )
        state["section_pair_store"].store_output(agent_output)
        discussion_events = [
            build_agent_discussion_event(state["task_id"], agent_output)
        ]
        host_name = role_display_name("host")
        logger.info(
            f"【{host_name}】收到章节就绪事件 "
            f"章节={agent_output.section_key} 来源={agent_output.source}"
        )
        return {
            "section_pair_store": state["section_pair_store"],
            "discussion_events": discussion_events,
        }

    async def generate_section_judgement(
            self,
            state: HostState,
    ) -> dict[str, Any]:
        """调用 Host LLM 为当前已齐备章节生成结构化研判。"""
        section_pair = state["section_pair_store"].get_ready_pair()
        host_name = role_display_name("host")
        logger.info(
            f"【{host_name}】双 Agent 章节已齐备，开始研判 "
            f"章节={section_pair.section_key}"
        )
        section_judgement = await self._section_judge.judge_section(section_pair)
        return {"section_judgement": section_judgement}

    async def apply_section_judgement(
            self,
            state: HostState,
    ) -> dict[str, Any]:
        """将章节研判应用到 Host 状态并生成讨论事件。"""
        section_judgement = state["section_judgement"]

        state["section_pair_store"].mark_judged(section_judgement.section_key)
        judgements = [*state["judgements"], section_judgement]
        discussion_events = [
            *state["discussion_events"],
            build_judgement_discussion_event(
                state["task_id"],
                section_judgement,
            ),
        ]
        logger.info(
            f"【{role_display_name('host')}】章节研判完成 "
            f"章节={section_judgement.section_key}"
        )
        return {
            "section_pair_store": state["section_pair_store"],
            "judgements": judgements,
            "discussion_events": discussion_events,
        }

    async def save_judgements(self, state: HostState) -> dict[str, Any]:
        """保存 Host 结构化研判。"""
        output_dir = get_output_dir(state["task_id"], "host")

        structured_content = json.dumps(
            [judgement.model_dump() for judgement in state["judgements"]],
            ensure_ascii=False,
            indent=2,
        )
        json_path = save_report(
            output_dir,
            "judgements.json",
            structured_content,
        )
        logger.info(f"Host 结构化研判已保存 {json_path}")
        return {}
