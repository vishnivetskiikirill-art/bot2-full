from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
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
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")
DATA_DIR = os.path.join(BASE_DIR, "data")


# --- API (сначала!) ---
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/listings")
def listings():
    with open(os.path.join(DATA_DIR, "listings.json"), "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/filters")
def filters():
    with open(os.path.join(DATA_DIR, "listings.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "cities": sorted({x.get("city") for x in data if x.get("city")}),
        "districts": sorted({x.get("district") for x in data if x.get("district")}),
        "types": sorted({x.get("type") for x in data if x.get("type")}),
    }


# --- WEBAPP (после API): "/" всегда отдаёт index.html ---
@app.get("/")
def root():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))


# Отдаём статику как обычные файлы: /app.js, /style.css, /i18n.js и т.д.
app.mount("/", StaticFiles(directory=WEBAPP_DIR, html=True), name="webapp")
