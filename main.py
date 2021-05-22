import logging

from fastapi import FastAPI, Form, HTTPException, Query
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.routing import Mount
from sqlalchemy.exc import OperationalError


from database.db import Database
from database.models import WikiMap
import utils.scratch

DEFAULT_LEVELS = 3
DEFAULT_LPP = 8
MAX_LEVELS = 5
MAX_LPP = 16
TEMPLATES = Jinja2Templates(directory="static/templates")


def create_app() -> FastAPI:
    routes = [
        Mount(
            "/home",
            app=StaticFiles(directory="frontend/dist", html=True),
            name="frontend",
        ),
        Mount(
            "/js",
            app=StaticFiles(directory="frontend/dist/js"),
            name="js",
        ),
        # Mount(
        #     "/css",
        #     app=StaticFiles(directory="frontend/dist/css"),
        #     name="css",
        # ),
        Mount(
            "/img",
            app=StaticFiles(directory="frontend/dist/img"),
            name="img",
        ),
    ]
    new_app = FastAPI(title="WikiMap", version="0.0.2", debug=True, routes=routes)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    new_app.logger = logger
    new_app.mount("/static", StaticFiles(directory="static"), name="static")
    try:  # default: try production ssl
        new_app.db = Database()
        sess = new_app.db.Session()
        sess.query(WikiMap).first()
        sess.close()
        new_app.logger.info("SSL connection to database SUCCEEDED")
    except OperationalError:  # happens on local db
        new_app.logger.critical("SSL connection to database FAILED")
        new_app.db = Database(sslmode=False)

    return new_app


app = create_app()


@app.get("/", response_class=RedirectResponse)
async def home(request: Request):
    return RedirectResponse("/home")


@app.post("/search")
async def search(
    request: Request,
    title_query: str = Form(...),
    levels: int = Form(DEFAULT_LEVELS),
    lpp: int = Form(DEFAULT_LPP),
):
    SUGGESTIONS = utils.scratch.search_title(title_query)
    if SUGGESTIONS is None:
        return TEMPLATES.TemplateResponse(
            "err_no_page.html", {"request": request, "title_query": title_query}
        )
    else:
        return TEMPLATES.TemplateResponse(
            "disambiguation.html",
            {
                "request": request,
                "suggestions": SUGGESTIONS,
                "levels": levels,
                "lpp": lpp,
                "title_query": title_query,
            },
        )


@app.get("/json/{title}")
async def get_json(
    title: str,
    levels: int = Query(..., gt=0, lt=MAX_LEVELS),
    lpp: int = Query(..., gt=0, lt=MAX_LPP),
):
    title = title.replace("_", " ")
    with app.db.Session() as sess:
        result = (
            sess.query(WikiMap).filter_by(title=title, levels=levels, lpp=lpp).first()
        )
        if result is None:
            raise HTTPException(status_code=404, detail="json doesn't exist")
        else:
            return result.json_data


@app.get("/map/{title}")
async def graph_json(
    request: Request,
    title: str,
    levels: int = Query(..., gt=0, lt=MAX_LEVELS),
    lpp: int = Query(..., gt=0, lt=MAX_LPP),
):
    title = title.replace("_", " ")
    with app.db.Session() as sess:
        app.logger.info("%s, %i, %i", title, levels, lpp)
        result = (
            sess.query(WikiMap).filter_by(title=title, levels=levels, lpp=lpp).first()
        )
        if result is None:
            raise HTTPException(status_code=404, detail="map doesn't exist")
        else:
            return TEMPLATES.TemplateResponse(
                "interface.html", {"request": request, "map": result}
            )
