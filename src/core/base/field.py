import re
from typing import Dict, Any

import phonenumbers
from bson import ObjectId, Decimal128

from src.core.utils import phone_to_e164_format


class PyDecimal128(Decimal128):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return Decimal128(str(value))

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="number",
            example="11.5",
        )


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):  # type: ignore
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict) -> None:
        field_schema.update(
            examples=["0123456789abcdef01234567", "ffffffffffffffffffffffff"],
            example="0123456789abcdef01234567",
            type="string",
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, (ObjectId, cls)):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise TypeError("invalid ObjectId specified")


class PhoneStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        try:
            if value.startswith("00"):
                value = value.replace("00", "+", 1)
            return phone_to_e164_format(value)
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="+989167076478",
        )


class PasswordField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        # Password must be at least 8 characters long
        if len(value) < 8:
            raise ValueError("Password is too short.")

        # Password must contain at least one uppercase letter
        if not re.search("[A-Z]", value):
            raise ValueError("Password does not contain any uppercase letters.")

        # Password must contain at least one lowercase letter
        if not re.search("[a-z]", value):
            raise ValueError("Password does not contain any lowercase letters.")

        # Password must contain at least one digit
        if not re.search("[0-9]", value):
            raise ValueError("Password does not contain any digits.")

        # Password must contain at least one special character
        if not re.search("[!@#$%^&*()_+-]", value):
            raise ValueError("Password does not contain any special characters.")

        return value

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="hNzrH4'7<-",
        )


class UsernameField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        # Username must be at least 4 characters long
        if len(value) < 4:
            raise ValueError(
                "Username is too short. It must be at least 4 characters long."
            )

        # Username must not contain any spaces
        if re.search(" ", value):
            raise ValueError("Username cannot contain spaces.")

        # Username must not start or end with a special character
        if re.search("[!@#$%^&*()_+-]", value[0]):
            raise ValueError("Username cannot start with a special character.")
        if re.search("[!@#$%^&*()_+-]", value[-1]):
            raise ValueError("Username cannot end with a special character.")

        return value

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="ThisIsMyUsername",
        )


class IranPostalCodeField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        # Postal code must be 10 digits long
        if len(value) != 10:
            return "Postal code must be 10 digits long."

        # Postal code must only contain digits
        if not re.search("[0-9]", value):
            return "Postal code must only contain digits."

        return value

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="1111111111",
        )


class IranNationalCodeStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not re.search(r"^\d{10}$", value):
            raise ValueError("The national code is invalid, it must be ten digits")

        check = int(value[9])
        s = sum([int(value[x]) * (10 - x) for x in range(9)]) % 11
        if (2 > s == check) or (s >= 2 and (check + s) == 11):
            return value
        else:
            raise ValueError(
                "The national code is invalid, There is no such national code"
            )

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="1111111111",
        )
