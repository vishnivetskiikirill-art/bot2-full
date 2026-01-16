from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
WEBAPP_DIR = BASE_DIR / "api" / "webapp"

@app.get("/api/health")
def health():
    return {"status": "ok"}

# ВАЖНО: монтируем webapp КАК КОРЕНЬ
app.mount("/", StaticFiles(directory=WEBAPP_DIR, html=True), name="webapp")
