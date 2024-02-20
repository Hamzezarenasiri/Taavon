from src.apps.category.models import Category
from .category_fixtures import all_categories


async def default_categories():
    if await Category.count() == 0:
        for category in all_categories:
            await Category(**category).insert()


async def run_fixtures():
    await default_categories()
