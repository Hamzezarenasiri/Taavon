from typing import Optional

from src.core.base.controller import BaseController
from src.core.common.exceptions import UpdateFailed
from src.core.mixins import SchemaID
from . import schema as store_schema
from .crud import store_crud
from .models import Store
from ..common.constants import ConfirmStatusEnum
from ..user.models import User


class StoreController(BaseController):
    async def get_single_store(
        self,
        target_store_id: SchemaID,
        criteria: Optional[dict] = None,
    ) -> store_schema.StoreGetOut:
        return await store_crud.get_joined(
            target_id=target_store_id,
            criteria=criteria,
        )

    async def update_single_store(
        self,
        target_id: SchemaID,
        new_store_data: store_schema.StoreUpdateIn,
    ) -> store_schema.StoreUpdateOut:
        new_store_dict = new_store_data.dict()
        (
            updated_store,
            is_updated,
        ) = await store_crud.default_update_and_get(
            criteria={"id": target_id}, new_doc=new_store_dict
        )
        if not is_updated:
            raise UpdateFailed
        updated_store = await store_crud.get_joined(
            target_id=target_id,
            criteria={"id": updated_store.id},
        )
        return store_schema.StoreUpdateOut(**updated_store)

    async def create_new_obj(
        self, new_data: store_schema.StoreCreateIn, **kwargs
    ) -> store_schema.StoreCreateOut:
        return await self.crud.create(
            self.create_model(**new_data.dict(exclude_none=True), **kwargs)
        )


store_controller = StoreController(
    crud=store_crud,
)
