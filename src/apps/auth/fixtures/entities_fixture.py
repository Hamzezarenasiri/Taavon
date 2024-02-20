from src.main.config import collections_names

colls = list(collections_names.dict().values())
default_rules = ["list", "create", "read", "update", "delete", "menu"]
all_entities_default = [
    {
        "code_name": code_name,
        "description": description,
        "rules": default_rules,
    }
    for code_name, description in zip(colls, colls)
]

all_entities = [
    {
        "code_name": "users",
        "description": "users",
        "rules": [
            "list",
            "create",
            "read",
            "update",
            "delete",
            "menu",
            "activation",
        ],
    }
]
