import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent  # api/webapp
DATA_FILE = BASE_DIR.parent / "data" / "listings.txt"  # api/data/listings.txt

app = FastAPI(title="Real Estate WebApp API")

# Чтобы WebApp мог дергать API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _read_listings() -> List[Dict[str, Any]]:
    """
    Ожидаем в api/data/listings.txt JSON-массив.
    Если файл пустой или нет — вернем пустой список.
    """
    if not DATA_FILE.exists():
        return []
    raw = DATA_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []

def _unique(values: List[str]) -> List[str]:
    return sorted(list({v for v in values if v and str(v).strip()}))

@app.get("/", response_class=HTMLResponse)
def home():
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>index.html not found</h1>", status_code=404)
    return FileResponse(index_path)

@app.get("/app.js")
def app_js():
    p = BASE_DIR / "app.js"
    return FileResponse(p) if p.exists() else JSONResponse({"error": "app.js not found"}, status_code=404)

@app.get("/styles.css")
def styles_css():
    p = BASE_DIR / "styles.css"
    return FileResponse(p) if p.exists() else JSONResponse({"error": "styles.css not found"}, status_code=404)

@app.get("/api/options")
def options():
    listings = _read_listings()
    cities = _unique([str(x.get("city", "")) for x in listings])
    districts = _unique([str(x.get("district", "")) for x in listings])
    types_ = _unique([str(x.get("type", "")) for x in listings])
    return {"cities": cities, "districts": districts, "types": types_}

@app.get("/api/listings")
def get_listings(
    city: Optional[str] = None,
    district: Optional[str] = None,
    type: Optional[str] = Query(None, alias="type"),
    max_price: Optional[int] = None,
):
    listings = _read_listings()

    def ok(item: Dict[str, Any]) -> bool:
        if city and str(item.get("city", "")).lower() != city.lower():
            return False
        if district and str(item.get("district", "")).lower() != district.lower():
            return False
        if type and str(item.get("type", "")).lower() != type.lower():
            return False
        if max_price is not None:
            try:
                price = int(item.get("price", 0))
            except Exception:
                price = 0
            if price > max_price:
                return False
        return True

    filtered = [x for x in listings if ok(x)]
    return {"count": len(filtered), "items": filtered}

# Railway/uvicorn entrypoint:
# railway ставит PORT, мы используем его
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
