import re
from typing import List

from fastapi import (
    APIRouter,
    Security,
    Depends,
    Query,
    Path,
)
from persiantools.characters import ar_to_fa

from src.apps.auth.deps import get_current_user
from src.apps.product import schema as product_schemas
from src.apps.product.controller import product_controller
from src.apps.product.crud import product_crud
from src.apps.product.deps import product_filters
from src.apps.user.models import User
from src.core.base.schema import Response, PaginatedResponse
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

product_router = APIRouter()
entity = collections_names.PRODUCT


@product_router.get(
    "/{product_id}",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[product_schemas.ProductDetailSchema],
    description="by `hamzezn`",
)
@return_on_failure
async def get_product(
    product_id: SchemaID = Path(...),
    _: User = Security(get_current_user, scopes=[entity, "read"]),
):
    product = await product_crud.get_product_joined(
        product_id=product_id, criteria={"is_deleted": {"$ne": True}}
    )
    return Response[product_schemas.ProductDetailSchema](data=product)


@product_router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[product_schemas.ProductListSchema]]],
    description="by `hamzezn`",
)
@return_on_failure
async def get_products(
    current_user: User = Security(get_current_user, scopes=[entity, "list"]),
    filters: dict = Depends(product_filters),
    search: str = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {
        "organization_ids": current_user.organization_id,
        "is_enabled": True,
        **filters,
    }
    if search:
        search = ar_to_fa(search)
        criteria["title"] = re.compile(search, re.IGNORECASE)
    products = await product_controller.get_products_joined(
        pagination=pagination,
        ordering=ordering,
        schema=product_schemas.ProductListSchema,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[product_schemas.ProductListSchema]]](
        data=products
    )
