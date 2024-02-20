from typing import Tuple, List

from src.core.base.controller import BaseController
from src.core.mixins.fields import SchemaID
from . import schema as country_schemas
from .crud import state_crud, city_crud
from .models import State, City


class StateController(BaseController):
    async def get_single_state(self, state_id: SchemaID) -> State:
        return await self.crud.get_by_id(_id=state_id)

    async def soft_delete_state(
        self, state_id: SchemaID
    ) -> Tuple[SchemaID, List[SchemaID]]:
        state = await self.crud.get_by_id(_id=state_id)
        city_ids = await city_crud.get_ids(criteria={"state_id": state.id})
        await self.crud.soft_delete_by_id(_id=state.id)
        if city_ids:
            await city_controller.bulk_delete_objs(obj_ids=city_ids)
        return state.id, city_ids


state_controller = StateController(
    crud=state_crud,
    create_out_schema=country_schemas.StateDetailSchema,
    update_out_schema=country_schemas.StateDetailSchema,
)


class CityController(BaseController):
    async def get_single_city(self, city_id: SchemaID) -> City:
        return await self.crud.get_by_id(_id=city_id)

    async def soft_delete_city(self, city_id: SchemaID) -> bool:
        city = await self.crud.get_by_id(_id=city_id)
        return await self.crud.soft_delete_by_id(_id=city.id)

    async def create_city(
        self,
        payload: country_schemas.CityCreateIn,
    ) -> City:
        await state_crud.get_by_id(payload.state_id)
        return await self.crud.create(City(**payload.dict(exclude_none=True)))


city_controller = CityController(
    crud=city_crud,
    create_out_schema=country_schemas.CityDetailSchema,
    update_out_schema=country_schemas.CityDetailSchema,
)
