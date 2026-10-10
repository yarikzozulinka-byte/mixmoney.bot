import asyncio
import random
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile
)

import database as db

BOT_TOKEN = "8748457473:AAG_iRNJ0ZPtK8hnIXSXNjnsURz_zFECGkI"
ADMIN_ID = 1043109680
ADMIN_USERNAME = "modergosgf"

SPONSORS = [
    "mixmoney_vyplata",
    "chat_mixmoney"
]

PAYOUT_CHANNEL_ID = "@mixmoney_vyplata"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    waiting_for_promo = State()
    waiting_for_withdraw_amount = State()
    waiting_for_withdraw_card = State()
    waiting_for_withdraw_confirm = State()
    waiting_for_task_name = State()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💼 Гаманець"), KeyboardButton(text="📑 Завдання")],
        [KeyboardButton(text="💰 Промокод"), KeyboardButton(text="👤 Партнерка")],
        [KeyboardButton(text="ℹ️ Інфопанель"), KeyboardButton(text="🎯 Квести та Ачивки")]
    ],
    resize_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔝 Повернутись до меню")]],
    resize_keyboard=True
)

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Підтвердити номер телефону", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def get_check_sub_kb():
    buttons = []
    for idx, username in enumerate(SPONSORS, 1):
        buttons.append([InlineKeyboardButton(text=f"📢 Канал {idx}", url=f"https://t.me/{username}")])
    buttons.append([InlineKeyboardButton(text="✅ Я підписався", callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def withdraw_start_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Українська карта")],
            [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="🔝 Повернутись до меню")]
        ],
        resize_keyboard=True
    )

def confirm_withdraw_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_payout"),
                InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_payout")
            ]
        ]
    )

def cabinet_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Вивести гроші (від 50 грн)", callback_data="start_withdraw")],
            [InlineKeyboardButton(text="🏆 Мій рівень та привілегії", callback_data="user_levels_info")]
        ]
    )

def tasks_category_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💵 Легкі завдання (без обмежень)", callback_data="task_cat_0")],
            [InlineKeyboardButton(text="💵 Завдання для 14+", callback_data="task_cat_14")],
            [InlineKeyboardButton(text="💵 Завдання для 18+", callback_data="task_cat_18")]
        ]
    )

def easy_tasks_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ Реєстрація в TaskFree Bot", callback_data="task_easy_taskkfree")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"), InlineKeyboardButton(text="🔝 Головне меню", callback_data="back_to_main")]
        ]
    )

def banks_14_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ Відкрити карту в ПУМБ", callback_data="task_bank_pumb")],
            [InlineKeyboardButton(text="2️⃣ Відкрити карту в Alliance", callback_data="task_bank_alliance")],
            [InlineKeyboardButton(text="3️⃣ Відкрити карту в Abank24", callback_data="task_bank_abank")],
            [InlineKeyboardButton(text="4️⃣ Відкрити карту в Monobank", callback_data="task_bank_mono")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"), InlineKeyboardButton(text="🔝 Головне меню", callback_data="back_to_main")]
        ]
    )

def banks_18_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ Відкрити карту в IZI bank", callback_data="task_bank_izi")],
            [InlineKeyboardButton(text="2️⃣ Відкрити карту в Райффайзен", callback_data="task_bank_raiff")],
            [InlineKeyboardButton(text="3️⃣ Відкрити карту в VST банк", callback_data="task_bank_vst")],
            [InlineKeyboardButton(text="4️⃣ Відкрити карту в Rozetka", callback_data="task_bank_rozetka")],
            [InlineKeyboardButton(text="5️⃣ Зареєструватися в Inzhur REIT", callback_data="task_bank_inzhur")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"), InlineKeyboardButton(text="🔝 Головне меню", callback_data="back_to_main")]
        ]
    )

def task_instruction_kb(cat_code: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data=f"task_cat_{cat_code}"),
                InlineKeyboardButton(text="🔝 Головне меню", callback_data="back_to_main")
            ]
        ]
    )

def info_panel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Канал з виплатами", url=f"https://t.me/{SPONSORS[0]}")],
            [InlineKeyboardButton(text="💬 Чат спілкування", url=f"https://t.me/{SPONSORS[1]}")],
            [InlineKeyboardButton(text="❓ Часті запитання (FAQ)", callback_data="info_faq")],
            [InlineKeyboardButton(text="📜 Правила проекту", callback_data="info_rules")]
        ]
    )

def quests_list_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏆 Квест #1: Активний воркер (+10 грн)", callback_data="quest_view_1")],
            [InlineKeyboardButton(text="🎯 Квест #2: Мастер 18+ (+20 грн)", callback_data="quest_view_2")],
            [InlineKeyboardButton(text="👥 Ачивка: Дружній старт (+5 грн)", callback_data="quest_view_3")]
        ]
    )

def quest_back_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад до квестів", callback_data="quests_list_back")]
        ]
    )

def payout_admin_kb(user_id: int, amount: float):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Зарахувати", callback_data=f"pay_approve_{user_id}_{amount:.2f}"),
                InlineKeyboardButton(text="❌ Відхилити", callback_data=f"pay_reject_{user_id}_{amount:.2f}")
            ]
        ]
    )

async def check_user_subscribed(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True

    valid_statuses = ['creator', 'administrator', 'member']
    for username in SPONSORS:
        try:
            member = await bot.get_chat_member(chat_id=f"@{username}", user_id=user_id)
            if member.status not in valid_statuses:
                return False
        except Exception as e:
            print(f"Помилка перевірки каналу @{username}: {e}")
            return False
    return True

# Функція надсилання сповіщення адміну після повного проходження всіх кроків
async def notify_admin_about_new_user(user_id: int, state: FSMContext):
    data = await state.get_data()
    if data.get("admin_notified"):
        return

    user = await db.get_user(user_id)
    if not user:
        return

    referrer_id = user['referrer_id'] if 'referrer_id' in user.keys() else None
    ref_info = f"за посиланням ID `{referrer_id}`" if referrer_id else "органічно (без реферала)"
    phone = user['phone_number'] if 'phone_number' in user.keys() and user['phone_number'] else "невідомо"

    admin_notify = (
        f"👤 **Новий вхід у бот!**\n\n"
        f"▫️ **Користувач:** {user['full_name']} (@{user['username'] or 'немає'})\n"
        f"▫️ **Телефон:** +{phone}\n"
        f"▫️ **ID:** `{user['user_id']}`\n"
        f"▫️ **Прийшов:** {ref_info}"
    )
    try:
        await bot.send_message(ADMIN_ID, admin_notify, parse_mode="Markdown")
        await state.update_data(admin_notified=True)
    except Exception as e:
        print(f"Помилка надсилання сповіщення адміну: {e}")

@dp.message.outer_middleware()
async def subscription_middleware(handler, event, data):
    if isinstance(event, types.Message):
        if event.chat.type != "private":
            return

        user_id = event.from_user.id
        if event.text and event.text.startswith("/start"):
            return await handler(event, data)
            
        is_sub = await check_user_subscribed(user_id)
        if not is_sub:
            text = (
                "⚠️ **Увага! Доступ обмежено.**\n\n"
                "Щоб користуватися ботом, підпишіться на всі обов'язкові канали нижче та натисніть **«✅ Я підписався»** 👇"
            )
            await event.answer(text, parse_mode="Markdown", reply_markup=get_check_sub_kb())
            return
    return await handler(event, data)

async def publish_daily_promo():
    rewards = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    reward_amount = random.choice(rewards)
    today_str = datetime.now().strftime("%d%m")
    promo_code = f"MIX{today_str}{random.randint(10, 99)}"

    await db.set_daily_promo(promo_code, reward_amount)

    post_text = (
        f"🎁 **Щоденний ранковий промокод MixMoney!**\n\n"
        f"Встигни активувати новий промокод у боті та отримай бонус на свій баланс!\n\n"
        f"🔑 **Промокод:** `{promo_code}`\n"
        f"💰 **Сума бонусу:** **{reward_amount:.2f} грн**\n"
        f"⏳ **Діє до публікації наступного промокоду (24 години)!**\n\n"
        f"🤖 **Активувати у боті:** @{(await bot.get_me()).username}"
    )

    try:
        await bot.send_message(PAYOUT_CHANNEL_ID, post_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Помилка публікації щоденного промокоду: {e}")

async def daily_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 9 and now.minute == 0:
            await publish_daily_promo()
            await asyncio.sleep(60)
        await asyncio.sleep(30)

@dp.message(F.text == "🔝 Повернутись до меню")
@dp.message(F.text == "⬅️ Назад")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ви повернулися до головного меню:", reply_markup=main_kb)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    
    if not user:
        referrer_id = None
        if command.args and command.args.isdigit():
            referrer_id = int(command.args)
        await state.update_data(pending_referrer_id=referrer_id)

        await message.answer(
            "👋 **Ласкаво просимо до MixMoney!**\n\n"
            "🔒 Для захисту від спаму та авто-реєстрацій, будь ласка, підтвердіть ваш український номер телефону.\n\n"
            "Натисніть кнопку нижче 👇",
            parse_mode="Markdown",
            reply_markup=phone_kb
        )
        return

    is_sub = await check_user_subscribed(message.from_user.id)
    if not is_sub:
        welcome_text = (
            "🇺🇦 **Вітаємо у MixMoney!**\n\n"
            "💵 Заробляй легко та без вкладень на актуальних завданнях та рефералах!\n\n"
            "📢 **Для використання бота обов'язково підпишись на наші канали нижче:**"
        )
        if os.path.exists("banner.jpg"):
            photo = FSInputFile("banner.jpg")
            await message.answer_photo(photo=photo, caption=welcome_text, parse_mode="Markdown", reply_markup=get_check_sub_kb())
        else:
            await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_check_sub_kb())
        return

    await notify_admin_about_new_user(message.from_user.id, state)
    await message.answer("Ласкаво просимо до MixMoney! Оберіть розділ в меню нижче:", reply_markup=main_kb)

@dp.message(F.contact)
async def process_phone_verification(message: types.Message, state: FSMContext):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer("❌ Будь ласка, надішліть свій власний контакт за допомогою кнопки нижче!", reply_markup=phone_kb)
        return

    phone = contact.phone_number.replace("+", "")
    if not phone.startswith("380"):
        await message.answer(
            "❌ **Реєстрація обмежена!**\n\n"
            "Бот доступний тільки для користувачів з українськими номерами телефонів (+380).",
            parse_mode="Markdown"
        )
        return

    data = await state.get_data()
    referrer_id = data.get("pending_referrer_id")

    await db.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name,
        phone_number=phone,
        referrer_id=referrer_id
    )

    is_sub = await check_user_subscribed(message.from_user.id)
    if not is_sub:
        await message.answer(
            "✅ **Номер телефону успішно підтверджено!**\n\n"
            "📢 **Останній крок:** Підпишіться на наші обов'язкові канали нижче, щоб відкрити доступ до бота та отримати вітальний бонус:",
            parse_mode="Markdown",
            reply_markup=get_check_sub_kb()
        )
        return

    await notify_admin_about_new_user(message.from_user.id, state)
    await message.answer(
        "✅ **Номер телефону успішно підтверджено!**\n\n"
        "Вам нараховано вітальний бонус **6.00 грн** на баланс! 🎉",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

@dp.callback_query(F.data == "check_subscription")
async def process_check_subscription(callback: types.CallbackQuery, state: FSMContext):
    is_sub = await check_user_subscribed(callback.from_user.id)
    if is_sub:
        try:
            await callback.message.delete()
        except Exception:
            pass

        await notify_admin_about_new_user(callback.from_user.id, state)

        await callback.message.answer(
            "✅ **Дякуємо за підписку! Доступ повністю відкрито.**\n\nОберіть потрібний розділ в меню нижче 👇", 
            parse_mode="Markdown", 
            reply_markup=main_kb
        )
    else:
        await callback.answer("❌ Ви ще не підписалися на всі обов'язкові канали!", show_alert=True)

@dp.message(F.text == "💼 Гаманець")
async def show_cabinet(message: types.Message, state: FSMContext):
    await state.clear()
    
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("👋 Введіть команду /start для проходження авторизації.")
        return

    total_bot_users = await db.get_total_users_count()

    level_badges = {
        "Новачок": "🥉 Новачок",
        "Партнер": "🥈 Партнер (+10%)",
        "PRO-воркер": "🥇 PRO-воркер"
    }
    badge = level_badges.get(user['level'], "🥉 Новачок")

    text = (
        f"💼 **Ваш Гаманець:** {user['full_name']}\n\n"
        f"🆔 **Ваш ID:** `{user['user_id']}`\n\n"
        f"🏆 **Ваш рівень:** {badge}\n\n"
        f"📊 **Статистика бота:**\n"
        f"🌐 **Усього користувачів у боті:** {total_bot_users} чол.\n"
        f"👤 **Ваших рефералів:** {user['total_referrals']} чол.\n\n"
        f"💰 **Деталізація прибутку:**\n"
        f"🏦 **На завданнях:** {user['earned_tasks']:.2f} грн\n"
        f"👥 **На рефералах:** {user['earned_refs']:.2f} грн\n\n"
        f"💵 **Ваш баланс:** {user['balance']:.2f} грн"
    )

    await message.answer(text, parse_mode="Markdown", reply_markup=cabinet_inline_kb())

@dp.callback_query(F.data == "user_levels_info")
async def process_levels_info(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Будь ласка, запустіть /start", show_alert=True)
        return

    level_badges = {
        "Новачок": "🥉 Новачок",
        "Партнер": "🥈 Партнер",
        "PRO-воркер": "🥇 PRO-воркер"
    }
    badge = level_badges.get(user['level'], "🥉 Новачок")

    text = (
        f"🏆 **Система рівнів MixMoney**\n\n"
        f"Ваш поточний статус: **{badge}**\n"
        f"Виконано підтверджених завдань: **{user['completed_tasks_count']}**\n\n"
        f"🥉 **Новачок** *(0–3 виконаних завдань)*\n"
        f"🥈 **Партнер** *(4–8 виконаних завдань — +10% до виплати)*\n"
        f"🥇 **PRO-воркер** *(від 9+ виконаних завдань — пріоритетні виплати)*"
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "start_withdraw")
async def start_withdraw_process(callback: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Сталася помилка. Введіть /start", show_alert=True)
        return

    if user['balance'] < 50:
        await callback.answer("❌ Мінімальна сума для виведення — 50 грн!", show_alert=True)
        return

    approved_count = await db.get_approved_tasks_count(callback.from_user.id)

    if approved_count < 1:
        no_tasks_msg = (
            "⚠️ **Виведення коштів недоступне!**\n\n"
            "Для активації першої виплати необхідно виконати "
            "принаймні **одне завдання у розділі 14+ або 18+**.\n\n"
            "Після підтвердження завдання ви зможете створити заявку! 🚀"
        )
        await callback.message.answer(no_tasks_msg, parse_mode="Markdown")
        await callback.answer()
        return

    await callback.message.answer("Оберіть спосіб отримання виплати:", reply_markup=withdraw_start_kb())
    await callback.answer()

@dp.message(F.text == "💳 Українська карта")
async def withdraw_select_card(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user or user['balance'] < 50:
        await message.answer("❌ Мінімальна сума для виплати — 50 грн!", reply_markup=main_kb)
        return

    await state.set_state(Form.waiting_for_withdraw_amount)
    text = (
        f"❗️ **Мінімальна сума для виплати — 50 грн**\n\n"
        f"💸 **Скільки ви хочете вивести?**\n"
        f"ℹ️ **У вас — {user['balance']:.2f} грн**"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=cancel_kb)

@dp.message(Form.waiting_for_withdraw_amount)
async def withdraw_process_amount(message: types.Message, state: FSMContext):
    if message.text in ["🔝 Повернутись до меню", "⬅️ Назад"]:
        await cancel_handler(message, state)
        return

    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Будь ласка, введіть суму числом (наприклад: 80):")
        return

    user = await db.get_user(message.from_user.id)
    if amount < 50:
        await message.answer("❌ Мінімальна сума для виплати — 50 грн!")
        return
    if amount > user['balance']:
        await message.answer(f"❌ Недостатньо коштів. Ваш баланс: {user['balance']:.2f} грн")
        return

    # Захист від мінусу: якщо сума >= 80 грн, потрібно мінімум 2 завдання
    if amount >= 80.0:
        approved_count = await db.get_approved_tasks_count(message.from_user.id)
        if approved_count < 2:
            await message.answer(
                f"⚠️ **Виведення від 80 грн недоступне!**\n\n"
                f"Для виведення сум від 80 грн необхідно мати виконано мінімум **2 завдання** (у вас підтверджено: {approved_count}).\n\n"
                f"Виконайте ще одне завдання в розділі 14+ або 18+, або виведіть меншу суму (до 79.99 грн), для якої достатньо 1 завдання.",
                reply_markup=main_kb
            )
            await state.clear()
            return

    await state.update_data(withdraw_amount=amount)
    await state.set_state(Form.waiting_for_withdraw_card)
    
    text = (
        "✍️ **Введіть реквізити вашої картки, щоб отримати виплату.**\n\n"
        "✅ **Переконайтеся, що дані вказані правильно.**"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=cancel_kb)

@dp.message(Form.waiting_for_withdraw_card)
async def withdraw_process_card(message: types.Message, state: FSMContext):
    if message.text in ["🔝 Повернутись до меню", "⬅️ Назад"]:
        await cancel_handler(message, state)
        return

    card_number = message.text.strip()
    await state.update_data(withdraw_card=card_number)
    await state.set_state(Form.waiting_for_withdraw_confirm)

    text = (
        f"❗️ **Перевірте правильність введених реквізитів 👇**\n\n"
        f"`{card_number}`\n\n"
        f"✅ **Усе правильно?**"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=confirm_withdraw_kb())

@dp.callback_query(Form.waiting_for_withdraw_confirm, F.data == "confirm_payout")
async def withdraw_confirm_final(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data.get("withdraw_amount")
    card = data.get("withdraw_card")

    user = await db.get_user(callback.from_user.id)
    if user['balance'] < amount:
        await callback.message.answer("❌ Недостатньо коштів на балансі.", reply_markup=main_kb)
        await state.clear()
        return

    await db.add_balance(callback.from_user.id, -amount, category="other")

    user_name = callback.from_user.full_name
    username = f"@{callback.from_user.username}" if callback.from_user.username else "немає"

    admin_msg = (
        f"📩 **НОВА ЗАЯВКА НА ВИПЛАТУ!**\n\n"
        f"👤 **Користувач:** {user_name} ({username})\n"
        f"🆔 **ID:** `{callback.from_user.id}`\n"
        f"💰 **Сума:** {amount:.2f} грн\n"
        f"💳 **Картка:** `{card}`"
    )
    
    await bot.send_message(
        ADMIN_ID, 
        admin_msg, 
        parse_mode="Markdown", 
        reply_markup=payout_admin_kb(callback.from_user.id, amount)
    )
    await callback.message.answer("✅ **Заявку успішно створено! Очікуйте на зарахування коштів.**", parse_mode="Markdown", reply_markup=main_kb)
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data.startswith("pay_approve_"))
async def process_payout_approve_by_admin(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    parts = callback.data.split("_")
    target_user_id = int(parts[2])
    amount = float(parts[3])

    target_user = await db.get_user(target_user_id)
    user_name = target_user['full_name'] if target_user else "Користувач"
    username_str = f" (@{target_user['username']})" if target_user and target_user['username'] else ""

    try:
        await bot.send_message(target_user_id, f"🎉 **Вашу виплату на суму {amount:.2f} грн успішно здійснено!**", parse_mode="Markdown")
    except Exception as e:
        print(f"Помилка надсилання сповіщення користувачу: {e}")

    channel_msg = (
        f"💸 **Виплату успішно здійснено!**\n\n"
        f"👤 **Користувач:** {user_name}{username_str}\n"
        f"💰 **Сума:** **{amount:.2f} грн**\n\n"
        f"✅ Дякуємо, що працюєте з MixMoney!"
    )
    try:
        await bot.send_message(PAYOUT_CHANNEL_ID, channel_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Помилка публікації виплати у канал: {e}")

    await callback.message.edit_text(callback.message.text + "\n\n✅ **ВИПЛАТУ ЗАРАХОВАНО ТА ОПУБЛІКОВАНО!**", parse_mode="Markdown")
    await callback.answer("Виплату підтверджено!")

@dp.callback_query(F.data.startswith("pay_reject_"))
async def process_payout_reject_by_admin(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    parts = callback.data.split("_")
    target_user_id = int(parts[2])
    amount = float(parts[3])

    await db.add_balance(target_user_id, amount, category="other")

    reject_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написати модерації", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
    )

    reject_text = (
        f"❌ **Вашу заявку на виплату ({amount:.2f} грн) відхилено!**\n\n"
        f"⚠️ **Будь ласка, перевірте, чи ви повністю виконали всі умови завдань.**\n\n"
        f"💰 Гроші повернуто на ваш баланс.\n\n"
        f"❓ Якщо у вас є питання або вам потрібна допомога, ви можете звернутися до нашої модерації:"
    )

    try:
        await bot.send_message(target_user_id, reject_text, parse_mode="Markdown", reply_markup=reject_kb)
    except Exception as e:
        print(f"Помилка надсилання відхилення: {e}")

    await callback.message.edit_text(callback.message.text + "\n\n❌ **ЗАЯВКУ ВІДХИЛЕНО (кошти повернуто користувачу)**", parse_mode="Markdown")
    await callback.answer("Заявку відхилено!")

@dp.callback_query(Form.waiting_for_withdraw_confirm, F.data == "cancel_payout")
async def withdraw_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Виведення скасовано. Ви повернулися в меню.", reply_markup=main_kb)
    await callback.answer()

@dp.message(F.text == "📑 Завдання")
async def show_tasks(message: types.Message, state: FSMContext):
    await state.clear()
    first_name = message.from_user.first_name
    text = (
        f"❗ **{first_name}**, тут зібрані завдання з різними віковими обмеженнями.\n\n"
        f"✅ **Обирай категорію під свій вік та починай виконувати:**"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=tasks_category_kb())

@dp.callback_query(F.data == "back_to_categories")
async def process_back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    first_name = callback.from_user.first_name
    text = (
        f"❗ **{first_name}**, тут зібрані завдання з різними віковими обмеженнями.\n\n"
        f"✅ **Обирай категорію під свій вік та починай виконувати:**"
    )
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=tasks_category_kb())
    except Exception:
        pass
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Ви повернулися до головного меню:", reply_markup=main_kb)
    await callback.answer()

@dp.callback_query(F.data.startswith("task_cat_"))
async def process_task_category(callback: types.CallbackQuery):
    cat = callback.data.split("_")[2]
    
    if cat == "0":
        await callback.message.edit_text("💵 **Легкі завдання (без обмежень)**\n\nОберіть доступне завдання:", parse_mode="Markdown", reply_markup=easy_tasks_kb())
    elif cat == "14":
        await callback.message.edit_text("💵 **Завдання для 14+**\n\nОберіть банк для виконання завдання:", parse_mode="Markdown", reply_markup=banks_14_kb())
    elif cat == "18":
        await callback.message.edit_text("💵 **Завдання для 18+**\n\nОберіть фонд/банк для виконання завдання:", parse_mode="Markdown", reply_markup=banks_18_kb())
    else:
        await callback.message.answer("📌 Наразі доступні завдання оновлюються.", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("task_easy_"))
async def process_easy_task(callback: types.CallbackQuery, state: FSMContext):
    task_code = callback.data.split("_")[2]
    
    easy_info = {
        "taskkfree": {
            "title": "TaskFree Bot", "cat": "0", "reward": 4.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 4 грн**\n\n"
                "⚠️ **Завдання доступне лише для користувачів, які ще не проходили реєстрацію в цьому боті.**\n\n"
                "**Інструкція 👇**\n"
                "1️⃣ Переходимо за посиланням 👇\n"
                "[👉 Натисни сюди для переходу](https://t.me/taskkfree_bot?start=ref_W9KYBGRJ)\n\n"
                "2️⃣ Проходимо легку реєстрацію до кінця і все.\n\n"
                "❗ **Звіт:** після того, як ви завершили реєстрацію, відправте `+` у відповіді на це завдання."
            )
        }
    }

    info = easy_info.get(task_code)
    if info:
        await state.update_data(current_bank=info["title"], reward=info["reward"])
        await state.set_state(Form.waiting_for_task_name)
        await callback.message.answer(
            info["text"], 
            parse_mode="Markdown", 
            reply_markup=task_instruction_kb(info["cat"]), 
            disable_web_page_preview=True
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("task_bank_"))
async def process_bank_task(callback: types.CallbackQuery, state: FSMContext):
    bank = callback.data.split("_")[2]
    
    banks_info = {
        "pumb": {
            "title": "ПУМБ", "cat": "14", "reward": 30.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 130 грн**\n\n"
                "**+100 грн від банку**\n**+30 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Перейди за посиланням і скачай додаток 👇\nhttps://pumb.onelink.me/Jrxy/42hsg69v\n\n"
                "2️⃣ Пройди реєстрацію та верифікацію\n3️⃣ Зроби першу покупку від 100 грн\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "alliance": {
            "title": "Alliance Bank", "cat": "14", "reward": 30.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 230 грн**\n\n"
                "**+200 грн від банку**\n**+30 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Перейди за посиланням 👇\nhttps://alb.ua/r/LG-EOwA\n\n"
                "2️⃣ Відкрий карту «Стартова» через ДІЮ\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "abank": {
            "title": "Абанк (Abank24)", "cat": "14", "reward": 30.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 130 грн**\n\n"
                "**+100 грн від банку**\n**+30 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Перейди за посиланням 👇\nhttps://link.a-bank.com.ua/UfHo5Vb7\n\n"
                "2️⃣ Відкрий карту\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "mono": {
            "title": "Monobank", "cat": "14", "reward": 30.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 80 грн**\n\n"
                "**+50 грн від банку**\n**+30 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Перейди за посиланням 👇\nhttps://monobank.ua/r/PecesV\n\n"
                "2️⃣ Відкрий карту\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "izi": {
            "title": "IZI bank", "cat": "18", "reward": 25.0,
            "text": (
                "💰 **Винагорода за виконане завдання: до 175 грн**\n\n"
                "**до 150 грн від банку**\n**+25 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Скачай додаток за посиланням 👇\nhttps://izibank.com.ua/r/4uYi\n\n"
                "2️⃣ Активуй картку\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "raiff": {
            "title": "Raiffeisen Bank", "cat": "18", "reward": 60.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 260 грн**\n\n"
                "**+200 грн від банку**\n**+60 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Перейди за посиланням 👇\nhttps://mrf-static.apps.raiffeisen.ua/v1/member-get-member?adj_t=1s492itc_1szn7s6p&ref_id=12744027\n\n"
                "2️⃣ Відкрий «Райфкартку»\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "vst": {
            "title": "VST банк", "cat": "18", "reward": 30.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 130 грн**\n\n"
                "**+100 грн від банку**\n**+30 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Скачай за посиланням 👇\nhttps://bv.onelink.me/clX0/o7yoy274KE\n\n"
                "2️⃣ Оплати товар картою від 2 грн\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "rozetka": {
            "title": "Rozetka Card", "cat": "18", "reward": 35.0,
            "text": (
                "💰 **Винагорода за виконане завдання: 235 грн**\n\n"
                "**+200 грн від Rozetka**\n**+35 грн від нас**\n\n"
                "**Інструкція 👇**\n1️⃣ Перейди за посиланням 👇\nhttps://rozetka.com.ua/ua/rozetka-card/main?code=vDcDA5zQ\n\n"
                "2️⃣ Відкрий картку\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я** у відповідь на це завдання."
            )
        },
        "inzhur": {
            "title": "Inzhur REIT", "cat": "18", "reward": 50.0,
            "text": (
                "💰 **Винагорода за виконання: 280 грн**\n\n"
                "**+20 подарункових сертифікатів від фонду (конвертуються у 230 грн)**\n"
                "**+50 грн від нас**\n\n"
                "**Інструкція 👇**\n"
                "1️⃣ Перейди за посиланням та зареєструйся 👇\n"
                "https://www.inzhur.reit/r/vlce-3qlOvqfQZuhkSwGH\n\n"
                "2️⃣ Пройди швидку верифікацію (через Дію або BankID) та отримай 20 сертифікатів\n\n"
                "❗ **Звіт:** надішліть **скріншот та ваше ім'я і прізвище** у відповідь на це завдання."
            )
        }
    }

    info = banks_info.get(bank)
    if info:
        await state.update_data(current_bank=info["title"], reward=info["reward"])
        await state.set_state(Form.waiting_for_task_name)
        await callback.message.answer(
            info["text"], 
            parse_mode="Markdown", 
            reply_markup=task_instruction_kb(info["cat"]), 
            disable_web_page_preview=True
        )
    await callback.answer()

@dp.message(Form.waiting_for_task_name)
async def process_task_report(message: types.Message, state: FSMContext):
    if message.text in ["🔝 Повернутись до меню", "⬅️ Назад"]:
        await cancel_handler(message, state)
        return

    data = await state.get_data()
    bank_title = data.get("current_bank", "Завдання")
    reward_amount = data.get("reward", 50.0)
    
    if message.photo:
        user_report = f"[Скріншот] {message.caption or 'Без підпису'}"
    else:
        user_report = message.text.strip()

    report_id = await db.create_report(
        user_id=message.from_user.id,
        bank_name=bank_title,
        user_reported_name=user_report,
        reward=reward_amount
    )

    admin_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"✅ Схвалити (+{reward_amount:.0f} грн)", callback_data=f"approve_{report_id}"),
                InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{report_id}")
            ]
        ]
    )

    admin_msg = (
        f"📥 **НОВИЙ ЗВІТ ПО ЗАВДАННЮ!**\n\n"
        f"👤 **Користувач:** {message.from_user.full_name} (@{message.from_user.username})\n"
        f"🆔 **ID:** `{message.from_user.id}`\n"
        f"🏦 **Завдання:** {bank_title} ({reward_amount:.0f} грн)\n"
        f"✍️ **Звіт:** *{user_report}*"
    )
    
    await bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown", reply_markup=admin_kb)
    await message.answer("✅ **Дякуємо! Звіт успішно прийнято в обробку.**", parse_mode="Markdown", reply_markup=main_kb)
    await state.clear()

@dp.callback_query(F.data.startswith("approve_"))
async def approve_report(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    report_id = int(callback.data.split("_")[1])
    async with db.aiosqlite.connect(db.DB_NAME) as connection:
        connection.row_factory = db.aiosqlite.Row
        async with connection.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,)) as cursor:
            report = await cursor.fetchone()

    if report and report['status'] == 'pending':
        user = await db.get_user(report['user_id'])
        final_reward = report['reward']
        if user and user['level'] == 'Партнер':
            final_reward *= 1.10

        await db.add_balance(report['user_id'], final_reward, category="tasks")
        await db.increment_completed_tasks(report['user_id'])
        await db.update_report_status(report_id, 'approved')
        
        updated_user = await db.get_user(report['user_id'])
        count = updated_user['completed_tasks_count']
        old_level = updated_user['level']
        new_level = old_level

        if count >= 3 and updated_user['quest_claimed'] == 0:
            await db.add_balance(report['user_id'], 10.0, category="other")
            await db.mark_quest_claimed(report['user_id'])
            await bot.send_message(report['user_id'], "🎉 **Виконано квест #1! Бонус +10.00 грн зараховано!**", parse_mode="Markdown")

        count_18 = await db.get_completed_18_tasks_count(report['user_id'])
        if count_18 >= 4 and updated_user['quest_18_claimed'] == 0:
            await db.add_balance(report['user_id'], 20.0, category="other")
            await db.mark_quest_18_claimed(report['user_id'])
            await bot.send_message(report['user_id'], "🎉 **Виконано квест #2 (18+)! Бонус +20.00 грн зараховано!**", parse_mode="Markdown")

        if count >= 9 and old_level != "PRO-воркер":
            new_level = "PRO-воркер"
        elif count >= 4 and count < 9 and old_level == "Новачок":
            new_level = "Партнер"

        if new_level != old_level:
            await db.update_user_level(report['user_id'], new_level)
            await bot.send_message(report['user_id'], f"🎉 **Твій рівень підвищено до статусу {new_level}!**", parse_mode="Markdown")

        await callback.message.edit_text(callback.message.text + "\n\n✅ **СХВАЛЕНО**", parse_mode="Markdown")
        await bot.send_message(report['user_id'], f"🎉 Звіт схвалено! +{final_reward:.2f} грн зараховано.", parse_mode="Markdown")
    await callback.answer("Звіт схвалено!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_report(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    report_id = int(callback.data.split("_")[1])
    async with db.aiosqlite.connect(db.DB_NAME) as connection:
        connection.row_factory = db.aiosqlite.Row
        async with connection.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,)) as cursor:
            report = await cursor.fetchone()

    if report and report['status'] == 'pending':
        await db.update_report_status(report_id, 'rejected')
        await callback.message.edit_text(callback.message.text + "\n\n❌ **ВІДХИЛЕНО**", parse_mode="Markdown")
        await bot.send_message(report['user_id'], f"❌ Ваш звіт по завданню **{report['bank_name']}** відхилено.", parse_mode="Markdown")
    await callback.answer("Звіт відхилено!")

@dp.message(F.text == "🎯 Квести та Ачивки")
async def show_quests_list(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        f"🎯 **Квести та Ачивки MixMoney**\n\n"
        f"Виконуй особливі завдання та отримуй додаткові бонуси!\n\n"
        f"Обери квест зі списку нижче 👇"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=quests_list_kb())

@dp.callback_query(F.data == "quests_list_back")
async def process_quests_list_back(callback: types.CallbackQuery):
    text = (
        f"🎯 **Квести та Ачивки MixMoney**\n\n"
        f"Виконуй особливі завдання та отримуй додаткові бонуси!\n\n"
        f"Обери квест зі списку нижче 👇"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=quests_list_kb())
    await callback.answer()

@dp.callback_query(F.data == "quest_view_1")
async def process_quest_1(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    count = user['completed_tasks_count'] if user else 0
    claimed = user['quest_claimed'] if user else 0
    status = "✅ **Виконано!**" if claimed == 1 or count >= 3 else f"⏳ **Прогрес:** {count}/3 виконано"

    text = (
        f"🏆 **Квест #1: Активний воркер**\n\n"
        f"📌 **Умови:** Виконати 3 будь-які завдання.\n"
        f"🎁 **Винагорода:** **+10.00 грн**\n\n"
        f"📊 **Статус:**\n{status}"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=quest_back_kb())
    await callback.answer()

@dp.callback_query(F.data == "quest_view_2")
async def process_quest_2(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    count_18 = await db.get_completed_18_tasks_count(callback.from_user.id)
    claimed_2 = user['quest_18_claimed'] if user else 0
    status = "✅ **Виконано!**" if claimed_2 == 1 or count_18 >= 4 else f"⏳ **Прогрес:** {count_18}/4 виконано (18+)"

    text = (
        f"🎯 **Квест #2: Мастер 18+**\n\n"
        f"📌 **Умови:** Виконати всі 4 завдання з розділу 18+.\n"
        f"🎁 **Винагорода:** **+20.00 грн**\n\n"
        f"📊 **Статус:**\n{status}"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=quest_back_kb())
    await callback.answer()

@dp.callback_query(F.data == "quest_view_3")
async def process_quest_3(callback: types.CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    refs_count = user['total_referrals'] if user else 0
    claimed_ref5 = user['quest_ref5_claimed'] if user else 0

    if refs_count >= 5 and claimed_ref5 == 0:
        await db.add_balance(callback.from_user.id, 5.0, category="other")
        await db.mark_quest_ref5_claimed(callback.from_user.id)
        claimed_ref5 = 1

    status = "✅ **Виконано та отримано!**" if claimed_ref5 == 1 else f"⏳ **Прогрес:** {refs_count}/5 друзів"

    text = (
        f"👥 **Ачивка: Дружній старт**\n\n"
        f"📌 **Умови:** Запросити 5 друзів за своїм реферальним посиланням.\n"
        f"🎁 **Винагорода:** **+5.00 грн**\n\n"
        f"📊 **Статус:**\n{status}"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=quest_back_kb())
    await callback.answer()

@dp.message(F.text == "👤 Партнерка")
async def show_ref_link(message: types.Message, state: FSMContext):
    await state.clear()
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    
    text = (
        f"🤝 **Партнерська програма MixMoney**\n\n"
        f"Запрошуй друзів та заробляйте разом!\n\n"
        f"💰 **Вигода для обох:**\n"
        f"▫️ **Тобі:** **7.00 грн** за кожного запрошеного друга.\n"
        f"▫️ **Другу:** **6.00 грн** вітального бонусу на баланс!\n\n"
        f"🔗 **Твоє реферальне посилання:**\n{ref_link}"
    )
    share_url = f"https://t.me/share/url?url={ref_link}"
    share_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Поділитися", url=share_url)]])
    await message.answer(text, parse_mode="Markdown", reply_markup=share_kb)

@dp.message(F.text == "ℹ️ Інфопанель")
async def show_info(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        f"ℹ️ **Інформаційна панель MixMoney**\n\n"
        f"Ласкаво просимо до офіційного інформаційного центру нашого проєкту! Тут зібрані всі ключові посилання, правила та відповіді на найпоширеніші запитання.\n\n"
        f"📌 Скористайтеся кнопками нижче для навігації:"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=info_panel_kb())

@dp.callback_query(F.data == "info_faq")
async def process_info_faq(callback: types.CallbackQuery):
    text = (
        f"❓ **Часті запитання (FAQ):**\n\n"
        f"🔹 **1. Як швидко зараховується винагорода за завдання?**\n"
        f"Після виконання умов та надсилання вашого звіту адміністратор перевіряє заявку. Зазвичай перевірка триває від 15 хвилин до кількох годин.\n\n"
        f"🔹 **2. Коли надходять гроші за рефералів?**\n"
        f"Бонус за запрошеного друга (+7 грн вам та +6 грн другу) нараховується **миттєво** після успішного підтвердження українського номера телефону за вашим посиланням.\n\n"
        f"🔹 **3. Який мінімальний поріг та термін виплат?**\n"
        f"Мінімальна сума для виведення складає **50 грн** (для виплат до 79.99 грн потрібно виконати 1 завдання, для сум від 80 грн і більше — мінімум 2 підтверджені завдання).\n\n"
        f"🔹 **4. Що робити, якщо виникають проблеми з реєстрацією?**\n"
        f"Обов'язково переконуйтеся, що ви реєструєтеся за нашими прямими реферальними посиланнями."
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "info_rules")
async def process_info_rules(callback: types.CallbackQuery):
    text = (
        f"📜 **Правила користування проєктом MixMoney:**\n\n"
        f"1️⃣ **Чесність та реферальна система:**\n"
        f"Суворо заборонено використовувати системні накрутки, сайти активної реклами (букси), спам та створювати мультиакаунти (реєструватися за власним посиланням). У разі виявлення накрутки баланс анулюється, а акаунт блокується назавжди без права виведення коштів.\n\n"
        f"2️⃣ **Звіти та перевірка завдань:**\n"
        f"Усі звіти перевіряються вручну адміністраторами. Заборонено надсилати неправдиві дані. Якщо дані не збігаються з реальною реєстрацією — звіт буде відхилено.\n\n"
        f"3️⃣ **Фінансові правила та виплати:**\n"
        f"Заявки на виплату створюються через розділ Гаманець (від 50 грн). Для великих виплат (від 80 грн) діє вимога мінімум 2 виконаних завдань.\n\n"
        f"4️⃣ **Дотримання умов:**\n"
        f"Користуючись ботом, ви автоматично погоджуєтеся з цими правилами."
    )
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text == "💰 Промокод")
async def ask_promo(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_promo)
    await message.answer("Введіть секретний промокод:", reply_markup=cancel_kb)

@dp.message(Form.waiting_for_promo)
async def process_promo(message: types.Message, state: FSMContext):
    if message.text in ["🔝 Повернутись до меню", "⬅️ Назад"]:
        await cancel_handler(message, state)
        return
    code = message.text.strip()
    success, msg = await db.use_promo_code(message.from_user.id, code)
    await message.answer(msg, parse_mode="Markdown", reply_markup=main_kb)
    await state.clear()

async def main():
    await db.init_db()
    asyncio.create_task(daily_scheduler())
    print("Бот MixMoney успішно запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
