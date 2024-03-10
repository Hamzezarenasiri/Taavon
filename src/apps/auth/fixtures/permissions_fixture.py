from src.apps.auth.fixtures.entities_fixture import all_entities
from src.main.config import collections_names

all_permissions_default = [
    {"entity": entity["code_name"], "rules": entity["rules"]} for entity in all_entities
]

admin_permissions = [
    {
        "entity": collections_names.ENTITY,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.CONFIG,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.FILE,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.ROLE,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.LOG,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {"entity": collections_names.RULE, "rules": ["list", "read", "menu"]},
    {
        "entity": collections_names.USER,
        "rules": [
            "list",
            "create",
            "read",
            "update",
            "confirm",
            "delete",
            "export-csv",
            "menu",
            "activation",
            "blocking",
            "change_password",
        ],
    },
    {
        "entity": collections_names.DASHBOARD,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    # {
    #     "entity": collections_names.NOTIFICATIONS,
    #     "rules": ["list", "create", "read", "update", "delete", "menu"],
    # },
    {
        "entity": collections_names.CITY,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.STATE,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.ORGANIZATION,
        "rules": ["list", "create", "read", "update", "confirm", "delete", "menu"],
    },
    {
        "entity": collections_names.PROFILE,
        "rules": ["update"],
    },
    {
        "entity": collections_names.PRODUCT,
        "rules": ["list", "create", "read", "update", "confirm", "delete", "menu"],
    },
    {
        "entity": collections_names.CATEGORY,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.REPORT,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.STORE,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": collections_names.INVOICE,
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
]
super_admin_permissions = admin_permissions + []
