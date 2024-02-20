from fastapi import APIRouter

from .auth import auth_router
from .city import router as city_router
from .state import router as state_router

common_router = APIRouter()

common_router.include_router(auth_router, prefix="/auth")
common_router.include_router(state_router, prefix="/states")
common_router.include_router(city_router, prefix="/cities")

