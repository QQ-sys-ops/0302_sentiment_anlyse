from fastapi import  FastAPI
from app.routers import  system_router

from app.exceptions.exception_handlers import register_exception_handlers
app= FastAPI()

register_exception_handlers(app)



app.include_router(system_router.router)




