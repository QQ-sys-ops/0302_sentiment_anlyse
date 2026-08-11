from engines.contracts.section_definitions import SECTION_DEFINITIONS
from engines.host_agent.models import AgentSectionOutput, AgentSectionPair

_REQUIRED_SOURCES = ("insight", "media")


class SectionPairStore:
    """按章节累积双 Agent 输出，并提供已就绪的章节配对。"""

    def __init__(self) -> None:
        self._outputs_by_section: dict[str, dict[str, AgentSectionOutput]] = {}
        self._judged_sections: set[str] = set()

    def store_output(self, output: AgentSectionOutput) -> None:
        """按章节与来源保存 Agent 输出。"""
        self._outputs_by_section.setdefault(output.section_key, {})[
            output.source
        ] = output



    def has_ready_pair(self) -> bool:
        """判断是否存在已齐备且尚未研判的章节配对。"""
        return any(self._is_pair_ready(section_key) for section_key in SECTION_DEFINITIONS)

    def get_ready_pair(self) -> AgentSectionPair:
        """按固定章节顺序返回首个待研判配对。"""
        section_key = next(
            section_key
            for section_key in SECTION_DEFINITIONS
            if self._is_pair_ready(section_key)
        )
        return self._build_section_pair(section_key)

    def mark_judged(self, section_key: str) -> None:
        """标记章节已完成研判。"""
        self._judged_sections.add(section_key)

    def all_sections_judged(self) -> bool:
        """判断全部固定章节是否已完成研判。"""
        return self._judged_sections.issuperset(SECTION_DEFINITIONS)

    def _is_pair_ready(self, section_key: str) -> bool:
        outputs = self._outputs_by_section.get(section_key, {})
        return section_key not in self._judged_sections and all(
            source in outputs for source in _REQUIRED_SOURCES
        )

    def _build_section_pair(self, section_key: str) -> AgentSectionPair:
        outputs = self._outputs_by_section[section_key]
        return AgentSectionPair(
            section_key=section_key,
            title=SECTION_DEFINITIONS[section_key].title,
            insight=outputs["insight"],
            media=outputs["media"]
        )

if __name__ == '__main__':



    set1={"a","b"}

    dict1={"a":"1","b":"2"}


    print(set1.issuperset(dict1))

