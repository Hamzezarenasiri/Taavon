import re
from typing import List, Optional, Tuple, TypeVar

from fastapi import Query, Request
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class Ordering:
    def __init__(self, prior_fields=None, default_field="-create_datetime"):
        self.prior_fields = prior_fields
        self.default_field = default_field

    def __call__(
        self,
        fields: str = Query(
            None,
            description="use - for descending sorting otherwise only field name seprated by ,",
            example="name,-age,-create_datetime",
            alias="ordering",
        ),
    ):
        self.fields = fields
        return self

    @property
    def _ordering_fields(self) -> List[str]:
        ordering_fields = [self.default_field]
        if self.prior_fields:
            ordering_fields = self.prior_fields.split(",")
        if self.fields:
            if self.prior_fields:
                ordering_fields.extend(self.fields.split(","))
            else:
                ordering_fields = self.fields.split(",")
        return ordering_fields

    def _get_ordering_filter(self, field: str) -> Tuple[str, int]:
        return (field[1:], -1) if field.startswith("-") else (field, 1)

    async def get_ordering_criteria(self) -> List[Tuple[str, int]]:
        return [self._get_ordering_filter(field) for field in self._ordering_fields]


class OldOrdering(object):
    default_sort_by = "desc(create_datetime),desc(_id)"

    def __init__(
        self,
        request: Request,
        sort_by: str = Query(
            default=default_sort_by,
            description="desc(field_name),asc(field_name)",
            alias="sort_by",
        ),
    ):
        self.request = request
        self.sort_by = sort_by

    async def get_ordering_criteria(
        self,
    ) -> Optional[List[Tuple]]:
        criteria = []
        if self.sort_by:
            fields = self.sort_by.split(",")
            for field in fields:
                field_name = re.findall(r"\(.*?\)", field)
                field_name = field_name[0]
                field_name = field_name.replace("(", "")
                field_name = field_name.replace(")", "")
                order = field.replace(f"({field_name})", "")
                order_mongo = 1 if order == "asc" else -1
                criteria.append((field_name, order_mongo))

        return criteria or None
