import uvicorn
from fastapi import FastAPI
from src.routes import tags, auth_new, pictures
from src import views

app = FastAPI()

app.include_router(views.router)
app.include_router(pictures.router, prefix="/wizards")
app.include_router(tags.router, prefix="/wizards")
app.include_router(auth_new.router, prefix="/api")
 
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
