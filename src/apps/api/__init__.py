from fastapi import APIRouter

from src.fastapi_babel import _

home_router = APIRouter()


@home_router.get("/")
async def home():
    fa_text = _("Hello World")
    return {"key": fa_text}
