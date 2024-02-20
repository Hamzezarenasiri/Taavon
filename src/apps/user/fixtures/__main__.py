#!/usr/bin/env python3
import os
import sys

SCRIPT_DIR = os.getcwd()
sys.path[0] = SCRIPT_DIR
import asyncio  # noqa

from src.apps.user.crud import users_crud  # noqa
from src.apps.user.models import User  # noqa
from src import services  # noqa
from src.services import events
from src.apps.user.fixtures import user_fixture  # noqa


async def default_users():
    services.global_services.DB = await events.initialize_db()
    for entity in user_fixture.all_users:
        await users_crud.create(User(**entity))


if __name__ == "__main__":
    print("SCRIPT_DIR", sys.path)

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(default_users()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
