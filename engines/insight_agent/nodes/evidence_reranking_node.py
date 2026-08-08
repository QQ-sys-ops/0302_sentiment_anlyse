from typing import Any

from loguru import logger

from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS
from engines.contracts.evidence import EvidenceRecord, RetrievalMeta
from engines.insight_agent.state import InsightState


class EvidenceRerankingNode(ResearchNode):
    """合并重复召回证据并计算统一重排分。"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """合并重复召回结果、计算排名分数并构建证据索引。"""
        role = state['role']
        role_info = ROLE_INFOS[role]
        logger.info(f"{role_info.agent_name} 开始进行去重、重排序")



        # 1. 合并去重
        merged_records = _dedupe_and_merge(state.get('retrieved_records'))

        # 2. 重新计算得分
        rerank_scores:dict[str,float] = _calculate_rerank_scores(merged_records)

        # 3. 重新排序
        ordered_records = sorted(
            merged_records,
            key=lambda record: rerank_scores.get(record.id),
            reverse=True,
        )

        logger.info(f"{role_info.agent_name} 去重、重排序完成")
        return {
            "records_by_id": {record.id: record for record in ordered_records},
            "rerank_scores": rerank_scores,
        }




def _dedupe_and_merge(retrieved_records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    records_by_id: dict[str, EvidenceRecord] = {}
    for record in retrieved_records:
        existing_record = records_by_id.get(record.id)
        if existing_record is None:
            records_by_id[record.id] = record
            continue
        records_by_id[record.id] = EvidenceRecord(
            document=existing_record.document,
            retrieval=RetrievalMeta(
                matched_queries=
                list(set(existing_record.retrieval.matched_queries + record.retrieval.matched_queries)),
                channel_scores={
                    **existing_record.retrieval.channel_scores,
                    **record.retrieval.channel_scores,
                },
            ),
        )
    return list(records_by_id.values())


def _calculate_rerank_scores(merged_records: list[EvidenceRecord]) -> dict[str, float]:
    max_hot_score = max(record.document.hotness_score for record in merged_records)

    return {
        record.id: _retrieval_score(record) * 0.6
                   + (record.document.hotness_score / max_hot_score) * 0.4
        for record in merged_records
    }


def _retrieval_score(record: EvidenceRecord) -> float:
    """按渠道权重加权召回得分并截断至 1。"""
    channel_scores = record.retrieval.channel_scores
    score = (
            channel_scores.get("vector_call", 0.0) * 0.5
            + channel_scores.get("db_call", 0.0) * 0.5
    )
    return score


if __name__ == '__main__':

    # list1=["高考"]
    # list2=["高考"]

    # print(list(set(list1+list2)))
    dict_data1={"id":"1234","name":"tom"}

    print(list(dict_data1.values()))
    # # dict_dat2={"age":18,"name":"jack"}
    # #
    # # dict_dat3={
    # #     **dict_dat2,
    # #     **dict_data1
    # # }
    # #
    # # print(dict_dat3)
    #

