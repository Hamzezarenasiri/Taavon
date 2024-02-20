import re
from typing import List

from fastapi import (
    APIRouter,
    Security,
    Query,
)
from persiantools.characters import ar_to_fa
from starlette.responses import FileResponse

from src.apps.auth.deps import get_current_user
from src.apps.report import schema as report_schemas
from src.apps.report.controller import report_controller
from src.apps.user.models import User
from src.core.base.schema import Response
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names, app_settings

report_router = APIRouter()
entity = collections_names.REPORT


@report_router.get(
    "/get_reports_filters",
    responses={**common_responses},
    response_model=Response[List[report_schemas.ReportListSchema]],
    description="by `hamzezn`",
)
@return_on_failure
async def get_reports_filters(
        _: User = Security(get_current_user, scopes=[entity, "list"]),
        search: str = Query(None),
):
    criteria = {"is_enabled": True}
    if search:
        search = ar_to_fa(search)
        criteria["title"] = re.compile(search, re.IGNORECASE)
    reports = await report_controller.get_list_objs_without_pagination(
        criteria=criteria,
    )
    return Response[List[report_schemas.ReportListSchema]](data=reports)


#
# @report_router.get(
#     "/generate_report_file",
#     responses={
#         **common_responses,
#         **response_404,
#     },
#     response_class=FileResponse,
#     description="by `hamzezn`",
# )
# @return_on_failure
# async def generate_report_file(
#     filters: dict = Depends(report_filters),
#     _: User = Security(get_current_user, scopes=[entity, "read"]),
# ):
#     criteria = filters
#     entities, fieldnames = await product_crud.export_dict_and_keys_join_aggregate(
#         criteria=criteria
#     )
#     if not entities:
#         raise EntitiesNotFound
#     path = f"{app_settings.DEFAULT_FILES_PATH}/export_{entity}_{User.id}.csv"
#     write_csv_file(path, entities, fieldnames)
#     return path


@report_router.post(
    "/generate_report_file",
    responses={
        **common_responses,
        **response_404,
    },
    response_class=FileResponse,
    description="by `hamzezn`",
)
@return_on_failure
async def generate_report_file(
        payload: report_schemas.GenerateReportFileIn,
        current_user: User = Security(get_current_user, scopes=[entity, "read"]),
):
    report = await report_controller.get_single_obj(_id=payload.report_filter_id)
    criteria = {"organization_ids": current_user.organization_id}
    # if payload.filters:
    #     if payload.filters.get("organization_name"):
    #         search = ar_to_fa(payload.filters.get("organization_name"))
    #         search_criteria = {"name": re.compile(search, re.IGNORECASE)}
    #         organization_ids = await organization_crud.get_ids(search_criteria)
    #         if organization_ids:
    #             criteria["organization_id"] = {"$in": organization_ids}
    #     if payload.filters.get("title"):
    #         search = ar_to_fa(payload.filters.get("title"))
    #         criteria["title"] = re.compile(search, re.IGNORECASE)
    # else:
    #     criteria["category_id"] = report.category_id
    #     entities, fieldnames = await product_crud.export_dict_and_keys_join_aggregate(
    #         criteria=criteria
    #     )
    #     if not entities:
    #         raise EntitiesNotFound
    #     category: Category = await categories_crud.get_object(
    #         {"_id": entities[0].get("category_id")}
    #     )
    #     attr_dict = {attr.field_name: attr.title for attr in category.attributes}
    #     res_entities = []
    #     for enti in entities:
    #         res_enti = {
    #             "عنوان": enti["title"],
    #             "نام سازمان": enti.get("organization_name", ""),
    #         }
    #         for ent_attr_key, ent_attr_value in enti.get("attributes", {}).items():
    #             res_enti[attr_dict.get(ent_attr_key)] = ent_attr_value
    #         res_entities.append(res_enti)
    # if not res_entities:
    #     raise EntitiesNotFound
    path = f"{app_settings.DEFAULT_FILES_PATH}/export_{entity}_{current_user.username}_{current_user.id}.csv"
    # write_csv_file(path, res_entities, fieldnames)
    return path


@report_router.post(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[report_schemas.ReportDetailSchema],
    description="by `hamzezn`",
)
@return_on_failure
async def create_report_filter(
        payload: report_schemas.CreateReportIn,
        _: User = Security(get_current_user, scopes=[entity, "create"]),
):
    report = await report_controller.create_new_obj(new_data=payload)

    return Response[report_schemas.ReportDetailSchema](data=report)
