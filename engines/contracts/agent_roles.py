from typing import Literal
from dataclasses import  dataclass
RoleKey=Literal["insight","media","host","report"]

@dataclass(slots=True)
class RoleInfo:
    confix_prefix:str     # 角色的配置前缀



ROLE_INFOS:dict[RoleKey,RoleInfo]={
    "insight": RoleInfo(confix_prefix="INSIGHT_ENGINE"),
    "media": RoleInfo(confix_prefix="MEDIA_ENGINE"),
    "host": RoleInfo(confix_prefix="HOST"),
    "report": RoleInfo(confix_prefix="REPORT_ENGINE")
}
