import json
import re
from datetime import datetime
from typing import List, TypeVar, Any

import phonenumbers
from fastapi import BackgroundTasks
from pydantic import validate_email

from src.apps.report.crud import report_crud
from src.apps.category.models import Attributes as CategoryAttributes
from src.apps.log_app.constants import LogActionEnum
from src.apps.log_app.controller import log_controller
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse, BaseSchema
from src.core.common.exceptions import InvalidQueryParams
from src.core.common.exceptions.common import CustomHTTPException
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.main.config import collections_names
from . import schema as report_schemas
from .models import Report

from ..category.crud import categories_crud
from ..common.constants import AttributeTypeEnum
from ..user.models import User
from ...core.utils import phone_to_e164_format

SCHEMA = TypeVar("SCHEMA", bound=BaseSchema)


class ReportController(BaseController):
    pass


report_controller = ReportController(
    crud=report_crud,
)
