from enum import Enum


class LogActionEnum(str, Enum):
    confirm: str = "confirm"
    insert: str = "insert"
    update: str = "update"
    update_status: str = "update_status"
    delete: str = "delete"
    single_read: str = "single_read"
    list_read: str = "list_read"
    wallet_inc: str = "wallet_inc"
    wallet_dec: str = "wallet_dec"


ALL_LOG_ACTIONS = [i.value for i in LogActionEnum.__members__.values()]
