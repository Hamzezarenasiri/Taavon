import json
from typing import List, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Path,
    Query,
    Security,
    status,
    BackgroundTasks,
)
from fastapi.responses import Response as StarletteResponse

from src.apps.auth.deps import get_current_user
from src.apps.file import schema as file_schema
from src.apps.file.controller import file_controller
from src.apps.user.models import User
from src.core.base.schema import BulkDeleteIn, PaginatedResponse, Response
from src.core.mixins.fields import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import (
    common_responses,
    response_413,
)
from src.core.utils import return_on_failure
from src.core.validators import file_validation
from src.main.config import app_settings, collections_names

file_router = APIRouter()
entity = collections_names.FILE


@file_router.post(
    "",
    # description="file_category : product || gallery",
    status_code=status.HTTP_200_OK,
    responses={**common_responses, **response_413},
    response_model=Response[file_schema.FileCreateOut],
)
@return_on_failure
async def upload_file(
    background_tasks: BackgroundTasks,
    payload: Optional[str] = Body(
        default=None,
        example={
            "alt": {"EN": "string"},
            # "file_category": "product",
        },
    ),
    file=Depends(file_validation),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "create"],
    ),
) -> Response[file_schema.FileCreateOut]:
    path = app_settings.DEFAULT_FILES_PATH
    meta_fields = (
        file_schema.FileUploadDataIn(**json.loads(payload)) if payload else None
    )
    result = await file_controller.upload_file(
        file=file,
        path=path,
        current_user=current_user,
        meta_fields=meta_fields,
        background_tasks=background_tasks,
    )
    return Response[file_schema.FileCreateOut](data=result)


@file_router.patch(
    "/{file_id}/meta",
    description="Save file metas like: alt text",
    status_code=status.HTTP_200_OK,
    responses={**common_responses},
    response_model=Response[file_schema.FileUpdateOut],
)
@return_on_failure
async def update_file_meta(
    file_meta: file_schema.FileUpdateIn,
    file_id: SchemaID = Path(...),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
) -> Response[file_schema.FileUpdateOut]:
    result = await file_controller.update_file_meta(
        file_id=file_id, file_meta=file_meta, current_user=current_user
    )
    return Response[file_schema.FileUpdateOut](data=result)


@file_router.delete(
    "",
    description="Delete files using provided ids",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **common_responses,
    },
)
@return_on_failure
async def bulk_delete_files(
    payload: BulkDeleteIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    await file_controller.soft_delete_files(
        current_user=current_user, obj_ids=payload.ids
    )
    return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@file_router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
    response_model=Response[PaginatedResponse[List[file_schema.FileGetListOut]]],
    description="Get the list of files",
)
@return_on_failure
async def get_files(
    search: Optional[str] = Query(None, alias="search", name="Search"),
    # file_category: Optional[FileCategoryEnum] = Query(None, enum=ALL_FILE_CATEGORIES),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "list"],
    ),
):
    criteria = {}
    # if file_category:
    #     criteria.update({"file_category": file_category})
    result_data = await file_controller.get_files(
        current_user=current_user,
        search=search,
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[file_schema.FileGetListOut]]](
        data=result_data
    )
