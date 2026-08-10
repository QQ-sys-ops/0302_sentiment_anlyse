"""跨平台 MySQL 四表关键词检索。"""
import asyncio
from datetime import datetime
from typing import Any
from dataclasses import fields, dataclass

from engines.contracts.evidence import Engagement
from engines.insight_agent.tools.db_connection import DataBaseConnectionManager, connection_manager
from engines.insight_agent.tools.search_results import SearchResult, EvidenceDocument
from engines.insight_agent.tools.sql import db_sql_statement


class DatabaseSearchRepository:
    """MySQL 数据仓储：提供检索及封装数据结果"""

    def __init__(self, con_manager: DataBaseConnectionManager = connection_manager):
        self._con_manager = con_manager

    async def db_call(self, query: str, limit: int = 100) -> SearchResult:
        # 1. 查询
        rows: list[dict[str, Any]] = await self._fetch_db_row(db_sql_statement(),
                                                              {"search_term": f"%{query}%", "limit": limit})

        # 2. 获取查询结果组装到最终数据模型SearchResult 返回
        return SearchResult(retrieval_channel="db_call",
                            retrieval_results=[self._map_row_to_document(row) for row in rows])

    def _map_row_to_document(self, row: dict[str, Any]) -> EvidenceDocument:
        return EvidenceDocument(
            platform=row["platform"],
            source_table=row["source_table"],
            source_id=row["mysql_primary_key"],
            content=row.get('title_or_content') or '',
            published_at=datetime.fromtimestamp(row["published_at"]),
            engagement={
                field.name:float(row[f'eng_{field.name}']) for field in fields(Engagement)   # 小写的fields 不是大写Field
            },
            hotness_score=row["hotness_score"],
        )

    async def _fetch_db_row(self,
                            statement: Any,
                            params: dict[str, Any]) -> list[dict[str, Any]]:
        # 1. 获取session工厂
        session_factory = connection_manager.get_async_session_factory()

        # 2. 获取session对象 执行sql 返回结果
        async with session_factory() as session:
            result = await session.execute(statement, params)

            return [dict(row) for row in result.mappings().all()]


async def main():
    repo = DatabaseSearchRepository()
    keyword = "高考"
    limit = 10
    try:
        result: SearchResult = await repo.db_call(query=keyword, limit=limit)

        print(f"检索成功,返回通道: {result.retrieval_channel}")
        records = result.retrieval_results
        print(f"共查到 {len(records)} 条数据")
        for idx, record in enumerate(records, start=1):
            print(f"[{idx}] 平台: {record.platform} | 数据表: {record.source_table} | ID: {record.mysql_primary_key}")
            print(f"    内容: {record.content[:50]}...")
            print(f"    发布时间: {record.published_at}")
            print(f"    互动数据: {record.engagement}")
            print(f"    热度得分: {record.hotness_score}")
            print("-" * 50)

    finally:
        await connection_manager.dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
