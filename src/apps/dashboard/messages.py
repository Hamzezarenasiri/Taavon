from enum import Enum
from typing import List
from src.fastapi_babel import _


class DashboardMessageEnum(str, Enum):
    create_new_dashboard: str = _("Create new dashboard")
    get_dashboards: str = _("Get dashboards")
    get_single_dashboard: str = _("Get single dashboard")
    update_dashboard: str = _("Update dashboard")


class DashboardErrorMessageEnum(str, Enum):
    dashboard_not_found: str = _("Dashboard not found")
    parent_dashboard_not_found: str = _("Parent dashboard not found")


class DashboardNotFoundErrorDetailEnum(list, Enum):
    dashboard_not_found: List[str] = [DashboardErrorMessageEnum.dashboard_not_found]
    parent_dashboard_not_found: List[str] = [
        DashboardErrorMessageEnum.parent_dashboard_not_found
    ]
