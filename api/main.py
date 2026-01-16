from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "listings.json"
WEBAPP_DIR = BASE_DIR / "webapp"

SUPPORTED_LANGS = {"en", "ru", "bg", "he"}

# 1) Переводы (можешь расширять)
CITY_I18N = {
    "Limassol": {"en": "Limassol", "ru": "Лимассол", "bg": "Лимасол", "he": "לימסול"},
    "Paphos":   {"en": "Paphos",   "ru": "Пафос",    "bg": "Пафос",   "he": "פאפוס"},
}

DISTRICT_I18N = {
    "Germasogeia": {"en": "Germasogeia", "ru": "Гермасойя", "bg": "Гермасоя", "he": "גרמסוג'יה"},
    "Kato Paphos": {"en": "Kato Paphos", "ru": "Като Пафос", "bg": "Като Пафос", "he": "קאפו פאפוס"},
}

TYPE_I18N = {
    "Apartment": {"en": "Apartment", "ru": "Квартира", "bg": "Апартамент", "he": "דירה"},
    "House":     {"en": "House",     "ru": "Дом",      "bg": "Къща",       "he": "בית"},
}

# Если title/description тоже хочешь переводить — добавишь как словарь по id.
# Пока оставим title как есть (или можешь сделать TITLE_I18N по id).

def get_lang(lang: str | None) -> str:
    if not lang:
        return "en"
    lang = lang.lower()
    return lang if lang in SUPPORTED_LANGS else "en"

def t(mapping: dict, key: str, lang: str) -> str:
    if not key:
        return key
    return mapping.get(key, {}).get(lang) or mapping.get(key, {}).get("en") or key

def load_listings() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/filters")
def api_filters(lang: str | None = Query(default="en")):
    lang = get_lang(lang)
    listings = load_listings()

    cities = sorted({x.get("city", "") for x in listings if x.get("city")})
    districts = sorted({x.get("district", "") for x in listings if x.get("district")})
    types = sorted({x.get("type", "") for x in listings if x.get("type")})

    # ВАЖНО: возвращаем value (сырой) + label (перевод)
    return {
        "cities": [{"value": c, "label": t(CITY_I18N, c, lang)} for c in cities],
        "districts": [{"value": d, "label": t(DISTRICT_I18N, d, lang)} for d in districts],
        "types": [{"value": tp, "label": t(TYPE_I18N, tp, lang)} for tp in types],
    }

@app.get("/api/listings")
def api_listings(
    lang: str | None = Query(default="en"),
    city: str | None = None,
    district: str | None = None,
    type: str | None = None,
    max_price: int | None = None,
):
    lang = get_lang(lang)
    listings = load_listings()

    # фильтруем по СЫРЫМ значениям (en), которые хранятся в json
    def ok(x: dict) -> bool:
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

    filtered = [x for x in listings if ok(x)]

    # добавляем label-поля для отображения на выбранном языке
    out = []
    for x in filtered:
        item = dict(x)
        item["city_label"] = t(CITY_I18N, item.get("city", ""), lang)
        item["district_label"] = t(DISTRICT_I18N, item.get("district", ""), lang)
        item["type_label"] = t(TYPE_I18N, item.get("type", ""), lang)
        out.append(item)

    return out

# отдаём фронт мини-аппа
if WEBAPP_DIR.exists():
    app.mount("/webapp", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
