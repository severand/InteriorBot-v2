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


# ===== 🆕 НОВЫЙ ОБРАБОТЧИК: КНОПКА "АДМИН-ПАНЕЛЬ" =====
@router.callback_query(F.data == "open_admin_panel")
async def open_admin_panel_callback(callback: CallbackQuery, state: FSMContext):
    """
    🆕 НОВЫЙ ОБРАБОТЧИК для кнопки "⚙️ Админ-панель" из главного меню.
    Проверяет права доступа и открывает админ-панель.
    """
    user_id = callback.from_user.id

    logger.info(f"[ADMIN_PANEL] 🎯 Callback 'open_admin_panel' от user {user_id}")

    # Проверка прав доступа
    if user_id not in ADMIN_IDS:
        logger.warning(f"[ADMIN_PANEL] ❌ Доступ запрещён для user {user_id} (не в ADMIN_IDS)")
        await callback.answer("❌ Доступ запрещён\n\nЭто меню только для администраторов.", show_alert=True)
        return

    logger.info(f"[ADMIN_PANEL] ✅ Права доступа подтверждены для user {user_id}")

    # Очищаем state и устанавливаем состояние админ-меню
    await state.clear()
    await state.set_state(AdminStates.admin_menu)

    logger.info(f"[ADMIN_PANEL] ✅ State установлен: AdminStates.admin_menu")

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

    menu_message_id = callback.message.message_id

    # Редактируем текущее сообщение, показываем админ-панель
    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=admin_text,
        keyboard=get_admin_menu_keyboard(),
    )

    # Сохраняем message_id в state
    await state.update_data(menu_message_id=menu_message_id)

    logger.info(f"[ADMIN_PANEL] ✅ Админ-панель открыта для user {user_id}")


# ===== ADMIN ENTRY POINT (КОМАНДА /admin) =====
@router.message(Command("admin"))
async def admin_start(message: Message, state: FSMContext):
    """Start admin panel via /admin command"""
    user_id = message.from_user.id

    logger.info(f"[ADMIN_CMD] 🎯 Команда /admin от user {user_id}")

    # Check if user is admin
    if user_id not in ADMIN_IDS:
        logger.warning(f"[ADMIN_CMD] ❌ Доступ запрещён для user {user_id}")
        await message.answer("❌ <b>Доступ запрещён</b>\n\nЭто меню только для администраторов.", parse_mode="HTML")
        return

    logger.info(f"[ADMIN_CMD] ✅ Права доступа подтверждены")

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
    logger.info(f"[ADMIN_CMD] ✅ Админ-панель отправлена, message_id: {menu.message_id}")


# ===== ADMIN MENU NAVIGATION =====
@router.callback_query(F.data == "admin_menu")
async def admin_menu_handler(callback: CallbackQuery, state: FSMContext):
    """Show admin menu (навигация внутри админ-панели)"""
    logger.info(f"[ADMIN_MENU] 🎯 Callback 'admin_menu' от user {callback.from_user.id}")

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

    logger.info(f"[ADMIN_MENU] ✅ Админ-меню обновлено")


# ===== STATISTICS =====
@router.callback_query(F.data == "admin_stats")
async def admin_stats_menu(callback: CallbackQuery, state: FSMContext):
    """Show statistics menu"""
    logger.info(f"[ADMIN_STATS] 🎯 Callback 'admin_stats'")

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

    logger.info(f"[ADMIN_STATS] ✅ Меню статистики показано")


@router.callback_query(F.data == "admin_stats_general")
async def admin_stats_general(callback: CallbackQuery, state: FSMContext):
    """Show general statistics"""
    logger.info(f"[STATS_GENERAL] 🎯 Загрузка общей статистики")

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

        logger.info(f"[STATS_GENERAL] ✅ Общая статистика загружена")

    except Exception as e:
        logger.error(f"[STATS_GENERAL] ❌ Ошибка статистики: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке статистики", show_alert=True)


@router.callback_query(F.data == "admin_stats_finance")
async def admin_stats_finance(callback: CallbackQuery, state: FSMContext):
    """Show financial statistics"""
    logger.info(f"[STATS_FINANCE] 🎯 Загрузка финансовой статистики")

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

        logger.info(f"[STATS_FINANCE] ✅ Финансовая статистика загружена")

    except Exception as e:
        logger.error(f"[STATS_FINANCE] ❌ Ошибка финансовой статистики: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке финансовой статистики", show_alert=True)


@router.callback_query(F.data == "admin_stats_styles")
async def admin_stats_styles(callback: CallbackQuery, state: FSMContext):
    """Show popular styles statistics"""
    logger.info(f"[STATS_STYLES] 🎯 Загрузка статистики стилей")

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

        logger.info(f"[STATS_STYLES] ✅ Статистика стилей загружена")

    except Exception as e:
        logger.error(f"[STATS_STYLES] ❌ Ошибка статистики стилей: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке статистики стилей", show_alert=True)


@router.callback_query(F.data == "admin_stats_rooms")
async def admin_stats_rooms(callback: CallbackQuery, state: FSMContext):
    """Show popular rooms statistics"""
    logger.info(f"[STATS_ROOMS] 🎯 Загрузка статистики комнат")

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

        logger.info(f"[STATS_ROOMS] ✅ Статистика комнат загружена")

    except Exception as e:
        logger.error(f"[STATS_ROOMS] ❌ Ошибка статистики комнат: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке статистики комнат", show_alert=True)


# ===== USERS MANAGEMENT =====
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery, state: FSMContext):
    """Show users list"""
    logger.info(f"[ADMIN_USERS] 🎯 Загрузка списка пользователей")

    try:
        await state.set_state(AdminStates.viewing_users)

        users = await db.get_all_users()

        users_text = "👥 <b>СПИСОК ПОЛЬЗОВАТЕЛЕЙ</b>\n\n"

        if users:
            users_text += "<b>ID | Telegram | Баланс | Дата регистрации</b>\n"
            users_text += "─" * 60 + "\n"

            for user in users[:20]:  # Show only first 20
                users_text += f"<code>{user['user_id']}</code> | @{user['username'] or 'N/A'} | {user['balance']} токен | {user['reg_date'][:10]}\n"

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

        logger.info(f"[ADMIN_USERS] ✅ Список пользователей загружен ({len(users) if users else 0} юзеров)")

    except Exception as e:
        logger.error(f"[ADMIN_USERS] ❌ Ошибка при загрузке пользователей: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при загрузке пользователей", show_alert=True)


# ===== ADMINS MANAGEMENT =====
@router.callback_query(F.data == "admin_manage_admins")
async def admin_manage_admins(callback: CallbackQuery, state: FSMContext):
    """Show admin management"""
    logger.info(f"[MANAGE_ADMINS] 🎯 Открытие управления администраторами")

    await state.set_state(AdminStates.managing_admins)

    admins_text = "🔑 <b>УПРАВЛЕНИЕ АДМИНИСТРАТОРАМИ</b>\n\n"
    admins_text += "<b>Текущие администраторы:</b>\n"

    for i, admin_id in enumerate(ADMIN_IDS, 1):
        admins_text += f"{i}. <code>{admin_id}</code>\n"

    admins_text += "\n<i>Для добавления/удаления администраторов отредактируйте config.py</i>"

    await edit_menu(
        callback=callback,
        message_id=callback.message.message_id,
        text=admins_text,
        keyboard=get_admin_back_keyboard()
    )

    logger.info(f"[MANAGE_ADMINS] ✅ Управление администраторами показано")


# ===== API TOKENS MANAGEMENT =====
@router.callback_query(F.data == "admin_api_tokens")
async def admin_api_tokens(callback: CallbackQuery, state: FSMContext):
    """Show API tokens management"""
    logger.info(f"[API_TOKENS] 🎯 Открытие управления API токенами")

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

    logger.info(f"[API_TOKENS] ✅ Управление API токенами показано")


# ===== BACK TO MAIN MENU FROM ADMIN =====
@router.callback_query(F.data == "admin_back_to_main")
async def admin_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Go back to main menu from admin (если потребуется)"""
    logger.info(f"[ADMIN_BACK] 🎯 Возврат в главное меню из админки")

    await state.clear()

    main_text = """
🎨 <b>Добро пожаловать в InteriorBot!</b>

Здесь вы найдёте идеи и вдохновение для дизайна своего дома и бизнеса.

Выберите, что вам нужно:
"""

    from keyboards.inline import get_main_menu_keyboard

    # Проверяем, является ли пользователь админом для передачи is_admin
    user_id = callback.from_user.id
    is_admin = user_id in ADMIN_IDS

    await edit_menu(
        callback=callback,
        message_id=callback.message.message_id,
        text=main_text,
        keyboard=get_main_menu_keyboard(is_admin=is_admin)
    )

    logger.info(f"[ADMIN_BACK] ✅ Возврат в главное меню выполнен")
