# bot/handlers/admin.py

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from config import ADMIN_IDS, config
from database.db import db
from utils.navigation import edit_menu

logger = logging.getLogger(__name__)
router = Router()


# ===== ADMIN FSM STATES =====
class AdminStates(StatesGroup):
    """States for admin panel"""
    admin_menu = State()
    viewing_stats = State()
    viewing_users = State()
    managing_admins = State()
    editing_api_tokens = State()


# ===== ADMIN PANEL KEYBOARDS =====
def get_admin_menu_keyboard():
    """Main admin menu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    builder.row(InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"))
    builder.row(InlineKeyboardButton(text="🔑 Администраторы", callback_data="admin_manage_admins"))
    builder.row(InlineKeyboardButton(text="🔐 API Токены", callback_data="admin_api_tokens"))
    builder.row(InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu"))

    return builder.as_markup()


def get_stats_keyboard():
    """Statistics menu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="📈 Общая статистика", callback_data="admin_stats_general"))
    builder.row(InlineKeyboardButton(text="💰 Финансовая статистика", callback_data="admin_stats_finance"))
    builder.row(InlineKeyboardButton(text="🎨 Популярность стилей", callback_data="admin_stats_styles"))
    builder.row(InlineKeyboardButton(text="🏠 Популярность комнат", callback_data="admin_stats_rooms"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад в админ меню", callback_data="admin_menu"))

    return builder.as_markup()


def get_admin_back_keyboard():
    """Back to admin menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад в админ меню", callback_data="admin_menu"))
    return builder.as_markup()


# ===== ADMIN ENTRY POINT =====
@router.message(Command("admin"))
async def admin_start(message: Message, state: FSMContext):
    """Start admin panel"""
    user_id = message.from_user.id

    # Check if user is admin
    if user_id not in ADMIN_IDS:
        await message.answer("❌ <b>Доступ запрещён</b>\n\nЭто меню только для администраторов.")
        return

    await state.clear()
    await state.set_state(AdminStates.admin_menu)

    admin_text = """
🔐 <b>АДМИН-ПАНЕЛЬ InteriorBot</b>

Добро пожаловать в администраторское меню!

Здесь вы можете:
• 📊 Просмотреть статистику
• 👥 Управлять пользователями
• 🔑 Управлять администраторами
• 🔐 Редактировать API токены

Выберите действие:
"""

    menu = await message.answer(
        admin_text,
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML"
    )

    await state.update_data(menu_message_id=menu.message_id)


# ===== ADMIN MENU NAVIGATION =====
@router.callback_query(F.data == "admin_menu")
async def admin_menu_handler(callback: CallbackQuery, state: FSMContext):
    """Show admin menu"""
    await state.set_state(AdminStates.admin_menu)

    admin_text = """
🔐 <b>АДМИН-ПАНЕЛЬ InteriorBot</b>

Добро пожаловать в администраторское меню!

Здесь вы можете:
• 📊 Просмотреть статистику
• 👥 Управлять пользователями
• 🔑 Управлять администраторами
• 🔐 Редактировать API токены

Выберите действие:
"""

    await edit_menu(
        callback=callback,
        message_id=callback.message.message_id,
        text=admin_text,
        keyboard=get_admin_menu_keyboard()
    )


# ===== STATISTICS =====
@router.callback_query(F.data == "admin_stats")
async def admin_stats_menu(callback: CallbackQuery, state: FSMContext):
    """Show statistics menu"""
    await state.set_state(AdminStates.viewing_stats)

    stats_text = """
📊 <b>СТАТИСТИКА</b>

Выберите тип статистики:
"""

    await edit_menu(
        callback=callback,
        message_id=callback.message.message_id,
        text=stats_text,
        keyboard=get_stats_keyboard()
    )


@router.callback_query(F.data == "admin_stats_general")
async def admin_stats_general(callback: CallbackQuery, state: FSMContext):
    """Show general statistics"""
    try:
        total_users = await db.get_total_users()
        new_users_today = await db.get_new_users_today()
        new_users_week = await db.get_new_users_week()
        new_users_month = await db.get_new_users_month()
        total_gens = await db.get_total_generations()
        gens_today = await db.get_generations_today()

        stats_text = f"""
📈 <b>ОБЩАЯ СТАТИСТИКА</b>

👥 <b>Пользователи:</b>
├─ Всего: <b>{total_users}</b>
├─ Новых сегодня: <b>{new_users_today}</b>
├─ Новых на неделю: <b>{new_users_week}</b>
└─ Новых в месяц: <b>{new_users_month}</b>

🎨 <b>Генерации:</b>
├─ Всего: <b>{total_gens}</b>
└─ Сегодня: <b>{gens_today}</b>
"""

        await edit_menu(
            callback=callback,
            message_id=callback.message.message_id,
            text=stats_text,
            keyboard=get_stats_keyboard()
        )
    except Exception as e:
        logger.error(f"❌ Ошибка статистики: {e}")
        await callback.answer("❌ Ошибка при загрузке статистики")


@router.callback_query(F.data == "admin_stats_finance")
async def admin_stats_finance(callback: CallbackQuery, state: FSMContext):
    """Show financial statistics"""
    try:
        revenue_total = await db.get_total_revenue()
        revenue_today = await db.get_revenue_today()
        revenue_week = await db.get_revenue_week()
        revenue_month = await db.get_revenue_month()

        stats_text = f"""
💰 <b>ФИНАНСОВАЯ СТАТИСТИКА</b>

💳 <b>Доход:</b>
├─ Всего: <b>{revenue_total}₽</b>
├─ Сегодня: <b>{revenue_today}₽</b>
├─ На неделю: <b>{revenue_week}₽</b>
└─ В месяц: <b>{revenue_month}₽</b>

📊 <b>Расходы API:</b>
└─ Зависит от модели

💹 <b>Прибыль:</b>
└─ {revenue_total - (revenue_total * 0.1)}₽ (примерно)
"""

        await edit_menu(
            callback=callback,
            message_id=callback.message.message_id,
            text=stats_text,
            keyboard=get_stats_keyboard()
        )
    except Exception as e:
        logger.error(f"❌ Ошибка финансовой статистики: {e}")
        await callback.answer("❌ Ошибка при загрузке финансовой статистики")


@router.callback_query(F.data == "admin_stats_styles")
async def admin_stats_styles(callback: CallbackQuery, state: FSMContext):
    """Show popular styles statistics"""
    try:
        styles = await db.get_popular_styles()

        styles_text = "🎨 <b>ПОПУЛЯРНЫЕ СТИЛИ</b>\n\n"

        if styles:
            for i, style in enumerate(styles[:10], 1):
                styles_text += f"{i}. <b>{style['style'].title()}</b> — {style['count']} генераций\n"
        else:
            styles_text += "Нет данных"

        await edit_menu(
            callback=callback,
            message_id=callback.message.message_id,
            text=styles_text,
            keyboard=get_stats_keyboard()
        )
    except Exception as e:
        logger.error(f"❌ Ошибка статистики стилей: {e}")
        await callback.answer("❌ Ошибка при загрузке статистики стилей")


@router.callback_query(F.data == "admin_stats_rooms")
async def admin_stats_rooms(callback: CallbackQuery, state: FSMContext):
    """Show popular rooms statistics"""
    try:
        rooms = await db.get_popular_rooms()

        rooms_text = "🏠 <b>ПОПУЛЯРНЫЕ КОМНАТЫ</b>\n\n"

        if rooms:
            for i, room in enumerate(rooms[:10], 1):
                rooms_text += f"{i}. <b>{room['room'].upper()}</b> — {room['count']} генераций\n"
        else:
            rooms_text += "Нет данных"

        await edit_menu(
            callback=callback,
            message_id=callback.message.message_id,
            text=rooms_text,
            keyboard=get_stats_keyboard()
        )
    except Exception as e:
        logger.error(f"❌ Ошибка статистики комнат: {e}")
        await callback.answer("❌ Ошибка при загрузке статистики комнат")


# ===== USERS MANAGEMENT =====
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery, state: FSMContext):
    """Show users list"""
    try:
        await state.set_state(AdminStates.viewing_users)

        users = await db.get_all_users()

        users_text = "👥 <b>СПИСОК ПОЛЬЗОВАТЕЛЕЙ</b>\n\n"

        if users:
            users_text += "<b>ID | Telegram | Баланс | Дата регистрации</b>\n"
            users_text += "─" * 60 + "\n"

            for user in users[:20]:  # Show only first 20
                users_text += f"de>{user['user_id']}</code> | @{user['username'] or 'N/A'} | {user['balance']} токен | {user['reg_date'][:10]}\n"

            if len(users) > 20:
                users_text += f"\n... и ещё {len(users) - 20} пользователей"
        else:
            users_text += "Нет пользователей"

        await edit_menu(
            callback=callback,
            message_id=callback.message.message_id,
            text=users_text,
            keyboard=get_admin_back_keyboard()
        )
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке пользователей: {e}")
        await callback.answer("❌ Ошибка при загрузке пользователей")


# ===== ADMINS MANAGEMENT =====
@router.callback_query(F.data == "admin_manage_admins")
async def admin_manage_admins(callback: CallbackQuery, state: FSMContext):
    """Show admin management"""
    await state.set_state(AdminStates.managing_admins)

    admins_text = "🔑 <b>УПРАВЛЕНИЕ АДМИНИСТРАТОРАМИ</b>\n\n"
    admins_text += "<b>Текущие администраторы:</b>\n"

    for i, admin_id in enumerate(ADMIN_IDS, 1):
        admins_text += f"{i}. de>{admin_id}</code>\n"

    admins_text += "\n<i>Для добавления/удаления администраторов отредактируйте config.py</i>"

    await edit_menu(
        callback=callback,
        message_id=callback.message.message_id,
        text=admins_text,
        keyboard=get_admin_back_keyboard()
    )


# ===== API TOKENS MANAGEMENT =====
@router.callback_query(F.data == "admin_api_tokens")
async def admin_api_tokens(callback: CallbackQuery, state: FSMContext):
    """Show API tokens management"""
    await state.set_state(AdminStates.editing_api_tokens)

    tokens_text = "🔐 <b>API ТОКЕНЫ</b>\n\n"
    tokens_text += "<b>Установленные токены:</b>\n\n"

    tokens_text += f"🤖 <b>Replicate API:</b> {'✅ Установлен' if config.REPLICATE_API_TOKEN else '❌ Не установлен'}\n"
    tokens_text += f"💳 <b>YooKassa Shop ID:</b> {'✅ Установлен' if config.YOOKASSA_SHOP_ID else '❌ Не установлен'}\n"
    tokens_text += f"🔑 <b>YooKassa Secret:</b> {'✅ Установлен' if config.YOOKASSA_SECRET_KEY else '❌ Не установлен'}\n"

    tokens_text += "\n<i>Для изменения токенов отредактируйте .env файл</i>"

    await edit_menu(
        callback=callback,
        message_id=callback.message.message_id,
        text=tokens_text,
        keyboard=get_admin_back_keyboard()
    )


# ===== BACK TO MAIN MENU FROM ADMIN =====
@router.callback_query(F.data == "admin_back_to_main")
async def admin_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Go back to main menu from admin"""
    await state.clear()

    main_text = """
🎨 <b>Добро пожаловать в InteriorBot!</b>

Здесь вы найдёте идеи и вдохновение для дизайна своего дома и бизнеса.

Выберите, что вам нужно:
"""

    from keyboards.inline import get_main_menu_keyboard

    await edit_menu(
        callback=callback,
        message_id=callback.message.message_id,
        text=main_text,
        keyboard=get_main_menu_keyboard()
    )
