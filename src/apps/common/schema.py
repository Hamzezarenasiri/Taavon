from src.apps.common.constants import ConfirmStatusEnum
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID


class BulkConfirmIn(BaseSchema):
    ids: list[SchemaID]
    status: ConfirmStatusEnum


class ConfirmIn(BaseSchema):
    status: ConfirmStatusEnum
