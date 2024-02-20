from typing import Any, Dict, Optional

from fastapi import HTTPException


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail=None,
        success: bool = False,
        message: str = None,
        data: dict = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if detail is None:
            detail = []
        super().__init__(status_code=status_code, detail=detail)
        self.success = success
        self.message = message
        self.data = data
        self.headers = headers

    def __call__(
        self,
        status_code: int = None,
        detail=None,
        success: bool = None,
        message: str = None,
        data: dict = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        if detail is None:
            detail = []
        if status_code:
            self.status_code = status_code
        if detail:
            self.detail = detail
        if success:
            self.success = success
        if message:
            self.message = message
        if data:
            self.data = data
        if headers:
            self.headers = headers
        return self

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}(status_code={self.status_code!r},"
            f" detail={self.detail!r}),"
            f" success={self.success!r}),"
            f" message={self.message!r}),"
            f" data={self.data!r})"
        )
