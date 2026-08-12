from typing import Any, Mapping

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import role_display_name
from engines.contracts.evidence import EvidenceRecord
from engines.contracts.research_graph_state import SectionState
from engines.contracts.section_definitions import SECTION_DEFINITIONS
from engines.insight_agent.state import InsightState


class SectionPreparationNode(ResearchNode):
    """初始化固定章节并为各章节选择、排序和截取证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """生成固定章节状态及供摘要节点消费的章节证据列表"""
        agent_name = role_display_name(state["role"])
        self.context.report_progress("planning", f"{agent_name} 开始固定章节与证据准备", 30)
        records_by_id = state.get("records_by_id")
        section_record_ids = state.get("section_record_ids")
        rerank_scores = state.get("rerank_scores")
        sections: list[SectionState] = []
        section_evidence_records: list[list[EvidenceRecord]] = []
        for definition in SECTION_DEFINITIONS.values():
            sections.append(
                {
                    "section_key": definition.key,
                    "title": definition.title,
                }
            )
            section_evidence_records.append(
                _select_section_records(
                    definition.key,
                    records_by_id,
                    section_record_ids,
                    rerank_scores,
                )[:20]
            )

        self.context.report_progress("planning", f"{agent_name} 固定章节与证据准备完成", 40)
        return {
            "sections": sections,
            "section_evidence_records": section_evidence_records,
        }


def _select_section_records(
        section_key: str,
        records_by_id: Mapping[str, EvidenceRecord],
        section_record_ids: Mapping[str, list[str]],
        rerank_scores: Mapping[str, float],
) -> list[EvidenceRecord]:
    """按章节键筛选证据并按统一重排分降序排列"""
    matched_records = [
        records_by_id[record_id]
        for record_id in section_record_ids.get(section_key)
    ]
    return sorted(
        matched_records,
        key=lambda record: rerank_scores.get(record.id),
        reverse=True
    )
