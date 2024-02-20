import re
from typing import Optional, List

from fastapi import (
    APIRouter,
    Security,
    Depends,
    Query,
)
from persiantools.characters import ar_to_fa

from src.apps.auth.deps import get_optional_current_user
from src.apps.country.controller import city_controller
from src.apps.country.schema import CityListSchema
from src.apps.user.models import User
from src.core.base.schema import Response, PaginatedResponse
from src.core.mixins.fields import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses
from src.core.utils import return_on_failure
from src.main.config import collections_names

entity = collections_names.CITY
router = APIRouter()


@router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[CityListSchema]]],
)
@return_on_failure
async def get_cities(
    _: User = Security(get_optional_current_user),
    state_id: Optional[SchemaID] = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
    search: Optional[str] = Query(None),
):
    criteria = {}
    if search:
        search = ar_to_fa(search)
        if search := re.sub(r"[()\[\]'*+?\\]", "", search):
            criteria = {"name": re.compile(search, re.IGNORECASE)}
    if state_id:
        criteria["state_id"] = state_id
    pipeline = [
        {"$match": criteria},
        {"$addFields": {"id": "$_id"}},
    ]
    cities = await city_controller.get_list_objs(
        pagination=pagination,
        ordering=ordering,
        pipeline=pipeline,
        sub_list_schema=CityListSchema,
    )
    return Response[PaginatedResponse[List[CityListSchema]]](data=cities)
