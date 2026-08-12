"""Insight 与 Media 研究图共享的状态契约"""
from typing import Generic, TypeVar

from typing_extensions import NotRequired, TypedDict

from engines.contracts.agent_roles import RoleKey

class SectionState(TypedDict):
    """完成规划后在研究图中持续传递的章节状态"""

    section_key: str
    title: str
    body: NotRequired[str]



SectionStateT = TypeVar("SectionStateT", bound=SectionState)


class ResearchGraphState(TypedDict, Generic[SectionStateT], total=False):
    """研究图全流程共享的运行标识、章节与报告状态"""

    task_id: str
    query: str
    role: RoleKey
    sections: list[SectionStateT]
    cursor: int
    final_report: str
