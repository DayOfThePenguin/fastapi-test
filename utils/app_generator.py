import logging
import re
from typing import Dict

from fastapi import FastAPI
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from database.db import get_database


def get_logging_config() -> logging.Logger:
    """sets up and returns logging config for the app

    Returns
    -------
    logger : Logger
        logger to be added to the app
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def get_static_routes():
    """the static routes the fastapi object should attempt to mount

    called by add_static_routes_to_app(), returns a dict of paths and associated names
    to try to mount to the fastapi object. the length of paths is enforced to be equal
    to the length of names to avoid errors when adding routes to the app.

    Returns
    -------
    routes : Dict["paths": List[str], "names": List[str]]
        routes to attempt to mount; each url should be relative (no leading '/') and
        each name should specify how you want the url to be mounted on the app (i.e.
        name of 'js' will be mounted under '/js' and named 'js')

    Raises
    ------
    ValueError
        if the length of paths != length of names (every url must be named)
    """
    paths = [
        "frontend/dist/js",
        "frontend/dist/css",
        "frontend/dist/fonts",
        "frontend/dist/img",
        "static/icons",
        "static",
    ]
    names = [
        "js",
        "css",
        "fonts",
        "img",
        "",
        "static",
    ]
    if len(paths) != len(names):
        raise ValueError("Every URL must have a corresponding name")
    routes = {"paths": paths, "names": names}
    return routes


def add_static_routes_to_app(app: FastAPI) -> FastAPI:
    """take a fastapi instance, add static routes, and return a new instance

    gets static routes from get_static_routes() and tried to append each of them to
    the fastapi instance. if unsuccessful, the failure to mount will be logged and the
    function will move on. failure to mount DOES NOT raise an exception.

    Parameters
    ----------
    app : FastAPI
        fastapi instance without routes mounted

    Returns
    -------
    app : FastAPI
        fastapi instance with valid routes from get_static_routes() mounted
    """
    routes = get_static_routes()
    for i in range(len(routes["paths"])):
        try:
            app.routes.append(
                Mount(
                    f"/{routes['names'][i]}",
                    StaticFiles(directory=routes["paths"][i]),
                    name=routes["names"][i],
                )
            )
        except RuntimeError:
            logging.warning("unable to mount %s", f"/{routes['names'][i]}")
    return app


def create_app() -> FastAPI:
    """Create a fastapi instance that has logging and database set up

    remove app config from main.py to keep main clean. static routes aren't added
    here because if you try to add things to the root level (i.e. favicons) here,
    you'll block every other app.route since the resolver looks top -> bottom

    Returns
    -------
    new_app : FastAPI
        app with logger and db attached
    """
    new_app = FastAPI(title="WikiMap", version="0.0.2", debug=False)
    new_app.logger = get_logging_config()
    new_app.db = get_database()
    return new_app


if __name__ == "__main__":
    print(get_static_routes())
