import abc
from datetime import datetime, time
from typing import Any, Dict, Optional, Union

import phonenumbers
from pydantic import BaseModel, EmailError, EmailStr, Field, root_validator, validator
from pydantic.fields import ModelField

from src.core.base.field import PhoneStr
from src.core.utils import CustomDict, phone_to_e164_format

USERNAME_IS_PHONE: str = "mobile_number"
USERNAME_IS_EMAIL: str = "email"


class UsernameSchema(BaseModel):
    username: str = Field(example="+989167076478")

    # pylint: disable=no-self-argument,no-self-use
    @validator("username")
    def phone_email_validate(cls, value) -> Optional[dict]:
        if not value:
            return value
        try:
            if not EmailStr.validate(value):
                raise EmailError
            valid_value = str(value)
            value_type = USERNAME_IS_EMAIL
        except EmailError:
            try:
                if value.startswith("00"):
                    value = value.replace("00", "+", 1)
                valid_value = phone_to_e164_format(value)
                value_type = USERNAME_IS_PHONE
            except phonenumbers.NumberParseException as e:
                raise ValueError("InValid PhoneNumber or Email") from e
        return CustomDict({"value": valid_value, "value_type": value_type})

    def dict(self, *args, **kwargs):
        _dict = super().dict(*args, **kwargs)
        _dict[f'{_dict["username"]["value_type"]}'] = _dict["username"]["value"]
        _dict.pop("username")
        return _dict


class UsernameModel(BaseModel):
    username: Union[dict, str]

    # pylint: disable=no-self-argument,no-self-use
    @validator("username")
    def phone_email_validate(cls, value) -> Optional[dict]:
        if not value:
            return value
        if isinstance(value, dict):
            return value
        try:
            if not EmailStr.validate(value):
                raise EmailError
            valid_value = str(value)
            value_type = USERNAME_IS_EMAIL
        except EmailError:
            try:
                if value.startswith("00"):
                    value = value.replace("00", "+", 1)
                valid_value = phone_to_e164_format(value)
                value_type = USERNAME_IS_PHONE
            except phonenumbers.NumberParseException as e:
                raise ValueError("InValid PhoneNumber or Email") from e
        return CustomDict({"value": valid_value, "value_type": value_type})

    def dict(self, *args, **kwargs):
        _dict = super().dict(*args, **kwargs)
        if _dict.get("username", None):
            _dict[f'{_dict["username"]["value_type"]}'] = _dict["username"]["value"]
            _dict.pop("username")
        return _dict


class CreateDatetimeMixin(BaseModel):
    create_datetime: Optional[datetime] = Field(default_factory=datetime.utcnow)


class UpdateDatetimeMixin(BaseModel):
    update_datetime: Optional[datetime] = Field(default_factory=datetime.utcnow)


class IsEnableMixin(BaseModel):
    is_enabled: Optional[bool] = True


class SoftDeleteMixin(BaseModel):
    is_deleted: Optional[bool] = False


class MobileNumberModelMixin(BaseModel):
    mobile_number: Optional[PhoneStr] = Field(example="+982112345678")

    @validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str):
        if not value:
            return value
        try:
            if value.startswith("00"):
                value = value.replace("00", "+", 1)
            return phone_to_e164_format(value)
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e


class PhoneNumberModelMixin(BaseModel):
    mobile_number: Optional[PhoneStr] = Field(example="+982112345678")

    @validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str):
        if not value:
            return value
        try:
            if value.startswith("00"):
                value = value.replace("00", "+", 1)
            return phone_to_e164_format(value)
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e


class EmailModelMixin(BaseModel):
    email: EmailStr = Field(example="user@example.com")

    @validator("email")
    @classmethod
    def validate_email(cls, value) -> str:
        return str(value).lower() if value else None


class FromToDatetimeMixin(BaseModel):
    from_datetime: Optional[datetime]
    to_datetime: Optional[datetime]

    # pylint: disable=no-self-argument,no-self-use
    @root_validator
    def check_datetime_order(cls, values):
        from_datetime, to_datetime = values.get("from_datetime"), values.get(
            "to_datetime"
        )
        if from_datetime and to_datetime and from_datetime > to_datetime:
            raise ValueError("`from_datetime` should not be greater than `to_datetime`")
        return values


class DurationMixin(FromToDatetimeMixin):
    duration: Optional[float]

    # pylint: disable=no-self-argument,no-self-use
    @validator("duration", always=True)
    def calculate_duration(cls, value, values):
        from_datetime: Optional[datetime] = values.get("from_datetime")
        to_datetime: Optional[datetime] = values.get("to_datetime")
        if from_datetime and to_datetime:
            return (to_datetime - from_datetime).total_seconds()
        return value


class IsoFormatStartEndTimeMixin(BaseModel):
    start_time: time
    end_time: time

    # pylint: disable=no-self-argument,no-self-use
    @validator("start_time", "end_time")
    def isoformat_time(cls, value: time) -> str:
        return value.isoformat()


class AddFieldsBaseModel(BaseModel, metaclass=abc.ABCMeta):
    @classmethod
    def add_fields(cls, **field_definitions: Any):
        new_fields: Dict[str, ModelField] = {}
        new_annotations: Dict[str, Optional[type]] = {}

        for f_name, f_def in field_definitions.items():
            if isinstance(f_def, tuple):
                try:
                    f_annotation, f_value = f_def
                except ValueError as e:
                    raise Exception(
                        "field definitions should either be "
                        "a tuple of (<type>, <default>) or just a "
                        "default value, unfortunately this means tuples as "
                        "default values are not allowed"
                    ) from e
            else:
                f_annotation, f_value = None, f_def

            if f_annotation:
                new_annotations[f_name] = f_annotation

            new_fields[f_name] = ModelField.infer(
                name=f_name,
                value=f_value,
                annotation=f_annotation,
                class_validators=None,
                config=cls.__config__,
            )

        cls.__fields__.update(new_fields)
        cls.__annotations__.update(new_annotations)  # pylint: disable=no-member

    def return_select_dict(
        self,
        select_dict,
        include: Optional[set] = None,
        exclude: Optional[set] = None,
    ) -> CustomDict:
        if select_dict not in self.__dict__.keys():
            raise ValueError("select_dict not valid")
        if include:
            return CustomDict(
                {_key: self.__dict__[select_dict][_key] for _key in include}
            )
        if exclude:
            for key in exclude:
                self.__dict__[select_dict].pop(key)
            return CustomDict(self.__dict__[select_dict])
        return CustomDict(self.__dict__[select_dict])
