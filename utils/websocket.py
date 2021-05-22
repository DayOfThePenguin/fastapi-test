from fastapi import FastAPI
from starlette.websockets import WebSocket
from starlette.responses import HTMLResponse

import asyncio

from database.db import Database
from database.models import WikiMap
from utils.wikigraph import WikipediaGraph

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Graph Test</title>
        <style>
        body { margin: 0; }
        </style>
    <script src="//unpkg.com/3d-force-graph"></script>
    </head>
    <body>
        <div id="3d-graph"></div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            const initData = {
                nodes: [],
                links: []
            };

            const elem = document.getElementById("3d-graph");
            const Graph = ForceGraph3D()(elem)
                .nodeLabel("name")
                .nodeAutoColorBy("group")
                .graphData(initData);

            ws.onmessage = function(event) {
                const jsonMessage = JSON.parse(event.data);
                const newNodes = jsonMessage.nodes;
                const newLinks = jsonMessage.links;
                console.log(newNodes);
                console.log(newLinks);
                const { nodes, links } = Graph.graphData();

                Graph.graphData({
                    nodes: [...nodes, ...newNodes],
                    links: [...links, ...newLinks]
                }); 
            };
        </script>
    </body>
</html>
"""


"""
               



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


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    database = Database(sslmode=False)
    with database.Session() as sess:
        result = sess.query(WikiMap).filter_by(title="Elon Musk").first()

    graph = WikipediaGraph("Elon Musk", levels=3, lpp=12)
    await websocket.accept()
    for json_chunk in graph.generate_from_wikimap(result, yield_size=5):
        await websocket.send_json(json_chunk)
        await asyncio.sleep(1)
    await websocket.close(code=1000)
