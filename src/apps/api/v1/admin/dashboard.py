from fastapi import APIRouter

from src.main.config import collections_names

dashboard_router = APIRouter()
entity = collections_names.DASHBOARD
