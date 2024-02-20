from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID


class SubMonthlyStatics(BaseSchema):
    name: str
    number: int


class MonthlyStatics(BaseSchema):
    result: list[SubMonthlyStatics]


class SubContCardStatics(BaseSchema):
    category_id: SchemaID
    category_title: str
    count: int
    percentage_change: float


class ContCardStatics(BaseSchema):
    result: list[SubContCardStatics]


class SubPieChartStatics(BaseSchema):
    category_id: SchemaID
    category_title: str
    count: int
    percentage: float


class PieChartStatics(BaseSchema):
    result: list[SubPieChartStatics]
