"""Insight 两路检索编排:MySQL 关键词召回 + Milvus 语义召回"""

import asyncio
from datetime import datetime, timedelta

import jieba.analyse

from engines.contracts.evidence import EvidenceDocument, EvidenceRecord, RetrievalMeta
from engines.contracts.settings import get_settings
from engines.insight_agent.tools.db.repository import DatabaseSearchRepository
from engines.insight_agent.tools.vector.repository import VectorSearchRepository


class InsightRetrievalService:
    """编排 MySQL 与 Milvus 两路检索并归一化为证据"""

    def __init__(self):
        """初始化数据库与可选的向量检索仓储"""
        self._db_repo = DatabaseSearchRepository()
        self._vector_repo = (
            VectorSearchRepository()
            if get_settings().INSIGHT_VECTOR_ENABLED
            else None
        )

    async def retrieve_evidence(self, query: str) -> list[EvidenceRecord]:
        """并发执行两路召回并返回原始命中"""
        db_records, vector_records = await asyncio.gather(
            self._retrieve_db_evidence(query), self._retrieve_vector_evidence(query)
        )
        return [*db_records, *vector_records]

    async def _retrieve_db_evidence(self, query: str) -> list[EvidenceRecord]:
        """按原句与分词并发执行 MySQL 关键词召回"""
        search_terms = _build_db_search_terms(query)
        db_results = await asyncio.gather(
            *(
                self._db_repo.db_call(search_term, limit=50)
                for search_term in search_terms
            )
        )
        return [
            map_document_to_evidence(
                document,
                db_result.retrieval_channel,
                search_term,
                channel_score=1.0
            )
            for search_term, db_result in zip(search_terms, db_results)
            for document in db_result.retrieval_results
        ]

    async def _retrieve_vector_evidence(self, query: str) -> list[EvidenceRecord]:
        """执行 Milvus 混合检索,得分按批次最高分归一化"""
        if self._vector_repo is None:
            return []

        vector_hits = await asyncio.to_thread(
            self._vector_repo.vector_call,
            query=query,
            limit=10,
            filter_expression=_build_published_at_filter()
        )

        max_retrieval_score = max(hit.retrieval_score for hit in vector_hits)
        return [
            map_document_to_evidence(
                hit.retrieval_document,
                hit.retrieval_channel,
                query,
                channel_score=(
                        hit.retrieval_score / max_retrieval_score
                )
            )
            for hit in vector_hits
        ]


def _build_db_search_terms(query: str) -> list[str]:
    """原句加 jieba 抽取的关键词,去重保序"""
    search_terms = [query]
    for extracted_term in jieba.analyse.extract_tags(query, 2):
        if 2 <= len(extracted_term) <= 4 and extracted_term not in search_terms:
            search_terms.append(extracted_term)
    return search_terms


def _build_published_at_filter() -> str:
    """生成按发布时间过滤的 Milvus 表达式"""
    filter_days = get_settings().INSIGHT_VECTOR_FILTER_DAYS
    start_timestamp = int(
        (datetime.now() - timedelta(days=filter_days)).timestamp()
    )
    return f"published_at >= {start_timestamp}"


def map_document_to_evidence(
        document: EvidenceDocument,
        retrieval_channel: str,
        matched_query: str,
        channel_score: float
) -> EvidenceRecord:
    """将统一文档记录转为证据记录,标注召回通道、查询词与得分"""
    return EvidenceRecord(
        document=document,
        retrieval=RetrievalMeta(
            matched_queries=[matched_query],
            channel_scores={retrieval_channel: channel_score},
        )
    )
