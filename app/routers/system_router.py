from fastapi import APIRouter
from app.schemas.system_schema import ConfigResponse, ConfigUpdateRequest
from app.dependenices import SystemConfigServiceDep

router = APIRouter(prefix="/api/config", tags=["配置信息接口层"])

@router.get(path="", response_model=ConfigResponse)
def get_config_info_endpoint(service: SystemConfigServiceDep):
    config_info_dict = service.get_config_info()
    raise ValueError(f"出错了")
    # return ConfigResponse(config=config_info_dict)


@router.post(path="")
def update_config_info_endpoint(
        config_request: ConfigUpdateRequest,
        service: SystemConfigServiceDep):

    service.update_config_info(config_request.root)  # 从root中获取
