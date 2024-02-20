from datetime import datetime
from typing import Any, Union

import pymongo
from beanie import Document
from pydantic import BaseModel, Field

from src.apps.product.constants import (
    ProductStateEnum,
    PeriodTypeEnum,
)
from src.apps.common.constants import ConfirmStatusEnum
from src.core import mixins
from src.core.base.field import PyDecimal128
from src.core.mixins import DB_ID
from src.main.config import collections_names


class PriceModel(BaseModel):
    value: PyDecimal128
    is_periodic: None | bool = False
    period_type: None | PeriodTypeEnum

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True


class StatusHistoryModel(BaseModel):
    last_state: ProductStateEnum
    current_state: ProductStateEnum
    description: str | None
    change_date: datetime = Field(default_factory=datetime.utcnow)
    changer_id: DB_ID
    fields: dict | None


class Product(
    Document,
    mixins.IsEnableMixin,
    mixins.SoftDeleteMixin,
    mixins.CreateDatetimeMixin,
):
    title: None | str
    product_state: ProductStateEnum = ProductStateEnum.PENDING.value
    confirm_status: ConfirmStatusEnum | None
    attributes: dict[str, Any]
    category_id: DB_ID
    category_ids: list[DB_ID]
    description: str | None
    organization_id: None | DB_ID
    organization_ids: list[DB_ID] = Field([])
    pictures: list[str] | None
    price: None | PriceModel
    status_history: Union[list[StatusHistoryModel], list] = []

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    class Meta:
        collection_name = collections_names.PRODUCT
        entity_name = "product"
        indexes = [
            pymongo.IndexModel("id", name="id", unique=True),
            pymongo.IndexModel("category_ids", name="category_ids"),
            pymongo.IndexModel("product_state", name="product_state"),
            pymongo.IndexModel([("price.value", pymongo.DESCENDING)], name="price"),
        ]
