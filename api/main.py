from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json

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

INDEX_PATH = os.path.join(WEBAPP_DIR, "index.html")
LISTINGS_PATH = os.path.join(DATA_DIR, "listings.json")

# --- Static files ---
# Будет доступно:
# /static/app.js
# /static/styles.css
app.mount("/static", StaticFiles(directory=WEBAPP_DIR), name="static")


# --- WebApp (frontend) ---
@app.get("/")
def webapp_index():
    if not os.path.exists(INDEX_PATH):
        return JSONResponse(
            status_code=500,
            content={"error": "webapp/index.html not found", "expected": INDEX_PATH},
        )
    return FileResponse(INDEX_PATH)


# --- API ---
@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/listings")
def listings():
    if not os.path.exists(LISTINGS_PATH):
        return JSONResponse(
            status_code=500,
            content={"error": "data/listings.json not found", "expected": LISTINGS_PATH},
        )
    with open(LISTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/filters")
def filters():
    if not os.path.exists(LISTINGS_PATH):
        return JSONResponse(
            status_code=500,
            content={"error": "data/listings.json not found", "expected": LISTINGS_PATH},
        )
    with open(LISTINGS_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    cities = sorted({x.get("city", "") for x in items if x.get("city")})
    districts = sorted({x.get("district", "") for x in items if x.get("district")})
    types = sorted({x.get("type", "") for x in items if x.get("type")})

    return {"cities": cities, "districts": districts, "types": types}
