from typing import Union
from pydantic import BaseModel
from typing import Optional
from fastapi import Query, Request
from src.core.common.exceptions import InvalidQueryParams
from src.core.mixins import SchemaID


class DynamicAttr(BaseModel):
    value: Union[int, bool, str]


def report_filters(
    request: Request,
    report_filter_id: Optional[SchemaID] = Query(None),
):
    criteria = {}
    if report_filter_id:
        criteria["_id"] = report_filter_id

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
