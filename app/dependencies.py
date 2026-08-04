from typing import Annotated
from fastapi import  Depends

from app.services.system.system_service import SystemConfigService

_config_service= SystemConfigService()


def  get_config_service():
    return  _config_service



SystemConfigServiceDep= Annotated[SystemConfigService,Depends(get_config_service)]
