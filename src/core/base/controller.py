from typing import List, Optional, TypeVar

from pydantic import BaseModel

from src.core.mixins import SchemaID
from src.core.ordering import OldOrdering, Ordering
from src.core.pagination import Pagination
from .crud import BaseCRUD
from .exception import EntitiesNotFound
from .schema import CommonExportCsvSchemaOut
from ..common import exceptions
from ..csv_utils import write_csv_file

T = TypeVar("T", bound=BaseModel)

CREATE_OUT_SCHEMA: Optional[T] = BaseModel()
CREATE_IN_SCHEMA: Optional[T] = BaseModel()
GET_OUT_SCHEMA: Optional[T] = BaseModel()
GET_SUB_LIST_OUT_SCHEMA: Optional[T] = BaseModel()
UPDATE_IN_SCHEMA: Optional[T] = BaseModel()
UPDATE_OUT_SCHEMA: Optional[T] = BaseModel()


class BaseController(object):
    def __init__(
        self,
        crud: BaseCRUD,
        create_out_schema: CREATE_OUT_SCHEMA = None,
        create_in_schema: CREATE_IN_SCHEMA = None,
        get_out_schema: GET_OUT_SCHEMA = None,
        get_sub_list_out_schema: GET_SUB_LIST_OUT_SCHEMA = None,
        update_in_schema: UPDATE_IN_SCHEMA = None,
        update_out_schema: UPDATE_OUT_SCHEMA = None,
    ):
        self.crud = crud
        self.create_model = crud.create_db_model
        self.update_model = crud.update_db_model
        self.read_model = crud.read_db_model
        self.get_out_schema = get_out_schema or crud.read_db_model
        self.get_sub_list_out_schema = get_sub_list_out_schema or self.get_out_schema
        self.create_in_schema = create_in_schema or crud.create_db_model
        self.create_out_schema = create_out_schema or self.get_out_schema
        self.update_in_schema = update_in_schema or crud.update_db_model
        self.update_out_schema = update_out_schema or self.get_out_schema

    async def create_new_obj(
        self, new_data: CREATE_IN_SCHEMA, **kwargs
    ) -> CREATE_OUT_SCHEMA:
        return await self.crud.create(
            self.create_model(**new_data.dict(exclude_none=True), **kwargs)
        )

    async def get_single_obj(self, **kwargs) -> GET_OUT_SCHEMA:
        criteria = dict(**kwargs) if kwargs else {}
        criteria["is_deleted"] = {"$ne": True}
        return await self.crud.get_object(criteria=criteria)

    async def update_single_obj(
        self,
        criteria: dict,
        new_data: Optional[T],
    ) -> Optional[T]:
        stored_item_model = await self.crud.get_object_in_model(criteria=criteria)
        data_dict = new_data.dict(exclude_unset=True)
        updated_item = stored_item_model.copy(update=data_dict).dict()
        (
            updated_obj,
            is_updated,
        ) = await self.crud.default_update_and_get(
            criteria=criteria,
            new_doc=updated_item,
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return updated_obj

    async def update_create_single_obj(
        self,
        criteria: dict,
        new_data: Optional[T],
    ) -> Optional[T]:
        stored_item_model = await self.crud.get_object_in_model(
            criteria=criteria, raise_exception=False
        )
        data_dict = new_data.dict(exclude_unset=True)
        if stored_item_model:
            updated_item = stored_item_model.copy(update=data_dict).dict()
            (
                updated_obj,
                is_updated,
            ) = await self.crud.default_update_and_get(
                criteria=criteria, new_doc=updated_item
            )
            if not is_updated:
                raise exceptions.UpdateFailed
        else:
            updated_obj = await self.crud.create(self.create_model(**data_dict))
        return self.update_out_schema(**updated_obj.dict())

    async def soft_delete_obj(self, **kwargs) -> bool:
        is_deleted = await self.crud.soft_delete(criteria=dict(**kwargs))
        if not is_deleted:
            raise exceptions.DeleteFailed
        return is_deleted

    async def hard_delete_obj(self, **kwargs) -> bool:
        is_deleted = await self.crud.hard_delete(criteria=dict(**kwargs))
        if not is_deleted:
            raise exceptions.DeleteFailed
        return is_deleted

    async def soft_delete_objs(self, **kwargs) -> Optional[bool]:
        return await self.crud.soft_delete_many(criteria=dict(**kwargs))

    async def get_list_objs(
        self,
        pagination: Pagination,
        ordering: Ordering,
        criteria: dict = None,
        pipeline: List[dict] = None,
        sub_list_schema: Optional[T] = None,
    ):
        if criteria is None:
            criteria = {}
        criteria["is_deleted"] = {"$ne": True}
        return await pagination.paginate(
            crud=self.crud,
            list_item_model=sub_list_schema or self.get_sub_list_out_schema,
            criteria=criteria,
            pipeline=pipeline,
            _sort=await ordering.get_ordering_criteria(),
        )

    async def get_list_objs_without_pagination(self, criteria: dict = None):
        if criteria is None:
            criteria = {}
        criteria["is_deleted"] = {"$ne": True}
        return await self.crud.get_list(criteria=criteria)

    async def bulk_create_objs(self, new_data_objs: List[T], **kwargs) -> List[T]:
        created_items = []
        for new_data in new_data_objs:
            created = await self.crud.create(
                self.create_model(**new_data.dict(exclude_none=True), **kwargs)
            )
            created_items.append(created)
        return created_items

    async def bulk_update_objs(
        self,
        obj_ids: List[SchemaID],
        new_data: UPDATE_IN_SCHEMA,
        id_field: Optional[str] = "_id",
    ):
        new_obj_dict = self.update_model(**new_data.dict(exclude_none=True)).dict(
            exclude_none=True, exclude={id_field}
        )
        (
            updated_objs,
            is_updated,
        ) = await self.crud.default_update_many_and_get(
            criteria={id_field: {"$in": obj_ids}}, new_doc=new_obj_dict
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return updated_objs

    async def bulk_delete_objs(
        self,
        obj_ids: List[SchemaID],
        id_field: Optional[str] = "_id",
    ):
        return await self.crud.bulk_soft_delete(obj_ids=obj_ids, id_field=id_field)

    async def bulk_hard_delete_objs(
        self,
        obj_ids: List[SchemaID],
        id_field: Optional[str] = "_id",
    ):
        return await self.crud.hard_delete_many(criteria={id_field: {"$in": obj_ids}})

    async def export_csv(
        self, files_path, entity_name, criteria=None
    ) -> CommonExportCsvSchemaOut:
        if criteria is None:
            criteria = {}
        entities, fieldnames = await self.crud.export_dict_and_keys_join_aggregate(
            criteria=criteria
        )
        if not entities:
            raise EntitiesNotFound
        path = f"{files_path}/export_{entity_name}.csv"
        write_csv_file(path, entities, fieldnames)
        return CommonExportCsvSchemaOut(url=path)
