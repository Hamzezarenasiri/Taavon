from typing import Dict, List

from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse
from src.core.common import exceptions
from src.core.ordering import OldOrdering, Ordering
from src.core.pagination import Pagination
from .crud import languages_crud
from .schema import LanguageGetOut


class LanguageController(BaseController):
    async def update_language_messages_put(
        self, language_code: str, messages: Dict[str, str]
    ) -> LanguageGetOut:
        is_updated = await self.crud.update(
            criteria=dict(code=language_code),
            new_doc=dict(messages=messages),
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return await self.get_single_obj(code=language_code)

    async def update_language_messages_patch(
        self, language_code: str, messages: Dict[str, str]
    ) -> LanguageGetOut:
        new_doc = {f"messages.{k}": v for k, v in messages.items()}
        is_updated = await self.crud.update(
            criteria=dict(code=language_code),
            new_doc=new_doc,
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return await self.get_single_obj(code=language_code)

    async def get_languages(
        self,
        pagination: Pagination,
        ordering: Ordering,
    ) -> PaginatedResponse[List[LanguageGetOut]]:
        criteria = {}
        return await pagination.paginate(
            crud=languages_crud,
            list_item_model=LanguageGetOut,
            criteria=criteria,
            _sort=await ordering.get_ordering_criteria(),
        )


language_controller = LanguageController(
    crud=languages_crud,
    get_out_schema=LanguageGetOut,
)
