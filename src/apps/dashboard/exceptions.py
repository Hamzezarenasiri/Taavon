from fastapi import status

from src.core.common.exceptions import CustomHTTPException
from .messages import DashboardErrorMessageEnum, DashboardNotFoundErrorDetailEnum

ParentDashboardNotFound = CustomHTTPException(
    detail=DashboardNotFoundErrorDetailEnum.parent_dashboard_not_found,
    message=DashboardErrorMessageEnum.parent_dashboard_not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
DashboardNotFound = CustomHTTPException(
    detail=DashboardNotFoundErrorDetailEnum.dashboard_not_found,
    message=DashboardErrorMessageEnum.dashboard_not_found,
    status_code=status.HTTP_404_NOT_FOUND,
)
