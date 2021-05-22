import logging
from fastapi import FastAPI
from starlette.requests import Request
from starlette.websockets import WebSocket
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

import asyncio

from database.db import Database
from database.models import WikiMap
from utils.wikigraph import WikipediaGraph

app = FastAPI()

TEMPLATES = Jinja2Templates(directory="../static/templates")


"""
          var simulation = d3.forceSimulation(nodes)
                .force("charge", d3.forceManyBody())
                .force("link", d3.forceLink(links))
                .force("center", d3.forceCenter());     



try {
                    Graph.graphData({
                        nodes: [...nodes, ...newNodes],
                        links: [...links, ...newLinks]
                        });
                } catch(ReferenceError) {
                    Graph.graphData({
                        nodes: [...newNodes],
                        links: [...newLinks]
                        });
                }
"""


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    title = "COVID-19 pandemic"
    return TEMPLATES.TemplateResponse(
        "websocket.html", {"request": request, "title": title}
    )


@app.websocket("/json/{title}/ws")
async def websocket_endpoint(title: str, websocket: WebSocket):
    title = title.replace("_", " ")
    database = Database(sslmode=False)
    with database.Session() as sess:
        result = sess.query(WikiMap).filter_by(title=title, lpp=12).first()
        logging.info(result)
    graph = WikipediaGraph("Elon Musk", levels=3, lpp=12)
    await websocket.accept()
    steps = 0
    delay = [1.5, 1, 0.75]
    for json_chunk in graph.generate_from_wikimap(result, yield_size=15):
        await websocket.send_json(json_chunk)
        if steps < 3:
            await asyncio.sleep(delay[0])
        elif steps < 5:
            await asyncio.sleep(delay[1])
        else:
            await asyncio.sleep(delay[2])
        steps += 1
    await websocket.close(code=1000)
