from typing import Literal
from dataclasses import dataclass

RoleKey = Literal["insight", "media", "host", "report"]
RESEARCH_ROLE_KEYS: tuple[RoleKey, ...] = ("insight", "media")

@dataclass(slots=True)
class RoleInfo:
    confix_prefix: str
    agent_name: str


ROLE_INFOS: dict[RoleKey, RoleInfo] = {
    "insight": RoleInfo(confix_prefix="INSIGHT_ENGINE", agent_name="私域检索智能体专家"),
    "media": RoleInfo(confix_prefix="MEDIA_ENGINE", agent_name="公域检索智能体专家"),
    "host": RoleInfo(confix_prefix="HOST", agent_name="研判智能体专家"),
    "report": RoleInfo(confix_prefix="REPORT_ENGINE", agent_name="报告引擎")
}


def role_display_name(role_key: RoleKey) -> str:
    """返回角色的中文展示名"""
    return ROLE_INFOS[role_key].agent_name
