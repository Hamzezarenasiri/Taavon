import abc
from typing import TypeVar, List

from pydantic import EmailStr


class BaseEmail(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def send_email(
        self,
        subject: str,
        email_to_list: List,
        from_email: EmailStr = None,
        email_body_text: str = None,
        email_body_html: str = None,
        email_cc_list: List = None,
        email_bcc_list: List = None,
    ):
        ...

    @abc.abstractmethod
    async def send_email_html_file(
        self,
        subject: str,
        email_to_list: List,
        from_email: EmailStr = None,
        email_body_text: str = None,
        email_html_path: str = None,
        email_cc_list: List = None,
        email_bcc_list: List = None,
        **kwargs,
    ):
        ...


EmailType = TypeVar("EmailType", bound=BaseEmail)
