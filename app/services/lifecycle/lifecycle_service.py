from app.services.host.host_service import HostService
from engines.common.task_manager import research_task_manager


class AppLifecycleManager:
    """应用生命周期管理器:统一启动与关闭后台服务组件及引擎共享资源。"""

    def __init__(self, host_service: HostService) -> None:
        """初始化生命周期管理器并注入依赖组件"""
        self.host_service = host_service

    def register(self) -> None:
        """统一注册并启动所有关联的后台服务组件"""
        # 1. 启动 Host 章节研判监听器
        self.host_service.register_host_listener()

    async def shutdown(self) -> None:
        """统一注销并停止所有关联的后台服务组件,释放持有的资源"""
        # 1. 停止讨论缓冲服务，释放监听
        self.host_service.stop_discussion_buffer()
        # 2. 停止 Host 章节监听 worker
        self.host_service.stop_host_listener()
        # 3. 取消仍在执行的研究/报告后台任务
        await research_task_manager.cancel_all_tasks()
