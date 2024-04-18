from fastapi import (
    APIRouter,
    Security,
)

from src.apps.auth.deps import get_current_user
from src.apps.dashboard import schema as dashboard_schema
from src.apps.dashboard.schema import SubContCardStatics
from src.apps.organization.crud import organization_crud
from src.apps.user.constants import DefaultRoleNameEnum
from src.apps.user.crud import users_crud
from src.apps.user.models import User
from src.core.base.schema import (
    Response,
)
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

dashboard_router = APIRouter()
entity = collections_names.DASHBOARD


@dashboard_router.get(
    "/count_cards",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[dashboard_schema.ContCardStatics],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_count_cards_statics(
    _: User = Security(
        get_current_user,
    ),
    # date_gt: Optional[datetime] = Query(None, alias="from", title="From Datetime"),
    # date_lt: Optional[datetime] = Query(None, alias="to", title="To Datetime"),
):
    criteria = {
        # "organization_ids": current_user.organization_id,
        "is_deleted": {"$ne": True},
    }
    # if date_gt and date_lt:
    #     criteria["create_datetime"] = {"$gte": date_gt, "$lte": date_lt}
    #
    # elif date_gt:
    #     criteria["create_datetime"] = {"$gte": date_gt}
    #
    # elif date_lt:
    #     criteria["create_datetime"] = {"$lte": date_lt}
    user_count = await users_crud.count(criteria)
    customer_count = await users_crud.count(
        {"is_deleted": {"$ne": True}, "role": [DefaultRoleNameEnum.CUSTOMER]}
    )
    store_count = await users_crud.count(criteria)
    organization_count = await organization_crud.count(criteria)

    result: list[SubContCardStatics] = [
        SubContCardStatics(
            title="تعداد سازمان ها",
            count=organization_count,
            icon="organization",
        ),
        SubContCardStatics(
            title="تعداد کاربران",
            count=user_count,
            icon="People",
        ),
        SubContCardStatics(
            title="تعداد مشتریان",
            count=customer_count,
            icon="People",
        ),
        SubContCardStatics(
            title="تعداد فروشگاه ها",
            count=store_count,
            icon="files",
        ),
    ]

    return Response[dashboard_schema.ContCardStatics](
        data=dashboard_schema.ContCardStatics(result=result), message="OK"
    )
