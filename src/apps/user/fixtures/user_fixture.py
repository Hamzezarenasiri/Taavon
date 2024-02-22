from bson import ObjectId

from src.core.security import user_password
from src.main.config import app_settings

all_users = [
    {
        "_id": ObjectId("0123456789abcdef01234567"),
        "is_blocked": False,
        "is_deleted": {"$ne": True},
        "is_enabled": True,
        "is_force_change_password": False,
        "is_force_login": False,
        "mobile_number": "+989123456789",
        "email": "admin@email.com",
        "hashed_password": str(
            user_password.get_password_hash(app_settings.DEFAULT_PASSWORD)
        ),
        "roles": ["super_admin"],
        "phone_verified": True,
        "email_verified": True,
        "national_code": "1111111111",
        "user_status": "confirmed",
        "address": {
            "location": {
                "coordinates": [25.11812, 55.20058],
                "type": "Point",
            },
            "first_name": "The Vira TAAVON",
            "last_name": "Manager Name",
            "country_code": "IR",
            "phone_number": "+97144570397",
            "alternate_phone_number": "+97144570397",
            "street": "-------",
            "address_line_1": "---",
            "address_line_2": "---",
            # "state": "-",
            # "city": "-",
            "postal_code": None,
            "type": None,
            "landmark": None,
            "address_name": "----",
            "building_name": "-----",
            "area": "---",
        },
        "gender": "male",
        "first_name": "Genesis",
        "last_name": "Admin",
        "username": "ThisIsMyUsername",
        "permissions": [],
        "settings": {
            "language": "EN",
            "country_code": "IR",
        },
    },
]
