from fastapi import APIRouter

from .invoice import invoice_router
from .product import product_router
from .auth import admin_auth_router
from .category import category_router
from .city import router as city_router
from .config import config_router
from .dashboard import dashboard_router
from .entity import entity_router
from .file import file_router
from .language import language_router
from .notification import notification_router
from .organization import organization_router
from .profile import profile_router
from .report import report_router
from .role import role_router
from .state import router as state_router
from .store import store_router
from .users import user_router

admin_router = APIRouter()

# admin_router.include_router(category_router, prefix="/categories", tags=["Categories"])
# admin_router.include_router(config_router, prefix="/configs")
# admin_router.include_router(notification_router, prefix="/notifications")
# admin_router.include_router(product_router, prefix="/products", tags=["Products"])
# admin_router.include_router(report_router, prefix="/reports", tags=["Reports"])
admin_router.include_router(admin_auth_router, prefix="/auth", tags=["Auth"])
admin_router.include_router(city_router, prefix="/cities", tags=["Cities"])
admin_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
admin_router.include_router(entity_router, prefix="/entities", tags=["Entities"])
admin_router.include_router(file_router, prefix="/files", tags=["Files"])
admin_router.include_router(invoice_router, prefix="/invoices", tags=["Invoices"])
admin_router.include_router(
    profile_router, prefix="/me", tags=["Profile & Permissions"]
)
# admin_router.include_router(
#     organization_router, prefix="/organizations", tags=["Organizations"]
# )
admin_router.include_router(role_router, prefix="/roles", tags=["Roles"])
admin_router.include_router(state_router, prefix="/states", tags=["States"])
admin_router.include_router(store_router, prefix="/stores", tags=["Stores"])
admin_router.include_router(user_router, prefix="/users", tags=["Users"])
