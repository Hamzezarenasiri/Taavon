from enum import Enum
from typing import List
from src.fastapi_babel import _


class SearchAttributeType(str, Enum):
    range: str = "range"
    radio: str = "radio"
    toggle: str = "toggle"
    multi_checkbox: str = "multi_checkbox"


ALL_SEARCH_ATTRIBUTE_TYPES = [i.value for i in SearchAttributeType.__members__.values()]


class CategoryNotFoundErrorDetailEnum(list, Enum):
    not_found: List[str] = ["Category not found"]


class Category422DetailEnum(list, Enum):
    recursive: List[str] = ["Can't be recursive (parent)"]
    has_child: List[str] = ["Category has child"]
    has_product: List[str] = ["Category has product"]


class CategoryErrorDetailEnum(list, Enum):
    have_child: List[str] = ["Categories have child"]
    have_product: List[str] = ["Categories have product"]


class CategoryMessageEnum(str, Enum):
    create_new_category: str = "create_new_category"
    get_categories: str = "get_categories"
    get_single_category: str = "get_single_category"
    update_category: str = "update_category"
    bulk_update_categories: str = "bulk_update_categories"
    get_category_attributes: str = "get_category_attributes"


class CategoryNotFoundErrorMessageEnum(str, Enum):
    not_found: str = "category_not_found"


class Category422MessageEnum(str, Enum):
    recursive: str = "can_t_be_recursive"
    has_child: str = "category_has_child"
    has_product: str = "category_has_product"
    Invalid_parent__category_not_found: str = _("Invalid parent. Category not found")
    Invalid_category_id__category_not_found: str = _(
        "Invalid category_id. Category not found"
    )


class CategoryErrorMessageEnum(str, Enum):
    have_child: str = "categories_have_child"
    have_product: str = "categories_have_product"
