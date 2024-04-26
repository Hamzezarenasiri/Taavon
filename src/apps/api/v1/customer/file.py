from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Security,
    status,
    BackgroundTasks,
)

from src.apps.auth.deps import get_current_user
from src.apps.file import schema as file_schema
from src.apps.file.controller import file_controller
from src.apps.user.models import User
from src.core.base.schema import PaginatedResponse, Response
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
    # payload: Optional[str] = Body(
    #     default=None,
    #     example={
    #         "alt": {"EN": "string"},
    #         # "file_category": "product",
    #     },
    # ),
    file=Depends(file_validation),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "create"],
    ),
) -> Response[file_schema.FileCreateOut]:
    path = app_settings.DEFAULT_FILES_PATH
    # meta_fields = (
    #     file_schema.FileUploadDataIn(**json.loads(payload)) if payload else None
    # )
    result = await file_controller.upload_file(
        file=file,
        path=path,
        current_user=current_user,
        # meta_fields=meta_fields,
        background_tasks=background_tasks,
    )
    return Response[file_schema.FileCreateOut](data=result)
