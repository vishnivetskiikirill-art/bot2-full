import os, json
from fastapi import Header, HTTPException, Depends
from telegram_webapp import verify_telegram_webapp_init_data

def get_bot_token() -> str:
    token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN (или TELEGRAM_TOKEN) не задан")
    return token

def get_admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "")
    return {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}

def get_webapp_user_id(x_tg_init_data: str = Header(default="")) -> int:
    try:
        data = verify_telegram_webapp_init_data(x_tg_init_data, get_bot_token())
        user_json = data.get("user")
        if not user_json:
            raise ValueError("Missing user")
        user = json.loads(user_json)
        return int(user["id"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {e}")

def admin_required(user_id: int = Depends(get_webapp_user_id)) -> int:
    if user_id not in get_admin_ids():
        raise HTTPException(status_code=403, detail="Forbidden")
    return user_id
