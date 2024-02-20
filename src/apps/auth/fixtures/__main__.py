#!/usr/bin/env python3
import os
import sys

SCRIPT_DIR = os.getcwd()
sys.path[0] = SCRIPT_DIR

import asyncio  # noqa
from src import services  # noqa
from src.services import events
from src.apps.auth.crud import entities_crud, roles_crud  # noqa
from src.apps.auth.fixtures.roles_fixture import all_roles  # noqa
from src.apps.auth.models import Entity, Role  # noqa
from src.apps.auth.fixtures import entities_fixture  # noqa


async def default_entities():
    services.global_services.DB = await events.initialize_db()
    for entity in entities_fixture.all_entities:
        await entities_crud.create(Entity(**entity))


async def default_roles():
    services.global_services.DB = await events.initialize_db()
    for name, permissions in all_roles.items():
        await roles_crud.create(Role(name=name, permissions=list(permissions)))


if __name__ == "__main__":
    print("SCRIPT_DIR", sys.path)

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(default_entities()),
        loop.create_task(default_roles()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
