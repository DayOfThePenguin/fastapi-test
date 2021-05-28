from fastapi import APIRouter, HTTPException, Query
from starlette.requests import Request

from database.db import get_database
from database.models import WikiMap
from utils.constants import DEFAULT_LEVELS, DEFAULT_LPP, MAX_LEVELS, MAX_LPP, TEMPLATES

router = APIRouter()

db = get_database()


@router.get("/json/{title}")
async def get_json(
    title: str,
    levels: int = Query(DEFAULT_LEVELS, gt=0, lt=MAX_LEVELS),
    lpp: int = Query(DEFAULT_LPP, gt=0, lt=MAX_LPP),
):
    title = title.replace("_", " ")
    with db.Session() as sess:
        result = (
            sess.query(WikiMap).filter_by(title=title, levels=levels, lpp=lpp).first()
        )
        if result is None:
            raise HTTPException(status_code=404, detail="json doesn't exist")
        else:
            return result.json_data


@router.get("/test")
async def ws_test(request: Request):
    return TEMPLATES.TemplateResponse("test.html", {"request": request})


@router.get("/map/{title}")
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
