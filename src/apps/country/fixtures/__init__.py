from persiantools.characters import ar_to_fa

from src.apps.country.models import (
    State,
    City,
)
from .iran_fixtures import iran


async def default_iran():
    if await State.count() == 0 and await City.count() == 0:
        for state in iran:
            db_state = await State(
                name=ar_to_fa(state.get("name")),
                is_enabled=True,
                is_deleted=False,
            ).insert()
            for city in state.get("cities"):
                await City(
                    name=ar_to_fa(city.get("name")),
                    state_id=db_state.id,
                    is_enabled=True,
                    is_deleted=False,
                ).create()


async def run_fixtures():
    await default_iran()
