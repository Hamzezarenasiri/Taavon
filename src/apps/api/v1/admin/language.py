from typing import List

from fastapi import APIRouter, Security, status, BackgroundTasks
from fastapi.param_functions import Depends
from fastapi.params import Path

from src.apps.auth.deps import get_current_user
from src.apps.language.constants import ALL_LANGUAGES
from src.apps.language.controller import language_controller
from src.apps.language.schema import (
    LanguageGetOut,
    LanguageListOut,
    LanguageMessagesUpdateIn,
)
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.user.models import User
from src.core.base.schema import PaginatedResponse, Response
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

language_router = APIRouter()
entity = collections_names.LANGUAGE


@language_router.get(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    status_code=status.HTTP_200_OK,
    response_model=Response[PaginatedResponse[List[LanguageListOut]]],
    description="Get the list of languages and their code",
)
@return_on_failure
async def get_languages(
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    result_data = await language_controller.get_languages(
        pagination=pagination, ordering=ordering
    )
    return Response[PaginatedResponse[List[LanguageListOut]]](data=result_data)


@language_router.get(
    "/{language_code}/",
    responses={
        **common_responses,
    },
    response_model=Response[LanguageGetOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_language(
    language_code: str = Path(
        enum=ALL_LANGUAGES,
    ),
):
    result_data = await language_controller.get_single_obj(code=language_code)
    return Response[LanguageGetOut](data=result_data)


@language_router.patch(
    "/{language_code}/",
    responses={
        **common_responses,
    },
    response_model=Response[LanguageGetOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def patch_update_language_messages(
    background_tasks: BackgroundTasks,
    payload: LanguageMessagesUpdateIn,
    language_code: str = Path(
        enum=ALL_LANGUAGES,
    ),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result_data = await language_controller.update_language_messages_patch(
        language_code=language_code, messages=payload.messages
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=language_code,
    )
    return Response[LanguageGetOut](data=result_data)


@language_router.put(
    "/{language_code}/",
    responses={
        **common_responses,
    },
    response_model=Response[LanguageGetOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def put_update_language_messages(
    background_tasks: BackgroundTasks,
    payload: LanguageMessagesUpdateIn,
    language_code: str = Path(
        enum=ALL_LANGUAGES,
    ),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result_data = await language_controller.update_language_messages_put(
        language_code=language_code, messages=payload.messages
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=language_code,
    )
    return Response[LanguageGetOut](data=result_data)
