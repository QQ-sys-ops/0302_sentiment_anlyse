"""数据库与向量检索共享的结果模型。"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class DocumentRecord:
    """跨 MySQL 与 Milvus 的归一化的文档记录。"""

    platform: str
    source_table: str
    mysql_primary_key: int
    content: str
    published_at: datetime
    engagement: dict[str, float] = field(default_factory=dict)
    hotness_score: float = 0.0

    @property
    def doc_id(self) -> str:
        """根据来源字段生成稳定文档标识。"""
        return f"{self.platform}:{self.source_table}:{self.mysql_primary_key}"


@dataclass(slots=True)
class SearchResult:
    """MySQL召回结果集合。"""

    retrieval_channel: str
    retrieval_results: list[DocumentRecord] = field(default_factory=list)


@dataclass(slots=True)
class SearchHit:
    """Milvus包含检索元数据的单条向量命中结果。"""

    retrieval_score: float
    retrieval_channel: str
    retrieval_document: DocumentRecord
