from typing import TYPE_CHECKING, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import DispatchFunction
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp

if TYPE_CHECKING:
    from .core import Babel


def to_locale(language):
    language, _, country = language.lower().partition("-")
    return language


class InternationalizationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        babel: "Babel",
        dispatch: Optional[DispatchFunction] = None,
    ) -> None:
        super().__init__(app, dispatch)
        self.babel: "Babel" = babel

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """dispatch function

        Args:
            request (Request): ...
            call_next (RequestResponseEndpoint): ...

        Returns:
            Response: ...
        """
        lang_code: Optional[str] = request.headers.get("Accept-Language", None)
        if lang_code:
            self.babel.locale = to_locale(lang_code.split(",")[0])
        response: Response = await call_next(request)
        return response
