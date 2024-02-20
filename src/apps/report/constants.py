from typing import List
from enum import Enum


class ReportNotFoundErrorMessageEnum(str, Enum):
    not_found: str = "Report not found"
    invalid_quantity: str = "Invalid quantity"


class ReportNotFoundErrorDetailEnum(List[str], Enum):
    not_found: List[str] = ["Report not found"]
    invalid_quantity: List[str] = ["Invalid quantity"]


class FilterBoxType(str, Enum):
    text_box: str = "text_box"
    large_text_box: str = "large_text_box"
    drop_down: str = "drop_down"
    text: str = "text"
    range: str = "range"
    radio: str = "radio"
    toggle: str = "toggle"
    multi_checkbox: str = "multi_checkbox"
    # range_calendar: str = "range_calendar"
    calendar: str = "calendar"


ALL_SEARCH_ATTRIBUTE_TYPES = [i.value for i in FilterBoxType.__members__.values()]
