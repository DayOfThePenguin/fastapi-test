from fastapi import FastAPI, Form, HTTPException, Query
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from sqlalchemy.exc import OperationalError


from database.db import Database
from database.models import WikiMap
from utils.custom_logging import CustomizeLogger
import utils.scratch

MAX_LEVELS = 5
MAX_PPL = 16
TEMPLATES = Jinja2Templates(directory="static/templates")


def create_app() -> FastAPI:
    new_app = FastAPI(title="CustomLogger", debug=False)
    logger = CustomizeLogger.make_logger()
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


@app.get("/test", response_class=HTMLResponse)
async def vue(request: Request):
    return TEMPLATES.TemplateResponse("vue.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return TEMPLATES.TemplateResponse(
        "index.html", {"request": request, "maps": app.db.get_available_maps()}
    )


@app.post("/search")
async def search(
    request: Request,
    title_query: str = Form(...),
    levels: int = Form(...),
    ppl: int = Form(...),
):
    TITLE, SUGGESTIONS = utils.scratch.search_title(title_query)
    if SUGGESTIONS is None:
        return TEMPLATES.TemplateResponse(
            "err_no_page.html", {"request": request, "title_query": title_query}
        )
    elif TITLE is None:
        return TEMPLATES.TemplateResponse(
            "disambiguation.html",
            {
                "request": request,
                "suggestions": SUGGESTIONS,
                "levels": levels,
                "ppl": ppl,
                "title_query": title_query,
            },
        )
    else:
        LINKS = utils.scratch.get_links(TITLE, num_links=15)
        return LINKS


@app.get("/json/{title}")
async def get_json(
    title: str,
    levels: int = Query(..., gt=0, lt=MAX_LEVELS),
    ppl: int = Query(..., gt=0, lt=MAX_PPL),
):
    title = title.replace("_", " ")
    with app.db.Session() as sess:
        result = (
            sess.query(WikiMap)
            .filter_by(title=title, levels=levels, pages_per_level=ppl)
            .first()
        )
        if result is None:
            raise HTTPException(status_code=404, detail="json doesn't exist")
        else:
            return result.json_data


@app.get("/maps/{title}")
async def graph_json(
    request: Request,
    title: str,
    levels: int = Query(..., gt=0, lt=MAX_LEVELS),
    ppl: int = Query(..., gt=0, lt=MAX_PPL),
):
    title = title.replace("_", " ")
    with app.db.Session() as sess:
        app.logger.info("%s, %i, %i", title, levels, ppl)
        result = (
            sess.query(WikiMap)
            .filter_by(title=title, levels=levels, pages_per_level=ppl)
            .first()
        )
        if result is None:
            raise HTTPException(status_code=404, detail="map doesn't exist")
        else:
            return TEMPLATES.TemplateResponse(
                "interface.html", {"request": request, "map": result}
            )
