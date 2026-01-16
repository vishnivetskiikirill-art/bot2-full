import os
import json
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")
DATA_FILE = os.path.join(BASE_DIR, "data", "listings.json")

app = FastAPI()

# static: api/webapp/static/*
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(WEBAPP_DIR, "static")),
    name="static",
)

def load_listings():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # добавим id, чтобы было куда кликать
    out = []
    for i, item in enumerate(data, start=1):
        x = dict(item)
        x["id"] = i
        out.append(x)
    return out

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/")
def index_page():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))

@app.get("/detail")
def detail_page():
    return FileResponse(os.path.join(WEBAPP_DIR, "detail.html"))

@app.get("/api/listings")
def api_listings(
    city: str | None = None,
    district: str | None = None,
    type: str | None = None,
    max_price: int | None = None,
):
    items = load_listings()

    def ok(x):
        if city and x.get("city") != city:
            return False
        if district and x.get("district") != district:
            return False
        if type and x.get("type") != type:
            return False
        if max_price is not None:
            try:
                if int(x.get("price", 0)) > int(max_price):
                    return False
            except Exception:
                return False
        return True

    return JSONResponse([x for x in items if ok(x)])

@app.get("/api/listings/{listing_id}")
def api_listing_detail(listing_id: int):
    items = load_listings()
    for x in items:
        if x.get("id") == listing_id:
            return JSONResponse(x)
    return JSONResponse({"detail": "Not Found"}, status_code=404)

@app.get("/api/filters")
def api_filters():
    items = load_listings()
    cities = sorted({x.get("city") for x in items if x.get("city")})
    districts = sorted({x.get("district") for x in items if x.get("district")})
    types = sorted({x.get("type") for x in items if x.get("type")})
    return {"cities": cities, "districts": districts, "types": types}
