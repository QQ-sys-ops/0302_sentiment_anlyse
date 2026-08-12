from fastapi import APIRouter
from app.schemas.system_schema import ConfigResponse, ConfigUpdateRequest
from app.dependencies import SystemConfigServiceDep

router = APIRouter(prefix="/api/config", tags=["配置信息接口层"])


@router.get(path="", response_model=ConfigResponse)
def get_config_info_endpoint(service: SystemConfigServiceDep):
    """返回当前系统配置信息"""
    config_info_dict = service.get_config_info()
    return ConfigResponse(config=config_info_dict)


@router.post(path="")
def update_config_info_endpoint(
        config_request: ConfigUpdateRequest,
        service: SystemConfigServiceDep):
    """更新系统配置信息。"""
    service.update_config_info(config_request.root)
