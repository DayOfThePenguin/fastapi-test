from fastapi import Form
from starlette.requests import Request
from starlette.responses import HTMLResponse


from routers import websockets, molecules
from utils.app_generator import create_app, add_static_routes_to_app
import utils.scratch
from utils.constants import DEFAULT_LEVELS, DEFAULT_LPP, TEMPLATES


app = create_app()
app.include_router(websockets.router)
app.include_router(molecules.router)


def generate_home_html_response():
    with open("frontend/dist/index.html", "r") as home_file:
        html_content = home_file.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return generate_home_html_response()


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


app = add_static_routes_to_app(app)  # add static routes at the end so
