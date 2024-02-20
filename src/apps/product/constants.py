from enum import Enum
from typing import List


class PeriodTypeEnum(str, Enum):
    DAILY = "روزانه"
    MONTHLY = "ماهانه"
    YEARLY = "سالانه"


class ProductStateEnum(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"


class ProductNotFoundErrorMessageEnum(str, Enum):
    not_found: str = "Product not found"
    invalid_quantity: str = "Invalid quantity"


class ProductNotFoundErrorDetailEnum(List[str], Enum):
    not_found: List[str] = ["Product not found"]
    invalid_quantity: List[str] = ["Invalid quantity"]
