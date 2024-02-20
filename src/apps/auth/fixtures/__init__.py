from . import entities_fixture, roles_fixture
from ..models import (
    Role,
    Entity,
)


async def default_entities():
    if await Entity.count() == 0:
        for entity in entities_fixture.all_entities_default:
            await Entity(**entity).insert()


async def default_roles():
    if await Role.count() == 0:
        for name, permissions in roles_fixture.all_roles.items():
            await Role(name=name, permissions=list(permissions)).insert()


async def run_fixtures():
    await default_entities()
    await default_roles()
