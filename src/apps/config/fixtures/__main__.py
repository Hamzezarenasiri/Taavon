#!/usr/bin/env python3
import os
import sys

SCRIPT_DIR = os.getcwd()
sys.path[0] = SCRIPT_DIR

import asyncio  # noqa
from src import services  # noqa
from src.services import events
from src.apps.config.models import Config  # noqa
from src.apps.config.fixtures import configs_fixture  # noqa
from src.apps.config.crud import configs_crud  # noqa


async def default_configs():
    services.global_services.DB = await events.initialize_db()
    await configs_crud.create(Config(**configs_fixture.configs))


if __name__ == "__main__":
    print("SCRIPT_DIR", sys.path)

    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(default_configs()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
