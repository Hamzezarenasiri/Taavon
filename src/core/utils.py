import asyncio
import json
import logging
import re
from datetime import date, datetime, time
from decimal import Decimal
from functools import wraps
from random import choice
from string import ascii_letters, digits
from time import time as time_time
from typing import List, Type, TypeVar

import phonenumbers
import unicodedata
from bson import Decimal128
from fastapi import HTTPException
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError

from src.core.common import exceptions
from src.core.common.exceptions import CustomHTTPException
from src.fastapi_babel import _

default_region_settings = "IR"


def phone_to_e164_format(mobile_number: str, region=default_region_settings):
    return (
        phonenumbers.format_number(
            phonenumbers.parse(mobile_number, region=region),
            phonenumbers.PhoneNumberFormat.E164,
        )
        if mobile_number
        else mobile_number
    )


def get_random_string(
    length=8,
    allowed_chars=digits + ascii_letters,
):
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return "".join(choice(allowed_chars) for _ in range(length))


def make_random_password(
    length=10,
    allowed_chars=digits + ascii_letters,
):
    """
    Generate a random password with the given length and given
    allowed_chars. The default value of allowed_chars does not have "I" or
    "O" or letters and digits that look similar -- just to avoid confusion.
    """
    return get_random_string(length, allowed_chars)


def return_on_failure(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise

        except DuplicateKeyError as e:
            key = list(e.details["keyValue"].keys())[0]
            raise CustomHTTPException(
                # message=f"{key} value ({e.details['keyValue'][key]}) is duplicate and can not be inserted",
                message=f"مقدار {key} ({e.details['keyValue'][key]}) تکراری است و نمی توان آن را درج کرد",
                detail={
                    "loc": ["body", key],
                    # "msg": _("field %(key)s duplicated") % key,
                    "msg": f"فیلد {key} از قبل وجود دارد و تکراری است ، لطفا مقدار دیگری دارد کنید ",
                    # "msg": "field duplicated",
                    "type": "value_error.duplicate",
                },
                status_code=409,
            ) from e
        except Exception as error:
            logging.exception("Traceback:")
            raise exceptions.InternalServerError(detail=str(error)) from error

    return wrapper


class CustomDict(dict):
    def __init__(self, *args, **kwargs):
        super(CustomDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


ModelType = TypeVar("ModelType", bound=BaseModel)


async def get_fields_by_type(model: Type[ModelType], field_type) -> List[str]:
    return [
        field.name
        for field in model.__fields__.values()
        if field.outer_type_ == field_type
    ]


async def get_required_fields(model: Type[ModelType]) -> List[str]:
    return [field.name for field in model.__fields__.values() if field.required]


def slugify(value, allow_unicode=False) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        elif isinstance(o, Decimal128):
            return float(o.to_decimal())
        elif isinstance(o, datetime):
            return o.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        elif isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, time):
            return o.strftime("%H:%M:%S.%fZ")
        super(DecimalEncoder, self).default(o)


def timeit(func):
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            print(f"{func.__name__} function is a coroutine")
            return await func(*args, **params)
        else:
            print(f"{func.__name__} is not a coroutine")
            return func(*args, **params)

    async def helper(*args, **params):
        start = time_time()
        result = await process(func, *args, **params)
        print(f"{func.__name__}.time >>>", time_time() - start)
        return result

    return helper
