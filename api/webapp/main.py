from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# ВАЖНО: webapp у тебя лежит в api/webapp
WEBAPP_DIR = BASE_DIR / "api" / "webapp"

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Раздаем весь webapp как статические файлы (index.html, app.js, detail.html и т.д.)
app.mount("/", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
