import os
from pathlib import Path


import wikipedia
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()

# domain where this api is hosted for example : localhost:5000/docs to see swagger documentation automagically generated.

URI = os.environ["DATABASE_URL"]
if URI.startswith("postgres://"):
    URI = URI.replace("postgres://", "postgresql://", 1)
# rest of connection code using the connection string `uri`

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="static/templates")


def search_result(page_name: str) -> str:
    return wikipedia.page(page_name)


def get_available_maps():
    data_path = Path("static/data")
    available_maps = []
    for child in data_path.iterdir():
        if child.suffix == ".json":
            available_maps.append(child.stem)
    return available_maps


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "maps": get_available_maps()}
    )


@app.get("/maps/{file_name}")
async def graph_json(file_name: str, request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse(
        "interface.html", {"request": request, "file_name": file_name}
    )
