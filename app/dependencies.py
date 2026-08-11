from typing import Annotated
from fastapi import Depends

from app.services.host.host_service import HostService
from app.services.lifecycle.lifecycle_service import AppLifecycleManager
from app.services.system.system_service import SystemConfigService

_config_service = SystemConfigService()


def get_config_service():
    return _config_service


SystemConfigServiceDep = Annotated[SystemConfigService, Depends(get_config_service)]

_host_service = HostService()


def get_host_service() -> HostService:
    """提供全局主持人研判服务单例。"""
    return _host_service


HostServiceDep = Annotated[HostService, Depends(get_host_service)]

_lifecycle_manager = AppLifecycleManager(_host_service)


def get_lifecycle_manager() -> AppLifecycleManager:
    """提供全局生命周期管理器单例。"""
    return _lifecycle_manager
