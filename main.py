import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from aiohttp import web

BOT_TOKEN = "8748457473:AAG_iRNJ0ZPtK8hnIXSXNjnsURz_zFECGkI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Веб-сервер для бесплатного тарифа Render ---
async def handle(request):
    return web.Response(text="MixMoney Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --- Стартовое меню и логика бота ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username)
    await message.answer("Привіт! Вітаю у MixMoney боті 💸")

@dp.callback_query(F.data == "withdraw")
async def process_withdraw(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if user['balance'] < 50:
        await callback.answer("❌ Мінімальна сума для виведення – 50 грн!", show_alert=True)
    else:
        await callback.message.answer("Введіть реквізити для виведення коштів:")
        await callback.answer()

@dp.callback_query(F.data == "roulette")
async def process_roulette(callback: types.CallbackQuery):
    await callback.answer("🎰 Модуль рулетки в розробці!", show_alert=True)

# --- Запуск бота ---
async def main():
    await db.init_db()
    asyncio.create_task(web_server())
    print("Бот MixMoney успішно запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
