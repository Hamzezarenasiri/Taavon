import re
from typing import List, Optional

from fastapi import (
    APIRouter,
    Security,
    Depends,
    Query,
)
from persiantools.characters import ar_to_fa

from src.apps.auth.deps import get_optional_current_user
from src.apps.country.controller import state_controller
from src.apps.country.schema import StateListSchema
from src.apps.user.models import User
from src.core.base.schema import Response, PaginatedResponse
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses
from src.core.utils import return_on_failure
from src.main.config import collections_names

entity = collections_names.STATE
router = APIRouter()


@router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[StateListSchema]]],
)
@return_on_failure
async def get_states(
    _: User = Security(get_optional_current_user),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
    search: Optional[str] = Query(None),
):
    criteria = {}
    if search:
        search = ar_to_fa(search)
        if search := re.sub(r"[()\[\]'*+?\\]", "", search):
            criteria = {"name": re.compile(search, re.IGNORECASE)}
    pipeline = [
        {"$match": criteria},
        {"$addFields": {"id": "$_id"}},
    ]

    states = await state_controller.get_list_objs(
        pagination=pagination,
        ordering=ordering,
        pipeline=pipeline,
        sub_list_schema=StateListSchema,
    )
    return Response[PaginatedResponse[List[StateListSchema]]](data=states)
