from enum import Enum


class CommonMessageEnum(str, Enum):
    export_csv: str = "export_csv"
    export_xml: str = "export_xml"
