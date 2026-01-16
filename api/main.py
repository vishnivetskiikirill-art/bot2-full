from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# CORS (на всякий)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Статика (JS, CSS)
app.mount("/webapp", StaticFiles(directory=WEBAPP_DIR), name="webapp")

# Главная — HTML
@app.get("/")
def root():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))

# Health
@app.get("/api/health")
def health():
    return {"status": "ok"}

# Listings
@app.get("/api/listings")
def listings():
    with open(os.path.join(DATA_DIR, "listings.json"), "r", encoding="utf-8") as f:
        return json.load(f)

# Filters
@app.get("/api/filters")
def filters():
    with open(os.path.join(DATA_DIR, "listings.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "cities": sorted({x["city"] for x in data}),
        "districts": sorted({x["district"] for x in data}),
        "types": sorted({x["type"] for x in data}),
    }
