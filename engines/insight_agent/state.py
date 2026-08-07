from engines.contracts.evidence import EvidenceRecord
from engines.contracts.research_graph_state import ResearchGraphState, SectionState


class InsightState(ResearchGraphState[SectionState], total=False):
    """LangGraph 全局状态：证据处理结果、章节列表与游标。"""

    retrieved_records: list[EvidenceRecord]
    records_by_id: dict[str, EvidenceRecord]
    rerank_scores: dict[str, float]
    section_record_ids: dict[str, list[str]]

    section_evidence_records: list[list[EvidenceRecord]]
