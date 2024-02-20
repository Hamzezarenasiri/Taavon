from enum import Enum


class ProductMessageEnum(str, Enum):
    create_new_product: str = "create_new_product"
    get_products: str = "get_products"
    get_single_product: str = "get_single_product:"
    update_single_product: str = "update_single_product"
    bulk_update_products: str = "bulk_update_products"
    change_products_status: str = "change_products_status"
    get_product_rates: str = "get_product_rates"
    get_product_reviews: str = "get_product_reviews"
    change_reviews_status: str = "change_reviews_status"
    create_new_review: str = "create_new_review"
    get_products_statistics: str = "get_products_statistics"
    get_CSV_import_history: str = "get_CSV_import_history"
    get_single_CSV_import: str = "get_single_CSV_import"
    export_product_CSV: str = "export_product_CSV"
    products_upload_CSV: str = "products_upload_CSV"
    add_product_to_favourites: str = "add_product_to_favourites"
    add_product_rate: str = "add_product_rate"
    get_product_rates_average: str = "get_product_rates_average"


class ProductErrorMessageEnum(str, Enum):
    not_found: str = "product_not_found"
    # not_found_or_disabled: str = "product_not_found_or_disabled"
    invalid_quantity: str = "invalid_quantity"
