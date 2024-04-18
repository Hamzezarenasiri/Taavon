from src.core.base.schema import BaseSchema


class SubContCardStatics(BaseSchema):
    title: str
    count: int
    icon: str


class ContCardStatics(BaseSchema):
    result: list[SubContCardStatics]
