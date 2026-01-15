import os
import json
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-me")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing in bot/.env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def is_admin(user_id: int) -> bool:
    return ADMIN_TELEGRAM_ID != 0 and user_id == ADMIN_TELEGRAM_ID

def kb_webapp() -> ReplyKeyboardMarkup:
    if not WEBAPP_URL:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⚠️ WEBAPP_URL не задан")]],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Каталог", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True
    )

# ---------- API helpers ----------
async def api_post(path: str, payload: dict):
    url = f"{API_BASE}{path}"
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=payload, timeout=30) as r:
            text = await r.text()
            if r.status != 200:
                raise RuntimeError(f"API {r.status}: {text}")
            return json.loads(text)

async def api_deactivate(listing_id: int):
    url = f"{API_BASE}/api/listings/{listing_id}/deactivate?api_key={ADMIN_API_KEY}"
    async with aiohttp.ClientSession() as s:
        async with s.post(url, timeout=30) as r:
            text = await r.text()
            if r.status != 200:
                raise RuntimeError(f"API {r.status}: {text}")
            return json.loads(text)

# ---------- FSM for /add ----------
class AddFlow(StatesGroup):
    district = State()
    ptype = State()
    price = State()
    title_ru = State()
    title_en = State()
    title_bg = State()
    title_he = State()
    desc_ru = State()
    desc_en = State()
    desc_bg = State()
    desc_he = State()
    contact_tg = State()
    contact_phone = State()

@dp.message(Command("myid"))
async def myid(message: Message):
    await message.answer(f"Твой Telegram ID: {message.from_user.id}\nВставь его в .env как ADMIN_TELEGRAM_ID")

@dp.message(CommandStart())
async def start(message: Message):
    # deep link: /start listing_123
    args = (message.text or "").split(maxsplit=1)
    if len(args) > 1 and args[1].startswith("listing_"):
        listing_id = args[1].replace("listing_", "").strip()
        # сообщение админу
        if ADMIN_TELEGRAM_ID != 0:
            await bot.send_message(
                ADMIN_TELEGRAM_ID,
                f"📩 Заявка от @{message.from_user.username or 'no_username'} (id {message.from_user.id}) по объекту ID={listing_id}"
            )
        await message.answer(
            f"✅ Спасибо! Я передал запрос по объекту ID={listing_id}.\n"
            f"Я скоро отвечу тебе здесь.",
            reply_markup=kb_webapp()
        )
        return

    await message.answer(
        "Привет! Это каталог недвижимости.\n"
        "Нажми кнопку «🏠 Каталог», чтобы открыть Mini App.\n\n"
        "Админ-команды (только для владельца): /add /del /help /myid",
        reply_markup=kb_webapp()
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("Команды:\n/start — каталог\n/myid — показать твой ID")
        return
    await message.answer(
        "Админ-команды:\n"
        "/add — добавить объявление\n"
        "/del <ID> — скрыть объявление\n"
        "/myid — узнать свой id\n\n"
        "Важно: API_BASE и ADMIN_API_KEY должны быть правильные."
    )

@dp.message(Command("add"))
async def add_cmd(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Нет доступа.")
        return
    await state.clear()
    await state.set_state(AddFlow.district)
    await message.answer("Ок. Введи district code (например: briz / chayka / center / vinitsa).")

@dp.message(AddFlow.district)
async def st_district(message: Message, state: FSMContext):
    code = (message.text or "").strip().lower()
    await state.update_data(district=code)
    await state.set_state(AddFlow.ptype)
    await message.answer("Введи type code (apartment/house/studio/commercial/land).")

@dp.message(AddFlow.ptype)
async def st_ptype(message: Message, state: FSMContext):
    code = (message.text or "").strip().lower()
    await state.update_data(property_type=code)
    await state.set_state(AddFlow.price)
    await message.answer("Цена числом (EUR), например 125000.")

@dp.message(AddFlow.price)
async def st_price(message: Message, state: FSMContext):
    try:
        price = int((message.text or "").strip())
        if price < 0: raise ValueError
    except Exception:
        await message.answer("Цена должна быть числом (например 125000).")
        return
    await state.update_data(price=price)
    await state.set_state(AddFlow.title_ru)
    await message.answer("Заголовок RU:")

@dp.message(AddFlow.title_ru)
async def st_tr(message: Message, state: FSMContext):
    await state.update_data(title_ru=(message.text or "").strip())
    await state.set_state(AddFlow.title_en)
    await message.answer("Title EN:")

@dp.message(AddFlow.title_en)
async def st_te(message: Message, state: FSMContext):
    await state.update_data(title_en=(message.text or "").strip())
    await state.set_state(AddFlow.title_bg)
    await message.answer("Title BG:")

@dp.message(AddFlow.title_bg)
async def st_tb(message: Message, state: FSMContext):
    await state.update_data(title_bg=(message.text or "").strip())
    await state.set_state(AddFlow.title_he)
    await message.answer("Title HE:")

@dp.message(AddFlow.title_he)
async def st_th(message: Message, state: FSMContext):
    await state.update_data(title_he=(message.text or "").strip())
    await state.set_state(AddFlow.desc_ru)
    await message.answer("Описание RU:")

@dp.message(AddFlow.desc_ru)
async def st_dr(message: Message, state: FSMContext):
    await state.update_data(desc_ru=(message.text or "").strip())
    await state.set_state(AddFlow.desc_en)
    await message.answer("Description EN:")

@dp.message(AddFlow.desc_en)
async def st_de(message: Message, state: FSMContext):
    await state.update_data(desc_en=(message.text or "").strip())
    await state.set_state(AddFlow.desc_bg)
    await message.answer("Description BG:")

@dp.message(AddFlow.desc_bg)
async def st_db(message: Message, state: FSMContext):
    await state.update_data(desc_bg=(message.text or "").strip())
    await state.set_state(AddFlow.desc_he)
    await message.answer("Description HE:")

@dp.message(AddFlow.desc_he)
async def st_dh(message: Message, state: FSMContext):
    await state.update_data(desc_he=(message.text or "").strip())
    await state.set_state(AddFlow.contact_tg)
    await message.answer("Контакт Telegram (например @yourusername) или '-' если не надо:")

@dp.message(AddFlow.contact_tg)
async def st_ctg(message: Message, state: FSMContext):
    txt = (message.text or "").strip()
    await state.update_data(contact_telegram=None if txt == "-" else txt)
    await state.set_state(AddFlow.contact_phone)
    await message.answer("Телефон (+359...) или '-' если не надо:")

@dp.message(AddFlow.contact_phone)
async def st_cph(message: Message, state: FSMContext):
    txt = (message.text or "").strip()
    data = await state.get_data()
    contact_phone = None if txt == "-" else txt

    payload = {
        "city": "varna",
        "district": data["district"],
        "property_type": data["property_type"],
        "price": data["price"],
        "currency": "EUR",
        "title": {
            "ru": data["title_ru"], "en": data["title_en"], "bg": data["title_bg"], "he": data["title_he"]
        },
        "description": {
            "ru": data["desc_ru"], "en": data["desc_en"], "bg": data["desc_bg"], "he": data["desc_he"]
        },
        "contact_telegram": data.get("contact_telegram") or f"@{message.from_user.username}" if message.from_user.username else None,
        "contact_phone": contact_phone,
        "is_active": True
    }

    try:
        res = await api_post(f"/api/listings?api_key={ADMIN_API_KEY}", payload)
    except Exception as e:
        await message.answer(f"❌ Ошибка добавления: {e}")
        await state.clear()
        return

    await message.answer(f"✅ Добавлено! ID: {res.get('id')}\nОткрой каталог и нажми Show.")
    await state.clear()

@dp.message(Command("del"))
async def del_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Нет доступа.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Используй: /del <ID>\nНапример: /del 3")
        return
    try:
        listing_id = int(parts[1])
    except Exception:
        await message.answer("ID должен быть числом.")
        return

    try:
        await api_deactivate(listing_id)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        return

    await message.answer(f"✅ Объявление {listing_id} скрыто (deactivate).")

@dp.message(F.web_app_data)
async def from_webapp(message: Message):
    # если потом захочешь: получать фильтры/заявки прямо из WebApp через tg.sendData(...)
    await message.answer(f"Получил данные из Mini App:\n{message.web_app_data.data}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())