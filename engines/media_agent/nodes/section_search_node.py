import asyncio
from itertools import zip_longest
from typing import Any

from engines.common.research_graph_runtime import ResearchNode, ResearchRunContext
from engines.contracts.agent_roles import role_display_name
from engines.contracts.evidence import EvidenceRecord
from engines.media_agent.state import MediaSectionState, MediaState
from engines.media_agent.web_search.retrieval_service import MediaRetrievalService


class SearchNode(ResearchNode):
    """遍历章节组合关键词检索并聚合去重证据"""

    def __init__(self, context: ResearchRunContext) -> None:
        """初始化检索节点及媒体检索服务"""
        super().__init__(context)
        self._retrieval_service = MediaRetrievalService()

    async def __call__(self, state: MediaState) -> dict[str, Any]:
        """遍历章节执行检索并去重产出证据池"""
        agent_name = role_display_name(state["role"])
        self.context.report_progress("searching", f"{agent_name} 开始执行公域信息搜索", 30)

        query = state.get("query")
        sections: list[MediaSectionState] = state.get("sections")
        section_evidence_records = []
        section_queries = []

        for section in sections:
            tool = section.get("search_tool")
            keywords = section.get("search_keywords")
            queries = [f"{query} {keyword}".strip() for keyword in keywords]
            query_results = await asyncio.gather(
                *(
                    self._retrieval_service.retrieve_evidence(tool, search_query)
                    for search_query in queries
                ),
            )
            section_records = _merge_query_results(query_results)
            section_evidence_records.append(section_records)
            section_queries.append(
                "\n".join(f"[{tool}] {search_query}" for search_query in queries)
            )
        self.context.report_progress("searching", f"{agent_name} 执行公域信息搜索完成", 40)
        return {
            "section_evidence_records": section_evidence_records,
            "section_queries": section_queries,
        }


def _merge_query_results(
        query_results: list[list[EvidenceRecord]],
) -> list[EvidenceRecord]:
    """各查询内按相关分降序排列，再轮询合并并按证据 ID 去重"""
    selected: list[EvidenceRecord] = []
    seen_ids: set[str] = set()
    ranked_results = [
        sorted(
            records,
            key=lambda record: record.retrieval.channel_scores.get("web_call"),
            reverse=True
        )
        for records in query_results
    ]
    for ranked_records in zip_longest(*ranked_results):
        for record in ranked_records:
            if record is None or record.id in seen_ids:
                continue
            seen_ids.add(record.id)
            selected.append(record)
    return selected
