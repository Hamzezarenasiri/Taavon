from fastapi import APIRouter

from .admin import admin_router
from .common import common_router
from .. import home_router

router_v1 = APIRouter()
router_v1.include_router(home_router, tags=["Home"])
router_v1.include_router(common_router, tags=["Common"])
router_v1.include_router(admin_router, prefix="/admin")
