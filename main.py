from fastapi import FastAPI
import uvicorn
from src.routes import tags

app = FastAPI()

app.include_router(tags.router, prefix='/api')
#app.include_router(photos.router, prefix='/api')
@app.get("/")
def index():
    return {"msg": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# coś innego
