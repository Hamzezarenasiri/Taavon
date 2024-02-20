import asyncio
from typing import List, Optional, Tuple, Type, TypeVar, Union

from fastapi import Query
from fastapi.requests import Request
from pydantic import BaseModel

from src.core.base.crud import BaseCRUD
from src.core.base.schema import PaginatedResponse

ModelT = TypeVar("ModelT", bound=BaseModel)


class Pagination(object):
    default_offset = 0
    default_limit = 10
    max_offset = None
    max_limit = 500

    def __init__(
        self,
        request: Request,
        offset: int = Query(default=default_offset, ge=0, le=max_offset),
        limit: int = Query(default=default_limit, ge=1, le=max_limit),
    ):
        self.request = request
        self.offset = offset
        self.limit = limit
        self.crud = None
        self.list_item_model = None
        self.count = None
        self.list = []

    async def get_count(self, criteria: dict = None) -> int:
        if criteria is None:
            criteria = {}
        self.count = await self.crud.count(criteria=criteria)
        return self.count

    def get_next_url(self) -> Union[str, None]:
        if self.offset + self.limit >= self.count:
            return None
        return str(
            self.request.url.include_query_params(
                limit=self.limit,
                offset=self.offset + self.limit,
            )
        )

    def get_previous_url(self) -> Union[str, None]:
        if self.offset <= 0:
            return None

        if self.offset - self.limit <= 0:
            return str(self.request.url.remove_query_params(keys=["offset"]))

        return str(
            self.request.url.include_query_params(
                limit=self.limit,
                offset=self.offset - self.limit,
            )
        )

    async def get_list(self, criteria: dict = None, _sort=None) -> list:
        self.list = await self.crud.get_list(
            criteria=criteria,
            limit=self.limit,
            skip=self.offset,
            sort=_sort,
        )
        return self.list

    async def get_list_aggregate(
        self,
        pipeline: List[dict] = None,
        criteria: dict = None,
        _sort: dict = None,
        **kwargs,
    ) -> Tuple[List[dict], int]:
        if not pipeline:
            pipeline = []
        if criteria:
            pipeline.insert(0, {"$match": criteria})
        _list_pipeline = [
            {"$skip": self.offset},
            {"$limit": self.limit},
        ]
        if _sort:
            _list_pipeline.insert(0, {"$sort": _sort})
        paginate_pipe = [
            {
                "$facet": {
                    "_list": _list_pipeline,
                    "page_info": [
                        {"$group": {"_id": None, "count": {"$sum": 1}}},
                    ],
                },
            }
        ]
        pipeline += paginate_pipe
        result = (
            await self.crud.aggregate(
                pipeline=pipeline,
                **kwargs,
            )
        )[0]
        self.list = result["_list"]
        self.count = result["page_info"][0]["count"] if result["page_info"] else 0
        return self.list, self.count

    async def paginate(
        self,
        crud: BaseCRUD,
        list_item_model: Type[BaseModel],
        criteria: dict = None,
        pipeline: List[dict] = None,
        _sort: Optional[List[tuple]] = None,
        by_alias=True,
        **kwargs,
    ) -> PaginatedResponse[List[Type[ModelT]]]:
        self.crud = crud
        self.list_item_model = list_item_model
        if pipeline:
            if _sort and isinstance(_sort, List):
                _sort = dict(_sort)
            await self.get_list_aggregate(
                pipeline=pipeline,
                _sort=_sort,
                criteria=criteria,
                **kwargs,
            )
            items = [
                self.list_item_model(**item).dict(exclude_none=True, by_alias=by_alias)
                for item in self.list
            ]
        else:
            await asyncio.gather(
                self.get_list(criteria=criteria, _sort=_sort),
                self.get_count(criteria=criteria),
            )
            items = [
                self.list_item_model(**item.dict(exclude_none=True, by_alias=by_alias))
                for item in self.list
            ]
        return PaginatedResponse[List[list_item_model]](
            total=self.count,
            offset=self.offset,
            limit=self.limit,
            next=self.get_next_url(),
            previous=self.get_previous_url(),
            result=items,
        )
