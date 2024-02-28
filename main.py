from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def index():
    return {"msg": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


# komentarz dodany na próbę
