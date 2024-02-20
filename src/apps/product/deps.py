from typing import Union
from pydantic import BaseModel
from typing import Optional
from fastapi import Query, Request
from src.core.common.exceptions import InvalidQueryParams
from src.core.mixins import SchemaID


class DynamicAttr(BaseModel):
    value: Union[int, bool, str]


def product_filters(
    request: Request,
    user_id: Optional[SchemaID] = Query(None, alias="owner_id"),
    category_id: Optional[SchemaID] = Query(None),
    price_from: Optional[int] = Query(None, ge=0),
    price_to: Optional[int] = Query(None),
):
    criteria = {}
    if user_id:
        criteria["user_id"] = user_id
    if category_id:
        criteria["category_ids"] = category_id
    if price_from:
        criteria["price.value"] = {"$gte": price_from}
    if price_to:
        criteria["price.value"] = {"$lte": price_to}

    attributes_criteria = []
    try:
        for key, value in request.query_params.items():
            if key.startswith("attr_"):
                value = DynamicAttr(value=value).value
                id = key.lstrip("attr_")
                if id.endswith("_from"):
                    id = id.rstrip("_from")
                    attributes_criteria.append(
                        {
                            "attributes": {
                                "$elemMatch": {"id": id, "value": {"$gte": value}}
                            }
                        }
                    )
                elif id.endswith("_to"):
                    id = id.rstrip("_to")
                    attributes_criteria.append(
                        {
                            "attributes": {
                                "$elemMatch": {"id": id, "value": {"$lte": value}}
                            }
                        }
                    )
                else:
                    attributes_criteria.append(
                        {"attributes": {"$elemMatch": {"id": id, "value": value}}}
                    )
    except ValueError as message:
        raise InvalidQueryParams(detail=[message]) from message
    if attributes_criteria:
        criteria["$and"] = attributes_criteria
    return criteria
