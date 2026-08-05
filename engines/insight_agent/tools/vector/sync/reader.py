"""从 MySQL 读取文档供向量同步。"""
from dataclasses import fields
from datetime import datetime
from typing import Any, Mapping

from engines.contracts.evidence import Engagement
from engines.insight_agent.tools.db_connection import (
    DataBaseConnectionManager,
    connection_manager,
)
from engines.insight_agent.tools.search_results import DocumentRecord
from engines.insight_agent.tools.sql import vector_sql_statement


class DocumentRecordReader:
    def __init__(
            self,
            connection_manager: DataBaseConnectionManager = connection_manager,
    ):
        self._connection_manager = connection_manager

    async def read_all_documents(self) -> list[DocumentRecord]:
        async with self._connection_manager.get_async_engine().connect() as connection:
            result = await connection.execute(vector_sql_statement())
            rows = result.mappings().all()
        return [document for row in rows if (document := self._map_row_to_document(row))]

    @staticmethod
    def _map_row_to_document(row: Mapping[str, Any]) -> DocumentRecord | None:
        content = row.get("content")
        published_at = datetime.fromtimestamp(int(row.get("published_at")))
        if not content.strip():
            return None
        return DocumentRecord(
            platform=row["platform"],
            source_table=row["source_table"],
            mysql_primary_key=row["mysql_primary_key"],
            content=content,
            published_at=published_at,
            engagement={
                metric_field.name: float(
                    row.get(f"eng_{metric_field.name}")
                )
                for metric_field in fields(Engagement)
            },
            hotness_score=row["hotness_score"],
        )
