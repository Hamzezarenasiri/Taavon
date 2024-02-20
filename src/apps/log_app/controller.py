from datetime import datetime
from typing import List, Optional

from pymongo import InsertOne

from src.apps.language.constants import LanguageEnum, MultiLanguageField
from src.apps.log_app import schema as log_schema
from src.apps.log_app.crud import logs_crud
from src.apps.log_app.constants import LogActionEnum
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse
from src.core.mixins.fields import SchemaID
from src.core.pagination import Pagination
from src.main.config import CollectionsNames


class LogController(BaseController):
    async def get_logs(
        self,
        language: LanguageEnum,
        pagination: Optional[Pagination] = None,
        criteria: Optional[dict] = None,
        action: Optional[List[LogActionEnum]] = None,
        action_by: Optional[SchemaID] = None,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
    ) -> PaginatedResponse[List[log_schema.LogGetListSchema]]:
        pipeline = await logs_crud.get_logs_pipeline(
            language=language,
            criteria=criteria,
            action=action,
            action_by=action_by,
            from_datetime=from_datetime,
            to_datetime=to_datetime,
        )

        return await pagination.paginate(
            crud=logs_crud,
            list_item_model=log_schema.LogGetListSchema,
            pipeline=pipeline,
        )

    async def get_single_log(
        self,
        target_obj_id: SchemaID,
        language: Optional[LanguageEnum] = None,
    ):
        return await self.crud.get_single_log(
            criteria=dict(id=target_obj_id),
            schema=self.get_out_schema,
            language=language,
        )

    async def get_single_log_action_by(
        self,
        target_obj_id: SchemaID,
        action_by: SchemaID,
        language: Optional[LanguageEnum] = None,
    ):
        return await self.crud.get_single_log(
            criteria=dict(id=target_obj_id, action_by=action_by),
            schema=self.get_out_schema,
            language=language,
        )

    async def create_log(
        self,
        action: LogActionEnum,
        action_by: SchemaID,
        entity: str,
        entity_id: Optional[SchemaID] = None,
        meta: Optional[dict] = None,
        description: Optional[MultiLanguageField] = None,
    ):
        if meta is None:
            meta = {}
        await self.crud.create(
            self.create_model(
                action=action,
                action_by=action_by,
                entity=entity,
                entity_id=entity_id,
                meta=meta,
                description=description,
            )
        )

    async def bulk_create_log(
        self,
        action: LogActionEnum,
        action_by: SchemaID,
        entity: CollectionsNames,
        meta: Optional[dict] = None,
        description: Optional[MultiLanguageField] = None,
        entity_ids: Optional[List[SchemaID]] = None,
    ):
        if entity_ids is None:
            entity_ids = []
        bulk_request_list = [
            InsertOne(
                self.create_model(
                    action=action,
                    action_by=action_by,
                    entity=entity,
                    entity_id=entity_id,
                    meta=meta,
                    description=description,
                ).dict(exclude_none=True)
            )
            for entity_id in entity_ids
        ]
        await self.crud.bulk_write(bulk_request_list)


log_controller = LogController(
    crud=logs_crud,
    get_out_schema=log_schema.LogGetOut,
    get_sub_list_out_schema=log_schema.LogGetListSchema,
)
