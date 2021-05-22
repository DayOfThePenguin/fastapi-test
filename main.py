import asyncio
import logging

from fastapi import FastAPI, Form, HTTPException, Query
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket
from sqlalchemy.exc import OperationalError


from database.db import Database
from database.models import WikiMap
import utils.scratch
from utils.wikigraph import WikipediaGraph

YIELD_SIZE = 15
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
        Mount(
            "/img",
            app=StaticFiles(directory="frontend/dist/img"),
            name="img",
        ),
    ]
    new_app = FastAPI(title="WikiMap", version="0.0.2", debug=False, routes=routes)
    try:
        new_app.routes.append(
            Mount(
                "/css",
                app=StaticFiles(directory="frontend/dist/css"),
                name="css",
            )
        )
    except RuntimeError:
        logging.warning(
            "can't find frontend/dist/css, frontend is running in DEBUG mode"
        )
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
    levels: int = Query(DEFAULT_LEVELS, gt=0, lt=MAX_LEVELS),
    lpp: int = Query(DEFAULT_LPP, gt=0, lt=MAX_LPP),
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


@app.websocket("/json/{title}/ws")
async def websocket_endpoint(title: str, websocket: WebSocket):
    title = title.replace("_", " ")
    graph = None
    gen = None
    sess = app.db.Session()
    result = sess.query(WikiMap).filter_by(title=title).first()
    logging.info("Database query returned %s", result)
    if result is None:
        graph = WikipediaGraph(title, levels=DEFAULT_LEVELS, lpp=DEFAULT_LPP)
        gen = graph.generate(yield_size=YIELD_SIZE)
        logging.info("Map %s doesn't exist in db", title)
    else:
        graph = WikipediaGraph(result.title, levels=result.levels, lpp=result.lpp)
        gen = graph.generate_from_wikimap(result, yield_size=YIELD_SIZE)
        logging.info("Map %s exists in db", title)
    await websocket.accept()
    steps = 0
    delay = [1.5, 1, 0.75]
    for json_chunk in gen:
        await websocket.send_json(json_chunk)
        if steps < 3:
            await asyncio.sleep(delay[0])
        elif steps < 5:
            await asyncio.sleep(delay[1])
        else:
            await asyncio.sleep(delay[2])
        steps += 1
    await websocket.close(code=1000)
    if result is None:
        page_map = WikiMap(
            title=graph.start_page,
            json_data=graph.get_json_dict(),
            levels=graph.levels,
            lpp=graph.lpp,
        )
        sess.add(page_map)
        sess.commit()
        sess.close()
        logging.info("Added missing map %s to db", title)


@app.get("/map/{title}")
async def graph_json(
    request: Request,
    title: str,
    levels: int = Query(DEFAULT_LEVELS, gt=0, lt=MAX_LEVELS),
    lpp: int = Query(DEFAULT_LPP, gt=0, lt=MAX_LPP),
):
    title = title.replace("_", " ")
    return TEMPLATES.TemplateResponse(
        "websocket.html", {"request": request, "title": title}
    )
