from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LISTINGS_PATH = DATA_DIR / "listings.json"

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-me")  # ключ для админ-добавления
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot")     # без @

app = FastAPI(title="Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG: Dict[str, Any] = {
    "cities": [
        {
            "code": "varna",
            "name": {"ru": "Варна", "en": "Varna", "bg": "Варна", "he": "ורנה"},
            "districts": [
                {"code":"center","name":{"ru":"Центр","en":"Center","bg":"Център","he":"מרכז"}},
                {"code":"asparuhovo","name":{"ru":"Аспарухово","en":"Asparuhovo","bg":"Аспарухово","he":"אספרוחובו"}},
                {"code":"galata","name":{"ru":"Галата","en":"Galata","bg":"Галата","he":"גלאטה"}},
                {"code":"briz","name":{"ru":"Бриз","en":"Briz","bg":"Бриз","he":"בריז"}},
                {"code":"chayka","name":{"ru":"Чайка","en":"Chayka","bg":"Чайка","he":"צ׳איקה"}},
                {"code":"levski","name":{"ru":"Левски","en":"Levski","bg":"Левски","he":"לבסקי"}},
                {"code":"mladost","name":{"ru":"Младост","en":"Mladost","bg":"Младост","he":"מלדוסט"}},
                {"code":"vazrazhdane","name":{"ru":"Возрождение","en":"Vazrazhdane","bg":"Възраждане","he":"ואזראז׳דנה"}},
                {"code":"vladislavovo","name":{"ru":"Владиславово","en":"Vladislavovo","bg":"Владиславово","he":"ולדיסלבובו"}},
                {"code":"vinitsa","name":{"ru":"Виница","en":"Vinitsa","bg":"Виница","he":"ויניצה"}},
                {"code":"trakata","name":{"ru":"Траката","en":"Trakata","bg":"Траката","he":"טרקאטה"}},
                {"code":"kaysieva_gradina","name":{"ru":"Кайсиева градина","en":"Kaysieva Gradina","bg":"Кайсиева градина","he":"קייסייבה גרדינה"}},
                {"code":"troshevo","name":{"ru":"Трошево","en":"Troshevo","bg":"Трошево","he":"טרושבו"}},
            ],
        }
    ],
    "property_types": [
        {"code":"apartment","name":{"ru":"Квартира","en":"Apartment","bg":"Апартамент","he":"דירה"}},
        {"code":"house","name":{"ru":"Дом","en":"House","bg":"Къща","he":"בית"}},
        {"code":"studio","name":{"ru":"Студия","en":"Studio","bg":"Студио","he":"סטודיו"}},
        {"code":"commercial","name":{"ru":"Коммерческая","en":"Commercial","bg":"Търговски","he":"מסחרי"}},
        {"code":"land","name":{"ru":"Участок","en":"Land","bg":"Парцел","he":"מגרש"}},
    ],
}

class ListingIn(BaseModel):
    city: str = "varna"
    district: str
    property_type: str
    price: int = Field(ge=0)
    currency: str = "EUR"
    title: Dict[str, str] = Field(default_factory=dict)        # ru/en/bg/he
    description: Dict[str, str] = Field(default_factory=dict)  # ru/en/bg/he
    contact_telegram: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool = True

def _load() -> List[Dict[str, Any]]:
    if not LISTINGS_PATH.exists():
        LISTINGS_PATH.write_text("[]", encoding="utf-8")
    return json.loads(LISTINGS_PATH.read_text(encoding="utf-8"))

def _save(items: List[Dict[str, Any]]) -> None:
    LISTINGS_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def _next_id(items: List[Dict[str, Any]]) -> int:
    return max([int(x.get("id", 0)) for x in items] + [0]) + 1

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/catalog")
def api_catalog():
    return {"catalog": CATALOG, "bot_username": BOT_USERNAME}

@app.get("/api/listings")
def api_listings(
    city: str = Query("varna"),
    district: Optional[str] = None,
    property_type: Optional[str] = None,
    max_price: Optional[int] = None,
):
    items = [x for x in _load() if x.get("is_active", True)]
    out = []
    for it in items:
        if it.get("city") != city:
            continue
        if district and it.get("district") != district:
            continue
        if property_type and it.get("property_type") != property_type:
            continue
        if max_price is not None and int(it.get("price", 0)) > max_price:
            continue
        out.append(it)
    out.sort(key=lambda x: int(x.get("id", 0)), reverse=True)
    return {"items": out, "count": len(out)}

@app.post("/api/listings")
def api_add_listing(payload: ListingIn, api_key: str = Query("")):
    if api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="bad api_key")

    items = _load()
    obj = payload.model_dump()
    obj["id"] = _next_id(items)
    items.append(obj)
    _save(items)
    return {"ok": True, "id": obj["id"]}

@app.post("/api/listings/{listing_id}/deactivate")
def api_deactivate(listing_id: int, api_key: str = Query("")):
    if api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="bad api_key")

    items = _load()
    for it in items:
        if int(it.get("id", 0)) == listing_id:
            it["is_active"] = False
            _save(items)
            return {"ok": True}
    raise HTTPException(status_code=404, detail="not found")