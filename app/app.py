from fastapi import FastAPI

from app.dependencies import get_lifecycle_manager
from app.routers import system_router

from app.exceptions.exception_handlers import register_exception_handlers


async def lifespan(app: FastAPI):
    """应用启停时注册与关闭生命周期管理器。"""
    lifecycle_manager = get_lifecycle_manager()
    try:
        lifecycle_manager.register()
        yield
    finally:
        await lifecycle_manager.shutdown()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(system_router.router)
