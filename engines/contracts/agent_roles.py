from typing import Literal
from dataclasses import  dataclass
RoleKey=Literal["insight","media","host","report"]

@dataclass(slots=True)
class RoleInfo:
    confix_prefix:str     # 角色的配置前缀
    agent_name:str



ROLE_INFOS:dict[RoleKey,RoleInfo]={
    "insight": RoleInfo(confix_prefix="INSIGHT_ENGINE",agent_name="私域检索智能体专家"),
    "media": RoleInfo(confix_prefix="MEDIA_ENGINE",agent_name="公域检索智能体专家"),
    "host": RoleInfo(confix_prefix="HOST",agent_name="研判智能体专家"),
    "report": RoleInfo(confix_prefix="REPORT_ENGINE",agent_name="报告引擎")
}
