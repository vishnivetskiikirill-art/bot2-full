from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
from typing import Optional, List
from pydantic import BaseModel

from auth_admin import admin_required


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "webapp"
STATIC_DIR = WEBAPP_DIR / "static"
DATA_FILE = BASE_DIR / "data" / "listings.json"

# --- Static / pages ---
# папка static обязана существовать
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(WEBAPP_DIR / "index.html"))


@app.get("/detail.html")
def detail_page():
    return FileResponse(str(WEBAPP_DIR / "detail.html"))


# --- Data helpers ---
def load_listings() -> list[dict]:
    if not DATA_FILE.exists():
        return []

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    # гарантируем id
    for i, item in enumerate(data):
        if isinstance(item, dict) and "id" not in item:
            item["id"] = i + 1

    return data


def save_listings(items: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def next_id(items: list[dict]) -> int:
    max_id = 0
    for x in items:
        try:
            max_id = max(max_id, int(x.get("id") or 0))
        except Exception:
            continue
    return max_id + 1


# --- Public API ---
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/filters")
def filters():
    items = load_listings()

    cities = sorted({x.get("city") for x in items if x.get("city")})
    districts = sorted({x.get("district") for x in items if x.get("district")})
    types = sorted({x.get("type") for x in items if x.get("type")})

    return {"cities": cities, "districts": districts, "types": types}


@app.get("/api/listings")
def listings(
    city: Optional[str] = None,
    district: Optional[str] = None,
    type: Optional[str] = None,
    max_price: Optional[int] = Query(default=None, ge=0),
):
    items = load_listings()

    def ok(x: dict) -> bool:
        if city and x.get("city") != city:
            return False
        if district and x.get("district") != district:
            return False
        if type and x.get("type") != type:
            return False
        if max_price is not None:
            try:
                price = int(x.get("price") or 0)
            except Exception:
                price = 0
            if price > max_price:
                return False
        return True

    return [x for x in items if ok(x)]


@app.get("/api/listings/{listing_id}")
def listing_detail(listing_id: int):
    items = load_listings()
    for x in items:
        try:
            if int(x.get("id")) == listing_id:
                return x
        except Exception:
            continue
    raise HTTPException(status_code=404, detail="Listing not found")


# --- Admin API (protected) ---
class ListingIn(BaseModel):
    city: str
    district: Optional[str] = None
    type: str
    price: Optional[int] = None
    currency: str = "EUR"

    # (по желанию дальше добавим мультиязычные поля)
    title_ru: Optional[str] = None
    title_en: Optional[str] = None
    title_bg: Optional[str] = None
    title_he: Optional[str] = None

    desc_ru: Optional[str] = None
    desc_en: Optional[str] = None
    desc_bg: Optional[str] = None
    desc_he: Optional[str] = None


class ListingOut(ListingIn):
    id: int


@app.get("/api/admin/listings", response_model=List[ListingOut])
def admin_list(_admin_id: int = Depends(admin_required)):
    items = load_listings()
    return [ListingOut(**x) for x in items if isinstance(x, dict)]


@app.post("/api/admin/listings", response_model=ListingOut)
def admin_create(payload: ListingIn, _admin_id: int = Depends(admin_required)):
    items = load_listings()
    item = payload.model_dump()
    item["id"] = next_id(items)

    items.append(item)
    save_listings(items)

    return ListingOut(**item)


@app.delete("/api/admin/listings/{listing_id}")
def admin_delete(listing_id: int, _admin_id: int = Depends(admin_required)):
    items = load_listings()
    new_items = []
    removed = False

    for x in items:
        try:
            if int(x.get("id")) == listing_id:
                removed = True
                continue
        except Exception:
            pass
        new_items.append(x)

    if not removed:
        raise HTTPException(status_code=404, detail="Listing not found")

    save_listings(new_items)
    return {"ok": True, "id": listing_id}
