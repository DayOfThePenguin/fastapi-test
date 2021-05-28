import logging

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

    called by add_static_routes_to_app(), returns a dict of urls and associated names
    to try to mount to the fastapi object. the length of urls is enforced to be equal
    to the length of names to avoid errors when adding routes to the app.

    Returns
    -------
    routes : Dict["urls": List[str], "names": List[str]]
        routes to attempt to mount; each url should be relative (no leading '/') and
        each name should specify how you want the url to be mounted on the app (i.e.
        name of 'js' will be mounted under '/js' and named 'js')

    Raises
    ------
    ValueError
        [description]
    """
    urls = [
        "frontend/dist/js",
        "frontend/dist/css",
        "frontend/dist/fonts",
        "frontend/dist/img",
        "static",
    ]
    names = [
        "js",
        "css",
        "fonts",
        "img",
        "static",
    ]
    if len(urls) != len(names):
        raise ValueError("Every URL must have a corresponding name")
    routes = {"urls": urls, "names": names}
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
    for i in range(len(routes["urls"])):
        try:
            app.routes.append(
                Mount(
                    f"/{routes['names'][i]}",
                    StaticFiles(directory=routes["urls"][i]),
                    name=routes["names"][i],
                )
            )
        except RuntimeError:
            logging.warning("unable to mount %s", f"/{routes['names'][i]}")
    return app


def create_app() -> FastAPI:
    """Create a fastapi instance that has logging, database, and static routes set up

    remove app config from main.py to keep main clean

    Returns
    -------
    new_app : FastAPI
        app with logger, db, and routes attached
    """
    new_app = FastAPI(title="WikiMap", version="0.0.2", debug=False)
    new_app.logger = get_logging_config()
    new_app = add_static_routes_to_app(new_app)
    new_app.db = get_database()
    return new_app
