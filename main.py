import os
import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.filters import Command

# =====================
# CONFIG
# =====================
BOT_TOKEN = "8467514297:AAHPTdnSZ-SLLBP51tuhM74PpkrEQ0KwhKE"
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable yo'q")

# =====================
# MENU
# =====================
MENU = {
    "🍔 Cheeseburger": 25000,
    "🍔 Double burger": 32000,
    "🍔 Chicken burger": 27000,
    "🌯 Lavash tovuqli": 28000,
    "🌯 Lavash mol go‘shtli": 32000,
    "🌯 Lavash pishloqli": 30000,
    "🌭 Hot-dog classic": 18000,
    "🌭 Hot-dog double": 23000,
    "🍟 Kartoshka fri": 15000,
    "🍟 Kartoshka wedges": 17000,
    "🧀 Nuggets": 20000,
    "🥤 Coca-Cola 0.5L": 10000,
    "🥤 Fanta 0.5L": 10000,
    "🥤 Sprite 0.5L": 10000,
    "🧃 Sharbat": 12000,
    "💧 Suv": 5000,
    "☕ Choy": 4000,
}

CART = {}

# =====================
# WEB SERVER (aiohttp)
# =====================
async def handle_root(request):
    return web.Response(text="EVOS aiogram bot ishlayapti ✅")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 3000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    # Keep running until cancelled
    # We don't return; the site remains running in background
    return runner

# =====================
# KEYBOARDS
# =====================
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Menu"), KeyboardButton(text="🛒 Savat")],
            [KeyboardButton(text="❌ Savatni tozalash")],
            [KeyboardButton(text="ℹ️ Yordam")],
        ],
        resize_keyboard=True,
    )

def menu_keyboard():
    buttons = [[KeyboardButton(text=item)] for item in MENU.keys()]
    buttons.append([KeyboardButton(text="⬅️ Orqaga")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# =====================
# BOT & DISPATCHER
# =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================
# HANDLERS
# =====================
@dp.message(Command("start"))
async def start_handler(message: Message):
    CART[message.from_user.id] = {}
    await message.answer(
        "🍔 EVOS Food Botga xush kelibsiz!\nOvqat yoki ichimlik tanlang 👇",
        reply_markup=main_keyboard(),
    )

@dp.message(Command("menu"))
@dp.message(F.text == "📋 Menu")
async def menu_handler(message: Message):
    await message.answer("📋 Menudan tanlang:", reply_markup=menu_keyboard())

@dp.message(Command("cart"))
@dp.message(F.text == "🛒 Savat")
async def cart_handler(message: Message):
    cart = CART.get(message.from_user.id, {})
    if not cart:
        await message.answer("🧺 Savat bo‘sh")
        return

    text = "🧺 Savatingiz:\n"
    total = 0
    for item, qty in cart.items():
        price = MENU[item]
        text += f"{item} x{qty} = {price * qty} so‘m\n"
        total += price * qty
    text += f"\n💰 Jami: {total} so‘m"
    await message.answer(text)

@dp.message(Command("clear"))
@dp.message(F.text == "❌ Savatni tozalash")
async def clear_handler(message: Message):
    CART[message.from_user.id] = {}
    await message.answer("❌ Savat tozalandi")

@dp.message(Command("help"))
@dp.message(F.text == "ℹ️ Yordam")
async def help_handler(message: Message):
    await message.answer(
        "ℹ️ Buyruqlar:\n"
        "/menu - Menuni ko‘rish\n"
        "/cart - Savat\n"
        "/clear - Savatni tozalash"
    )

@dp.message(F.text == "⬅️ Orqaga")
async def back_handler(message: Message):
    await message.answer("Asosiy menyu", reply_markup=main_keyboard())

@dp.message(F.text.in_(MENU.keys()))
async def add_to_cart(message: Message):
    user_id = message.from_user.id
    item = message.text
    cart = CART.setdefault(user_id, {})
    cart[item] = cart.get(item, 0) + 1
    await message.answer(f"✅ {item} savatga qo‘shildi")

# =====================
# MAIN
# =====================
async def main():
    # start webserver in background
    runner = await start_webserver()

    # start polling
    try:
        await dp.start_polling(bot)
    finally:
        # cleanup web runner on shutdown
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
