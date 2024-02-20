import importlib
import inspect
import pkgutil
import pyclbr

import sys
from typing import Sequence, Type, TypeVar

from beanie import Document


DocType = TypeVar("DocType", bound=Document)


def gather_documents() -> Sequence[Type[DocType]]:
    """Returns a list of all MongoDB document models defined in `models` module."""
    from inspect import getmembers, isclass

    return [
        doc
        for _, doc in getmembers(sys.modules[__name__], isclass)
        if issubclass(doc, Document) and doc.__name__ != "Document"
    ]


def get_models(app_settings, logger) -> list:
    """
    Scans `settings.apps_folder_name`.
    Find `models` modules in each of them and get all attributes there.
    :return: list of user-defined models in apps
    """
    from beanie import Document as Model

    apps_folder_name = app_settings.APPS_FOLDER_NAME
    models = []
    for app in app_settings.APPS:
        app_path = f"{apps_folder_name}/{app}"
        modules = [
            f for f in pkgutil.walk_packages(path=[app_path]) if f.name == "models"
        ]
        if not modules:
            continue
        for module in modules:
            path_to_models = f"{apps_folder_name}.{app}.models".replace("/", ".")
            mudule = importlib.import_module(path_to_models)
            if module.ispkg:
                module_models = [
                    x[0] for x in inspect.getmembers(mudule, inspect.isclass)
                ]
            else:
                try:
                    module_models = pyclbr.readmodule(path_to_models).keys()
                except (AttributeError, ImportError):
                    logger.warning(
                        f"Unable to read module attributes in {path_to_models}"
                    )
                    continue
            models.extend([getattr(mudule, model) for model in module_models])
    return list(filter(lambda x: issubclass(x, Model), models))


async def create_indexes(db_engine, app_settings, logger) -> None:
    """
    Gets all models in project and then creates indexes for each one of them.
    :return: list of indexes that has been invoked to create
             (could've been created earlier, it doesn't raise in this case)
    """
    models = get_models(app_settings, logger)
    return await db_engine.configure_database(models)


async def get_fixtures(app_settings, logger) -> list:
    apps_folder_name = app_settings.APPS_FOLDER_NAME
    funcs = []
    for app in app_settings.APPS:
        app_path = f"{apps_folder_name}/{app}"
        modules = [
            f for f in pkgutil.walk_packages(path=[app_path]) if f.name == "fixtures"
        ]
        if not modules:
            continue
        for module in modules:
            path_to_fixtures_func = f"{apps_folder_name}.{app}.fixtures".replace(
                "/", "."
            )
            mudule = importlib.import_module(path_to_fixtures_func)
            if module.ispkg:
                module_funcs = [
                    x[0] for x in inspect.getmembers(mudule, inspect.isfunction)
                ]
            else:
                try:
                    module_funcs = pyclbr.readmodule(path_to_fixtures_func).keys()
                except (AttributeError, ImportError):
                    logger.warning(
                        f"Unable to read module attributes in {path_to_fixtures_func}"
                    )
                    continue
            funcs.extend([getattr(mudule, func) for func in module_funcs])
    return list(filter(lambda x: x.__name__ == "run_fixtures", funcs))


async def create_fixtures(app_settings, logger):
    fixtures = await get_fixtures(app_settings, logger)
    for func in fixtures:
        await func()
