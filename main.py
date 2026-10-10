import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

import database as db

# Твой токен от MixMoney
BOT_TOKEN = "8748457473:AAG_iRNJ0ZPtK8hnIXSXNjnsURz_zFECGkI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔑 Кабінет")],
        [KeyboardButton(text="📑 Завдання"), KeyboardButton(text="💰 Промокод"), KeyboardButton(text="👤 Партнерка")],
        [KeyboardButton(text="ℹ️ Інформаційна панель"), KeyboardButton(text="📜 Правила")],
        [KeyboardButton(text="➡️ ІНШІ ТГ БОТИ, ЯКІ ПЛАТЯТЬ!")]
    ],
    resize_keyboard=True
)

# Кнопки под Кабинетом
def cabinet_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Вивести гроші від 50 грн", callback_data="withdraw")],
            [InlineKeyboardButton(text="🎰 Рулетка ( 10-100 грн )", callback_data="roulette")]
        ]
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    referrer_id = None
    if command.args and command.args.isdigit():
        referrer_id = int(command.args)

    await db.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name,
        referrer_id=referrer_id
    )

    await message.answer("Ласкаво просимо до MixMoney! Оберіть розділ в меню нижче:", reply_markup=main_kb)

@dp.message(F.text == "🔑 Кабінет")
async def show_cabinet(message: types.Message):
    user = await db.get_user(message.from_user.id)

    text = (
        f"👤 **Ім'я:** {user['full_name']}\n\n"
        f"🆔 **ID:** `{user['user_id']}` ( натисни для копіювання )\n\n"
        f"✅ **Верифіковано по твоєму посиланню:**\n"
        f"• Загалом: {user['total_referrals']}\n"
        f"• Сьогодні: {user['today_referrals']}\n\n"
        f"💳 **Зароблено коштів:** {user['balance']:.0f} грн"
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=cabinet_inline_kb())

@dp.message(F.text == "👤 Партнерка")
async def show_ref_link(message: types.Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    
    text = (
        f"🤝 **Партнерська програма MixMoney**\n\n"
        f"Запрошуй друзів та отримуй бонуси на баланс!\n\n"
        f"🔗 Твоє реферальне посилання:\n`{ref_link}`"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.callback_query(F.data == "withdraw")
async def process_withdraw(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if user['balance'] < 50:
        await callback.answer("❌ Мінімальна сума для виведення — 50 грн!", show_alert=True)
    else:
        await callback.message.answer("Введіть реквізити для виведення коштів:")
        await callback.answer()

@dp.callback_query(F.data == "roulette")
async def process_roulette(callback: types.CallbackQuery):
    await callback.answer("🎰 Модуль рулетки в розробці!", show_alert=True)

async def main():
    await db.init_db()
    print("Бот MixMoney успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

import database as db

# Твой токен от MixMoney
BOT_TOKEN = "8748457473:AAG_iRNJ0ZPtK8hnIXSXNjnsURz_zFECGkI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔑 Кабінет")],
        [KeyboardButton(text="📑 Завдання"), KeyboardButton(text="💰 Промокод"), KeyboardButton(text="👤 Партнерка")],
        [KeyboardButton(text="ℹ️ Інформаційна панель"), KeyboardButton(text="📜 Правила")],
        [KeyboardButton(text="➡️ ІНШІ ТГ БОТИ, ЯКІ ПЛАТЯТЬ!")]
    ],
    resize_keyboard=True
)

# Кнопки под Кабинетом
def cabinet_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Вивести гроші від 50 грн", callback_data="withdraw")],
            [InlineKeyboardButton(text="🎰 Рулетка ( 10-100 грн )", callback_data="roulette")]
        ]
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    referrer_id = None
    if command.args and command.args.isdigit():
        referrer_id = int(command.args)

    await db.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name,
        referrer_id=referrer_id
    )

    await message.answer("Ласкаво просимо до MixMoney! Оберіть розділ в меню нижче:", reply_markup=main_kb)

@dp.message(F.text == "🔑 Кабінет")
async def show_cabinet(message: types.Message):
    user = await db.get_user(message.from_user.id)

    text = (
        f"👤 **Ім'я:** {user['full_name']}\n\n"
        f"🆔 **ID:** `{user['user_id']}` ( натисни для копіювання )\n\n"
        f"✅ **Верифіковано по твоєму посиланню:**\n"
        f"• Загалом: {user['total_referrals']}\n"
        f"• Сьогодні: {user['today_referrals']}\n\n"
        f"💳 **Зароблено коштів:** {user['balance']:.0f} грн"
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=cabinet_inline_kb())

@dp.message(F.text == "👤 Партнерка")
async def show_ref_link(message: types.Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    
    text = (
        f"🤝 **Партнерська програма MixMoney**\n\n"
        f"Запрошуй друзів та отримуй бонуси на баланс!\n\n"
        f"🔗 Твоє реферальне посилання:\n`{ref_link}`"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.callback_query(F.data == "withdraw")
async def process_withdraw(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if user['balance'] < 50:
        await callback.answer("❌ Мінімальна сума для виведення — 50 грн!", show_alert=True)
    else:
        await callback.message.answer("Введіть реквізити для виведення коштів:")
        await callback.answer()

@dp.callback_query(F.data == "roulette")
async def process_roulette(callback: types.CallbackQuery):
    await callback.answer("🎰 Модуль рулетки в розробці!", show_alert=True)

async def handle(request):
    from aiohttp import web
    return web.Response(text="MixMoney Bot is running!")

async def web_server():
    from aiohttp import web
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await db.init_db()
    asyncio.create_task(web_server())
    print("Бот MixMoney успішно запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
