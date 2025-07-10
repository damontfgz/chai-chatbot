from fastapi import APIRouter
from app.services.chat_v1 import router as chat_api_router
from app.services.healthcheck import router as healthcheck_api_router

api_router = APIRouter()
api_router.include_router(chat_api_router, prefix="/v1")
api_router.include_router(healthcheck_api_router)

