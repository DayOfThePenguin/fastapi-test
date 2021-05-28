import asyncio
import json
import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket

from database.db import get_database
from database.models import WikiMap
from utils.wikigraph import WikipediaGraph
from utils.constants import *


router = APIRouter()
db = get_database()


@router.websocket("/json/{title}/ws")
async def websocket_endpoint(title: str, websocket: WebSocket):
    title = title.replace("_", " ")
    graph = None
    gen = None
    sess = db.Session()
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


@router.websocket("/home")
async def home_websocket(websocket: WebSocket):
    home_data = json.loads("static/maps/home.json")
    home_map = WikiMap(title="home", json_data=home_data, levels=2, lpp=1)
    graph = WikipediaGraph(home_map, levels=2, lpp=1)
    gen = graph.generate_from_wikimap(home_map, yield_size=1)
    await websocket.accept()

    delay = 0.5
    for json_chunk in gen:
        await websocket.send_json(json_chunk)
        await asyncio.sleep(delay)
    await websocket.close(code=1000)
