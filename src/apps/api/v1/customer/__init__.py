from fastapi import APIRouter

from .auth import customer_auth_router
from .category import category_router
from .file import file_router
from .invoice import invoice_router
from .notification import notification_router
from .product import product_router
from .profile import profile_router
from .store import store_router

customer_router = APIRouter()

# customer_router.include_router(category_router, prefix="/categories", tags=["Categories"])
# customer_router.include_router(config_router, prefix="/configs")
# customer_router.include_router(notification_router, prefix="/notifications")
# customer_router.include_router(product_router, prefix="/products", tags=["Customer Products"])
# customer_router.include_router(report_router, prefix="/reports", tags=["Customer Reports"])
customer_router.include_router(
    customer_auth_router, prefix="/auth", tags=["Customer Auth"]
)

customer_router.include_router(file_router, prefix="/files", tags=["Customer Files"])
customer_router.include_router(
    invoice_router, prefix="/invoices", tags=["Customer Invoices"]
)
customer_router.include_router(
    profile_router, prefix="/me", tags=["Customer Profile & Permissions"]
)
# customer_router.include_router(
#     organization_router, prefix="/organizations", tags=["Customer Organizations"]
# )
customer_router.include_router(store_router, prefix="/stores", tags=["Customer Stores"])
