"""跨平台 MySQL 四表关键词检索"""
from datetime import datetime
from typing import Any
from dataclasses import fields

from engines.contracts.evidence import Engagement
from engines.insight_agent.tools.db_connection import DataBaseConnectionManager, connection_manager
from engines.insight_agent.tools.search_results import SearchResult, EvidenceDocument
from engines.insight_agent.tools.sql import db_sql_statement


class DatabaseSearchRepository:
    """MySQL 数据仓储：提供检索及封装数据结果"""

    def __init__(self, con_manager: DataBaseConnectionManager = connection_manager):
        """初始化数据库仓储实例及连接管理器"""
        self._con_manager = con_manager

    async def db_call(self, query: str, limit: int = 100) -> SearchResult:
        """根据关键词跨表检索数据库并封装为搜索结果。"""
        rows: list[dict[str, Any]] = await self._fetch_db_row(db_sql_statement(),
                                                              {"search_term": f"%{query}%", "limit": limit})

        return SearchResult(retrieval_channel="db_call",
                            retrieval_results=[self._map_row_to_document(row) for row in rows])

    def _map_row_to_document(self, row: dict[str, Any]) -> EvidenceDocument:
        """将数据库单行结果映射为标准的证据文档对象"""
        return EvidenceDocument(
            platform=row["platform"],
            source_table=row["source_table"],
            source_id=row["mysql_primary_key"],
            content=row.get('title_or_content') or '',
            published_at=datetime.fromtimestamp(row["published_at"]),
            engagement={
                field.name: float(row[f'eng_{field.name}']) for field in fields(Engagement)
            },
            hotness_score=row["hotness_score"]
        )

    async def _fetch_db_row(self,
                            statement: Any,
                            params: dict[str, Any]) -> list[dict[str, Any]]:
        """异步执行 SQL 语句并以字典列表形式返回原始查询结果"""
        session_factory = connection_manager.get_async_session_factory()
        async with session_factory() as session:
            result = await session.execute(statement, params)

            return [dict(row) for row in result.mappings().all()]
