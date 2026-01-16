from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "data", "listings.json")

# ---------- API ----------
@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/listings")
def get_listings():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/filters")
def get_filters():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "cities": sorted({i["city"] for i in data}),
        "districts": sorted({i["district"] for i in data}),
        "types": sorted({i["type"] for i in data}),
    }

# ---------- MINI APP ----------
app.mount(
    "/", 
    StaticFiles(directory=os.path.join(BASE_DIR, "webapp"), html=True),
    name="webapp"
)
