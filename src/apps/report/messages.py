from enum import Enum


class ReportMessageEnum(str, Enum):
    create_new_report: str = "create_new_report"
    get_reports: str = "get_reports"
    get_single_report: str = "get_single_report:"
    update_single_report: str = "update_single_report"
    bulk_update_reports: str = "bulk_update_reports"
    change_reports_status: str = "change_reports_status"
    get_report_rates: str = "get_report_rates"
    get_report_reviews: str = "get_report_reviews"
    change_reviews_status: str = "change_reviews_status"
    create_new_review: str = "create_new_review"
    get_reports_statistics: str = "get_reports_statistics"
    get_CSV_import_history: str = "get_CSV_import_history"
    get_single_CSV_import: str = "get_single_CSV_import"
    export_report_CSV: str = "export_report_CSV"
    reports_upload_CSV: str = "reports_upload_CSV"
    add_report_to_favourites: str = "add_report_to_favourites"
    add_report_rate: str = "add_report_rate"
    get_report_rates_average: str = "get_report_rates_average"


class ReportErrorMessageEnum(str, Enum):
    not_found: str = "report_not_found"
    # not_found_or_disabled: str = "report_not_found_or_disabled"
    invalid_quantity: str = "invalid_quantity"
