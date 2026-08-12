from fastapi import FastAPI

from app.dependencies import get_lifecycle_manager
from app.routers.rest import system_router, host_router, research_router, report_router
from app.routers.sse import research_progress

from app.exceptions.exception_handlers import register_exception_handlers


async def lifespan(app: FastAPI):
    """应用启停时注册与关闭生命周期管理器"""
    lifecycle_manager = get_lifecycle_manager()
    try:
        lifecycle_manager.register()
        yield
    finally:
        await lifecycle_manager.shutdown()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(research_router.router)
app.include_router(report_router.router)
app.include_router(host_router.router)
app.include_router(system_router.router)
app.include_router(research_progress.router)
