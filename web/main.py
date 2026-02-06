from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from importlib import import_module
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory="templates")

routes_path = Path(__file__).parent / "routes"
for file in routes_path.glob("*.py"):
    if file.name == "__init__.py":
        continue
    module_name = f"routes.{file.stem}"
    module = import_module(module_name)
    if hasattr(module, "router"):
        app.include_router(module.router)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page": "index"})

@app.get("/docs/api", response_class=HTMLResponse)
def apidocs(request: Request):
    return templates.TemplateResponse("docs/api.html", {"request": request, "page": "api"})

@app.get("/docs/whois", response_class=HTMLResponse)
def whoisdocs(request: Request):
    return templates.TemplateResponse("docs/whois.html", {"request": request, "page": "whois"})