from fastapi import FastAPI
import uvicorn


from src.routes import fake_pictures

app = FastAPI()


@app.get("/")
def index():
    return {"msg": "Hello World"}


app.include_router(fake_pictures.router, prefix="/wizards")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
