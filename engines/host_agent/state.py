from typing import Any, TypedDict

from engines.common.events import HostDiscussionMessageEvent
from engines.contracts.judgement import SectionJudgement
from engines.host_agent.section_pair_store import SectionPairStore


class HostState(TypedDict, total=False):
    """Host LangGraph 的事件输入、章节配对与研判状态。"""

    task_id: str                                                    # 任务ID
    event_payload: dict[str, Any]                                   # 五个章节对应的章节准备事件类型的数据包
    section_pair_store: SectionPairStore                            # 章节对"存储"----->章节对：管理章节对（最起码作用：章节对存储起来）
    judgements: list[SectionJudgement]                              # 五个章节研判结果，每一个研判结果是一个结构化对象
    discussion_events: list[HostDiscussionMessageEvent]             # 三个角色讨论区要展示的数据对象
    section_judgement: SectionJudgement                             # 当前章节的研判结果
