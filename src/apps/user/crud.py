from typing import Optional, Tuple

from src.apps.user.exceptions import UserNotFound
from src.apps.user.models import (
    User,
)
from src.apps.user.schema import UsersUpdateIn
from src.core.base.crud import BaseCRUD
from src.core.base.models import AddressModel
from src.core.mixins.fields import DB_ID, SchemaID
from src.core.security import user_password


class UserCRUD(BaseCRUD):
    async def update_user(
        self,
        new_data: UsersUpdateIn,
        target_id: SchemaID,
    ) -> Tuple[bool, User]:
        stored_item_model: User = await self.get_by_id(target_id)
        data_dict = new_data.dict(exclude_unset=True)
        updated_item = stored_item_model.copy(update=data_dict).dict()
        if updated_item.get("password"):
            updated_item["hashed_password"] = user_password.get_password_hash(
                new_data.password
            )
        updated_user, is_updated = await self.update_and_get(
            criteria={"_id": target_id},
            new_doc=self.update_db_model(**updated_item).dict(),
        )

        return is_updated, updated_user

    async def get_joined_user(
        self,
        target_id: DB_ID,
        criteria: Optional[dict] = None,
    ) -> dict:
        if criteria is None:
            criteria = {}
        criteria.update({"_id": target_id})
        pipeline = [
            {"$match": criteria},
        ]
        result = await self.aggregate(pipeline=pipeline)
        if not result:
            raise UserNotFound
        return result[0]

    async def get_address_by_address_id(
        self, address_id: SchemaID
    ) -> Optional[AddressModel]:
        pipeline = [
            {
                "$project": {
                    "details": {
                        "$filter": {
                            "input": "$addresses",
                            "as": "addresses",
                            "cond": {
                                "$eq": [
                                    "$$addresses.address_id",
                                    address_id,
                                ]
                            },
                        }
                    }
                }
            },
            {"$unwind": "$details"},
        ]
        address = await self.aggregate(pipeline=pipeline)
        return AddressModel(**address[0]["details"]) if address else None

    async def export_dict_and_keys_join_aggregate(self, criteria):
        project = {
            "first_name": 1,
            "last_name": 1,
            "email": 1,
            "mobile_number": {"$ifNull": ["$mobile_number", "Unspecified"]},
            "gender": 1,
            "is_enabled": 1,
            "date_of_birth": 1,
            "login_type": 1,
            "user_status": 1,
            "user_type": 1,
            "is_blocked": 1,
            "email_verified": 1,
            "phone_verified": 1,
            "login_datetime": 1,
            "create_datetime": 1,
        }
        entities = await self.aggregate(
            pipeline=[
                {"$match": criteria},
                {"$project": {"_id": 0, **project}},
            ]
        )
        return entities, project.keys()


users_crud = UserCRUD(
    read_db_model=User,
    create_db_model=User,
    update_db_model=User,
)
