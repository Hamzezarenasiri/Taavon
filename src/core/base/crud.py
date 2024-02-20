import abc
from typing import List, Optional, Tuple, Type, TypeVar, Union, Any

from beanie import Document
from beanie.odm.queries.find import FindMany
from fastapi import HTTPException, status
from pydantic import BaseModel
from pymongo.results import BulkWriteResult, UpdateResult

from src.core.async_tools import force_sync
from src.core.base.schema import BaseSchema
from src.core.common import exceptions
from src.core.mixins import DB_ID, SchemaID
from src.services import global_services
from src.services.db.mongodb import UpdateOperatorsEnum


class BaseCRUD(metaclass=abc.ABCMeta):
    T = TypeVar("T", bound=BaseModel)
    T_SCHEMA = TypeVar("T_SCHEMA", bound=BaseSchema)
    create_db_model: Type[T]
    read_db_model: Type[T]
    update_db_model: Type[T]

    def __init__(
        self,
        create_db_model: Type[T],
        read_db_model: Type[T],
        update_db_model: Optional[Type[T]] = None,
    ):
        self.create_db_model = create_db_model
        self.read_db_model = read_db_model
        self.update_db_model = update_db_model

    async def get_an_object(
        self,
        criteria: dict = None,
        projection: Optional[dict] = None,
        raise_exception: Optional[bool] = True,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> Union[T, dict]:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        if projection:
            result = await self.read_db_model.find_one(
                criteria, projection_model=projection
            )
        else:
            result = await self.read_db_model.find_one(criteria)
        if not result and raise_exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.read_db_model.Meta.entity_name} not found.",
            )
        return result

    async def get_object(
        self,
        criteria: dict = None,
        projection: Optional[dict] = None,
        raise_exception: Optional[bool] = True,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> Union[T, dict]:
        return await self.get_an_object(
            criteria=criteria,
            projection=projection,
            raise_exception=raise_exception,
            deleted=deleted,
            **kwargs,
        )

    async def get_object_in_model(
        self,
        criteria: dict = None,
        raise_exception: Optional[bool] = True,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> T:
        return await self.get_an_object(
            criteria=criteria,
            raise_exception=raise_exception,
            deleted=deleted,
            **kwargs,
        )

    async def get_last_object(
        self,
        criteria: dict,
        sort_field: Optional[str] = "_id",
        raise_exception: Optional[bool] = True,
    ) -> Optional[T]:
        return await self.get_object(
            criteria=criteria, sort=[(sort_field, -1)], raise_exception=raise_exception
        )

    async def get_by_id(
        self,
        _id: DB_ID,
        criteria: Optional[dict] = None,
        projection: Optional[dict] = None,
        raise_exception: Optional[bool] = True,
        deleted: Optional[bool] = None,
    ) -> Optional[T]:
        if criteria is None:
            criteria = {}
        criteria.update(_id=_id)
        return await self.get_object(
            criteria=criteria,
            projection=projection,
            raise_exception=raise_exception,
            deleted=deleted,
        )

    async def get_or_create(
        self, criteria: dict, another_fields: Optional[dict] = None
    ):
        if not await self.get_object(criteria, raise_exception=False):
            if another_fields:
                criteria |= another_fields
            await self.create(self.create_db_model(**criteria))

    async def exists(
        self,
        criteria: dict = None,
        projection: Optional[dict] = None,
        raise_exception: Optional[bool] = True,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> bool:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        result = await global_services.DB.raw_exists(
            criteria=criteria,
            model=self.read_db_model,
            projection=projection,
            **kwargs,
        )
        if not result and raise_exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.read_db_model.Meta.entity_name} not found.",
            )
        return result

    async def exists_by_id(
        self,
        _id: DB_ID,
        criteria: Optional[dict] = None,
        projection: Optional[dict] = None,
        raise_exception: Optional[bool] = True,
        deleted: Optional[bool] = None,
    ) -> Optional[bool]:
        if criteria is None:
            criteria = {}
        criteria.update(id=_id)
        return await self.exists(
            criteria=criteria,
            projection=projection,
            raise_exception=raise_exception,
            deleted=deleted,
        )

    @force_sync
    async def sync_get_by_id(
        self,
        _id: DB_ID,
        raise_exception: Optional[bool] = True,
        deleted: Optional[bool] = None,
    ) -> Optional[T]:
        return await self.get_by_id(
            _id=_id,
            raise_exception=raise_exception,
            deleted=deleted,
        )

    async def get_list(
        self,
        criteria: dict = None,
        sort: Optional[Any] = None,
        skip: int = 0,
        limit: Optional[int] = None,
        projection: Optional[dict] = None,
        deleted: Optional[bool] = None,
    ) -> List[T]:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        results: FindMany = self.read_db_model.find(
            criteria, projection_model=projection, skip=skip, limit=limit, sort=sort
        )
        result = []
        async for res in results:
            result.append(res)
        return result

    async def get_list_by_ids(
        self,
        ids=Optional[List[DB_ID]],
        skip: int = 0,
        limit: int = 0,
        sort: Optional[list] = None,
        projection: Optional[dict] = None,
        deleted: Optional[bool] = None,
    ) -> Optional[List[T]]:
        return (
            await self.get_list(
                criteria={"_id": {"$in": ids}},
                skip=skip,
                limit=limit,
                sort=sort,
                projection=projection,
                deleted=deleted,
            )
            if ids
            else None
        )

    async def create(
        self,
        obj: Document,
    ) -> T:
        return await obj.insert()

    async def count(self, criteria: Optional[dict] = None) -> int:
        if criteria is None:
            criteria = {}
        return await self.read_db_model.find(criteria).count()

    async def default_update(
        self,
        criteria: dict,
        new_doc: dict,
        operator: UpdateOperatorsEnum = UpdateOperatorsEnum.set_,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> bool:
        is_updated: bool = await self.update(
            upsert=upsert,
            criteria=criteria,
            new_doc=self.update_db_model(**new_doc).dict(exclude_none=True),
            operator=operator,
            deleted=deleted,
            **kwargs,
        )
        return is_updated

    async def default_update_and_get(
        self,
        criteria: dict,
        new_doc: dict,
        operator: UpdateOperatorsEnum = UpdateOperatorsEnum.set_,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[T, bool]:
        is_updated: bool = await self.default_update(
            upsert=upsert,
            criteria=criteria,
            new_doc=new_doc,
            operator=operator,
            deleted=deleted,
            **kwargs,
        )
        result = await self.get_object(criteria=criteria)
        return result, is_updated

    async def default_update_many_and_get(
        self,
        criteria: dict,
        new_doc: dict,
        operator: UpdateOperatorsEnum = UpdateOperatorsEnum.set_,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[List[T], bool]:
        is_updated: bool = await self.update_many(
            criteria=criteria,
            update=new_doc,
            upsert=upsert,
            deleted=deleted,
            operator=operator,
            **kwargs,
        )
        result = await self.get_list(criteria=criteria)
        return result, is_updated

    async def update_and_get(
        self,
        criteria: dict,
        new_doc: dict,
        operator: UpdateOperatorsEnum = UpdateOperatorsEnum.set_,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[T, bool]:
        is_updated: bool = await self.update(
            upsert=upsert,
            criteria=criteria,
            new_doc=new_doc,
            operator=operator,
            deleted=deleted,
            **kwargs,
        )
        result = await self.get_object(criteria=criteria)
        return result, is_updated

    async def update(
        self,
        criteria: dict,
        new_doc: dict,
        operator: Optional[UpdateOperatorsEnum] = UpdateOperatorsEnum.set_,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> bool:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        result: UpdateResult = await self.read_db_model.find(criteria).set(new_doc)
        return bool(result.matched_count)

    async def multi_operations(
        self,
        criteria: dict,
        new_doc: dict,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> bool:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        return await global_services.DB.raw_update_multi_operations(
            upsert=upsert,
            criteria=criteria,
            new_values=new_doc,
            model=self.read_db_model,
            **kwargs,
        )

    async def update_many(
        self,
        criteria: dict,
        update: dict,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> bool:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        result: UpdateResult = await self.read_db_model.find(criteria).set(update)
        return bool(result.matched_count)

    @force_sync
    async def sync_update_many(
        self,
        criteria: dict,
        update: dict,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> bool:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        return await global_services.DB.raw_update_many(
            criteria=criteria,
            new_values=update,
            upsert=upsert,
            model=self.read_db_model,
            **kwargs,
        )

    async def update_many_and_modified_count(
        self,
        criteria: dict,
        update: dict,
        upsert: Optional[bool] = False,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[bool, int, int]:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        result = await global_services.DB.raw_update_many(
            criteria=criteria,
            new_values=update,
            upsert=upsert,
            model=self.read_db_model,
            **kwargs,
        )
        return result.acknowledged, result.matched_count, result.modified_count

    async def soft_delete(
        self,
        criteria: dict,
        deleted: Optional[bool] = None,
        **kwargs,
    ) -> bool:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)
        result = await self.read_db_model.find(criteria).set({"is_deleted": True})
        return bool(result.matched_count)

    async def soft_delete_by_id(
        self,
        _id: DB_ID,
    ):
        return await self.soft_delete(
            criteria={
                "_id": _id,
            },
        )

    async def hard_delete(
        self,
        criteria: dict,
    ) -> bool:
        return await global_services.DB.raw_delete(
            criteria=criteria, model=self.read_db_model
        )

    async def hard_delete_many(
        self,
        criteria: dict,
    ) -> bool:
        return await global_services.DB.raw_delete_many(
            criteria=criteria, model=self.read_db_model
        )

    async def aggregate(self, pipeline: List[dict], **kwargs) -> List[dict]:
        results = self.read_db_model.find().aggregate(aggregation_pipeline=pipeline)
        result = []
        async for res in results:
            result.append(res)
        return result

    async def raw_aggregate_schema(
        self,
        pipeline: List[dict],
        schema: Type[T_SCHEMA],
        model: Type[T] = None,
        **kwargs,
    ):
        return await global_services.DB.raw_aggregate_schema(
            pipeline=pipeline,
            schema=schema,
            model=model or self.read_db_model,
            **kwargs,
        )

    async def aggregate_schema(
        self,
        pipeline: List[dict],
        schema: Type[T_SCHEMA],
        model: Type[T] = None,
        **kwargs,
    ) -> List[T_SCHEMA]:
        return await global_services.DB.raw_aggregate_schema(
            pipeline=pipeline,
            schema=schema,
            model=model or self.read_db_model,
            **kwargs,
        )

    async def distinct(
        self,
        field: str,
        criteria: Optional[dict] = None,
        **kwargs,
    ) -> list:
        return await global_services.DB.raw_distinct(
            field=field,
            criteria=criteria,
            model=self.read_db_model,
            **kwargs,
        )

    async def get_ids(
        self,
        criteria: dict = None,
        target_id_field: str = "_id",
        deleted: Optional[bool] = None,
    ) -> Optional[List[DB_ID]]:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)

        pipeline = [
            {"$match": criteria},
            {"$project": {"_id": f"${target_id_field}"}},
        ]
        ids_dict = await self.aggregate(pipeline=pipeline)
        return [id_dict["_id"] for id_dict in ids_dict]

    async def get_list_of_a_field_values(
        self,
        target_field: str,
        criteria: dict = None,
        deleted: Optional[bool] = None,
    ) -> Optional[List[DB_ID]]:
        if not criteria:
            criteria = {}
        if deleted is not None:
            criteria.update(is_deleted=deleted)

        pipeline = [
            {"$match": criteria},
            {"$project": {"_id": f"${target_field}"}},
            {"$project": {"_id": 0}},
        ]
        ids_dict = await self.aggregate(pipeline=pipeline)
        return [id_dict["_id"] for id_dict in ids_dict]

    async def bulk_soft_delete(
        self,
        obj_ids: List[SchemaID],
        id_field: Optional[str] = "_id",
    ):
        (
            updated_documents,
            is_updated,
        ) = await self.default_update_many_and_get(
            criteria={id_field: {"$in": obj_ids}}, new_doc={"is_deleted": True}
        )
        if not is_updated:
            raise exceptions.DeleteFailed
        return updated_documents

    async def soft_delete_many(
        self,
        criteria: dict,
    ) -> bool:
        return await self.update_many(criteria=criteria, update={"is_deleted": True})

    async def bulk_write(
        self,
        requests,
        **kwargs,
    ) -> BulkWriteResult:
        return await global_services.DB.bulk_write(
            requests=requests,
            model=self.read_db_model,
            **kwargs,
        )

    async def export_dict_and_keys_join_aggregate(
        self, criteria
    ) -> Tuple[List[dict], Optional[list]]:
        entities = await self.get_list(criteria=criteria)
        return [entity.dict() for entity in entities], None
