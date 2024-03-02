from fastapi import FastAPI
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.routes import fake_pictures
from src.database.db import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

app = FastAPI()
app.include_router(fake_pictures.router, prefix="/wizards")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/login/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login_register.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request, db: Session = Depends(get_db)):
    pictures =  await fake_pictures.display_pictures(db)
    context = {"pictures" : pictures}
    return templates.TemplateResponse("index.html", {"request": request, "context":context})
    

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
