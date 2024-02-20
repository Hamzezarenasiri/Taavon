from . import user_fixture
from ..models import User


async def default_users():
    if await User.count() == 0:
        for entity in user_fixture.all_users:
            await User(**entity).insert()


async def run_fixtures():
    await default_users()
