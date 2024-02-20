from enum import Enum



class AttributeTypeEnum(str, Enum):
    BOOL = "boolean"
    STR = "string"
    INT = "integer"
    DATE = "date"
    DATETIME = "date-time"
    FLOAT = "number"
    EMAIL = "email"
    PRICE = "price"
    CHOICE = "choice"
    NATIONAL_CODE = "national_code"
    PHONE_NUMBER = "phone_number"
    # MULTI_CHOICE = "multi_choice"
    # RANGE = "range"


class FilterTypeEnum(str, Enum):
    BOOL = "boolean"
    STR = "string"
    INT = "integer"
    DATE = "date"
    DATETIME = "date-time"
    FLOAT = "number"
    EMAIL = "email"
    PRICE = "price"
    CHOICE = "choice"
    NATIONAL_CODE = "national_code"
    PHONE_NUMBER = "phone_number"
    # RANGE_DATE = "range_date"
    # MULTI_CHOICE = "multi_choice"
    # RANGE = "range"



class ConfirmStatusEnum(str, Enum):
    Confirm: str = "Confirm"
    Reject: str = "Reject"
