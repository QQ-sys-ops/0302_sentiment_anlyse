"""主持人结构化裁决契约:Host 与 Report 引擎共享的裁决模型与 Markdown 渲染。"""

from pydantic import BaseModel, Field


class SectionJudgement(BaseModel):
    """主持人对单个章节的结构化裁决。"""

    section_key: str
    aligned_points: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    evidence_review: str
    host_judgement: str

    @property
    def content(self) -> str:
        """渲染讨论区展示用的 Markdown 文本。"""
        return render_judgement_markdown(self)


def render_judgement_markdown(judgement: SectionJudgement) -> str:
    """将结构化裁决渲染为 Markdown,标题层级按嵌入上下文调整。"""
    heading_level = "#" * 3
    blocks = [
        judgement.host_judgement or "暂无研判",
        f"{heading_level} 双方一致观点\n"
        f"{format_markdown_list(judgement.aligned_points)}",
        f"{heading_level} 关键分歧\n"
        f"{format_markdown_list(judgement.conflicts)}",
        f"{heading_level} 证据情况与信息缺口\n"
        f"{judgement.evidence_review or '暂无补充'}",
    ]
    return "\n\n".join(blocks)


def format_markdown_list(items: list[str]) -> str:
    """渲染无序列表"""
    return "\n".join(f"- {item}" for item in items) or "- 暂无"
