from fastapi import FastAPI
import uvicorn
from src.routes import 
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.routes import fake_pictures, tags


app = FastAPI()

app.include_router(fake_pictures.router, prefix="/wizards")
app.include_router(tags.router, prefix='/wizards')

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/login/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("login_register.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
