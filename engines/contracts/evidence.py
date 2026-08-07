from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Engagement:
    likes: float
    comments: float
    shares: float
    collects: float
    replies: float



@dataclass(slots=True)
class EvidenceDocument:
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
class RetrievalMeta:
    """召回过程元数据(查询词/通道/分数)"""

    matched_queries: list[str] = field(default_factory=list)
    channel_scores: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class EvidenceRecord:
    """一次检索中命中的舆情证据及其召回元数据。"""

    document: EvidenceDocument
    retrieval: RetrievalMeta = field(default_factory=RetrievalMeta)

    @property
    def id(self) -> str:
        return self.document.doc_id




