"""Insight/Media 共享的章节摘要节点基类。"""

from typing import Any

from engines.common.research_graph_runtime import ResearchNode
from engines.prompts.shared import SECTION_SUMMARY_USER_PROMPT


class BaseSectionSummaryNode(ResearchNode):
    """章节摘要节点基类:游标推进、证据组装、LLM 生成摘要与事件发布。"""

    system_prompt: str = ""
    user_prompt_template: str = SECTION_SUMMARY_USER_PROMPT

    async def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """按游标取证据包生成章节正文并发布就绪事件。"""
        pass