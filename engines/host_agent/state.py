from typing import Any, TypedDict

from engines.common.events import HostDiscussionMessageEvent
from engines.contracts.judgement import SectionJudgement
from engines.host_agent.section_pair_store import SectionPairStore


class HostState(TypedDict, total=False):
    """Host LangGraph 的事件输入、章节配对与研判状态"""

    task_id: str
    event_payload: dict[str, Any]
    section_pair_store: SectionPairStore
    judgements: list[SectionJudgement]
    discussion_events: list[HostDiscussionMessageEvent]
    section_judgement: SectionJudgement
