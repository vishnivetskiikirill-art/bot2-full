from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP = os.path.join(BASE_DIR, "webapp")
DATA = os.path.join(BASE_DIR, "data")


# ---------- API ----------
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/listings")
def listings():
    with open(os.path.join(DATA, "listings.json"), encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/filters")
def filters():
    with open(os.path.join(DATA, "listings.json"), encoding="utf-8") as f:
        items = json.load(f)

    return {
        "cities": sorted({i["city"] for i in items}),
        "districts": sorted({i["district"] for i in items}),
        "types": sorted({i["type"] for i in items}),
    }


# ---------- WEBAPP ----------
@app.get("/")
def index():
    return FileResponse(os.path.join(WEBAPP, "index.html"))


@app.get("/{file_name}")
def static_files(file_name: str):
    file_path = os.path.join(WEBAPP, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"detail": "Not Found"}
