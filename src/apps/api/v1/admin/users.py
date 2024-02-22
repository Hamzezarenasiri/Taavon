import re
import shutil
from typing import List, Optional

from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Security,
    BackgroundTasks,
    status,
    UploadFile,
    File,
)
from fastapi.responses import Response as StarletteResponse
from persiantools.characters import ar_to_fa
from starlette.responses import FileResponse, JSONResponse

from src.apps.auth.deps import get_current_user
from src.apps.country.crud import state_crud, city_crud
from src.apps.country.models import State, City
from src.apps.language.constants import LanguageEnum
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.apps.organization.crud import organization_crud
from src.apps.organization.models import Organization
from src.apps.user import schema as user_schema
from src.apps.user.constants import ALL_USER_STATUSES, UserMessageEnum, UserStatus
from src.apps.user.controller import user_controller
from src.apps.user.models import User
from src.apps.user.schema import AddressSchemaIn
from src.core.base.schema import (
    BulkDeleteIn,
    PaginatedResponse,
    Response,
    CitySchemaIn,
    StateSchemaIn,
)
from src.core.csv_utils import csv_to_list_dict
from src.core.mixins import SchemaID, ErrorMessage
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import (
    common_responses,
    response_404,
    response_403,
)
from src.core.security import user_password
from src.core.utils import return_on_failure
from src.main.config import app_settings, collections_names

user_router = APIRouter()
entity = collections_names.USER


@user_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]
    ],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_users(
    _: User = Security(get_current_user, scopes=[entity, "list"]),
    search: Optional[str] = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
) -> Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]]:
    criteria = {"is_deleted": {"$ne": True}}
    if search:
        search = ar_to_fa(search)
        if search := re.sub(r"[()\[\]'*+?\\]", "", search):
            spl = search.split(" ", 1)
            if len(spl) > 1:
                criteria["first_name"] = re.compile(spl[0], re.IGNORECASE)
                criteria["last_name"] = re.compile(spl[1], re.IGNORECASE)
            else:
                criteria["$or"] = [
                    {"first_name": re.compile(search, re.IGNORECASE)},
                    {"last_name": re.compile(search, re.IGNORECASE)},
                    {"email": re.compile(search, re.IGNORECASE)},
                    {"mobile_number": re.compile(search, re.IGNORECASE)},
                    {"username": re.compile(search, re.IGNORECASE)},
                ]

    result_data = await user_controller.get_all_users(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]](
        data=result_data.dict()
    )


@user_router.get(
    "/export-csv",
    responses={
        **common_responses,
    },
    response_class=FileResponse,
    description="export CSV",
)
@return_on_failure
async def export_users_csv(
    _: User = Security(get_current_user, scopes=[entity, "export-csv"]),
    search: Optional[str] = Query(None),
    user_status: Optional[List[UserStatus]] = Query(None, enum=ALL_USER_STATUSES),
    roles: Optional[List[str]] = Query(None),
):
    criteria = {"is_deleted": {"$ne": True}}
    if search:
        search = ar_to_fa(search)
        if search := re.sub(r"[()\[\]'*+?\\]", "", search):
            spl = search.split(" ", 1)
            if len(spl) > 1:
                criteria["first_name"] = re.compile(spl[0], re.IGNORECASE)
                criteria["last_name"] = re.compile(spl[1], re.IGNORECASE)
            else:
                criteria["$or"] = [
                    {"first_name": re.compile(search, re.IGNORECASE)},
                    {"last_name": re.compile(search, re.IGNORECASE)},
                    {"email": re.compile(search, re.IGNORECASE)},
                    {"mobile_number": re.compile(search, re.IGNORECASE)},
                    {"username": re.compile(search, re.IGNORECASE)},
                ]
    if user_status:
        criteria["user_status"] = {"$in": user_status}
    if roles:
        criteria["roles"] = {"$in": roles}
    result_data = await user_controller.export_csv(
        files_path=app_settings.DEFAULT_FILES_PATH,
        entity_name=entity,
        criteria=criteria,
    )
    return result_data.url


@user_router.post(
    "",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_user(
    background_tasks: BackgroundTasks,
    payload: user_schema.UsersCreateIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "create"],
    ),
) -> Response[user_schema.UsersCreateOut]:
    result_data = await user_controller.create_new_user(new_user_data=payload)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_id=result_data.id,
    )
    return Response[user_schema.UsersCreateOut](data=result_data)


@user_router.get(
    "/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_user(
    user_id: SchemaID = Path(...),
    _: User = Security(get_current_user, scopes=[entity, "read"]),
) -> Response[user_schema.UsersGetUserOut]:
    result_data = await user_controller.get_single_user(target_user_id=user_id)
    return Response[user_schema.UsersGetUserOut](data=result_data)


@user_router.patch(
    "/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_user(
    background_tasks: BackgroundTasks,
    payload: user_schema.UsersUpdateIn,
    user_id: SchemaID = Path(...),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
) -> Response[user_schema.UsersGetUserOut]:
    result_data = await user_controller.update_single_user(
        target_id=ObjectId(user_id),
        new_data=payload,
    )

    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=ObjectId(user_id),
    )
    return Response[user_schema.UsersGetUserOut](data=result_data)


async def users_bulk_update_method(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserBulkUpdateIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    result_data = await user_controller.bulk_update_obj(
        obj_ids=payload.ids, new_obj_data=payload
    )
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return Response[List[user_schema.UsersGetUserOut]](data=result_data)


@user_router.patch(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[List[user_schema.UsersGetUserOut]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_update_users(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserBulkUpdateIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "update"],
    ),
):
    return await users_bulk_update_method(background_tasks, payload, current_user)


@user_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_users(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    await user_controller.bulk_delete_users(obj_ids=payload.ids)
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return StarletteResponse(status_code=204)


@user_router.post(
    "/{user_id}/password/reset",
    description="Set new password for given user_id by admin \n\nBy `Hamze.zn`",
    responses={**common_responses},
    # response_model=Response,
)
@return_on_failure
async def set_new_password(
    background_tasks: BackgroundTasks,
    user_id: SchemaID,
    payload: user_schema.UsersChangePasswordByAdminIn,
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "change_password"],
    ),
):
    result_data = await user_controller.set_password(
        new_password=payload.new_password,
        user_id=ObjectId(user_id),
        force_change_password=True,
        force_login=True,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=ObjectId(user_id),
        description={LanguageEnum.english: "set password"},
    )
    return Response(detail=result_data, message=UserMessageEnum.changed_password)


@user_router.delete(
    "/{user_id}/",
    status_code=204,
    responses={
        **common_responses,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_user(
    background_tasks: BackgroundTasks,
    user_id: SchemaID = Path(...),
    current_user: User = Security(
        get_current_user,
        scopes=[entity, "delete"],
    ),
):
    if await user_controller.soft_delete_single_user(
        target_user_id=ObjectId(user_id),
    ):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=ObjectId(user_id),
        )
        return StarletteResponse(status_code=204)


#
# @user_router.patch(
#     "/avatar/{user_id}/",
#     description="Upload avatar for an existing user",
#     status_code=status.HTTP_200_OK,
#     responses={**common_responses, **response_413},
#     response_model=Response[FileOut],
# )
# @return_on_failure
# async def upload_avatar(
#     user_id: SchemaID = Path(...),
#     avatar=Depends(avatar_validation),
#     _: User = Security(get_current_user, scopes=[entity, "update"]),
# ):
#     path = app_settings.DEFAULT_AVATARS_PATH
#     result = await profile_controller.upload_avatar(
#         avatar=avatar, user_id=ObjectId(user_id), path=path
#     )
#     return Response[FileOut](data=result)


@user_router.post(
    "/import-csv",
    # response_model=Response[user_schema.UsersImportOut],
    response_model=user_schema.UsersImportOut,
    responses={
        **response_403,
        406: {"model": ErrorMessage, "description": "File type must be csv"},
    },
)
@return_on_failure
async def import_csv(
    background_tasks: BackgroundTasks,
    _: User = Depends(get_current_user),
    file: UploadFile = File(...),
):
    if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=ErrorMessage(detail="File type must be csv").dict(),
        )

    csv_path = "user_import.csv"
    with open(csv_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    data = csv_to_list_dict(csv_path)
    dict_item: dict
    for dict_item in data:
        if dict_item.get("state"):
            state: State = await state_crud.get_an_object(
                criteria={"name": ar_to_fa(dict_item.get("state"))}
            )
            if dict_item.get("city"):
                city: City = await city_crud.get_an_object(
                    criteria={
                        "name": ar_to_fa(dict_item.get("city")),
                        "state_id": state.id,
                    }
                )
        if dict_item.get("organization_name"):
            organization: Organization = await organization_crud.get_an_object(
                criteria={"name": ar_to_fa(dict_item.get("organization_name"))}
            )
        background_tasks.add_task(
            func=user_controller.update_create_single_obj,
            criteria={"username": dict_item.get("username")},
            new_data=user_schema.UserImportCsvSchema(
                **dict_item,
                organization_id=organization.id,
                hashed_password=user_password.get_password_hash(
                    dict_item.get("password")
                ),
                roles=[dict_item.get("role")],
                address=AddressSchemaIn(
                    address_line_1=dict_item.get("address_line_1"),
                    state=StateSchemaIn(name=state.name, state_id=state.id),
                    city=CitySchemaIn(name=city.name, city_id=city.id),
                ),
            ),
        )
    return user_schema.UsersImportOut()
