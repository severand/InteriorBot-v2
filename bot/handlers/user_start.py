# handlers/user_start.py
# С ОТЛАДКОЙ И НОВОЙ ЛОГИКОЙ ВЫБОРА РЕЖИМА

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.db import db
from keyboards.inline import (
    get_main_menu_keyboard,
    get_profile_keyboard,
    get_home_rooms_keyboard,
    get_business_rooms_keyboard,
    get_design_mode_keyboard,  # ← НОВАЯ КЛАВИАТУРА
)
from utils.texts import (
    START_TEXT,
    MAIN_MENU_TEXT,
    PROFILE_TEXT,
    HOME_TEXT,
    BUSINESS_TEXT,
    DESIGN_MODE_TEXT,  # ← НОВЫЙ ТЕКСТ
)
from utils.navigation import edit_menu
from states.fsm import MainMenuStates, CreationStates
from utils.debug import (
    debug_handler,
    log_state,
    log_user_choice,
    log_message_send,
    log_state_transition,
)

logger = logging.getLogger(__name__)
router = Router()

logger.info("🔧 [user_start.py] Модуль загружен")


# ===== СТАРТ БОТА =====
@router.message(Command("start"))
@debug_handler
async def start_command(message: Message, state: FSMContext):
    """Команда /start — показать главное меню"""
    user_id = message.from_user.id

    logger.info(f"[START] 🎯 Запуск /start для user {user_id}")

    # Создаём пользователя если его нет
    await db.create_user(user_id, message.from_user.username or "Unknown")
    logger.info(f"[START] ✅ Пользователь создан/проверен")

    await state.clear()
    logger.info(f"[START] ✅ State очищена")

    await state.set_state(MainMenuStates.main_menu)
    logger.info(f"[START] ✅ State установлена: main_menu")

    log_message_send(user_id, START_TEXT, 3)

    # Отправляем главное меню
    menu = await message.answer(
        START_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    logger.info(f"[START] ✅ Главное меню отправлено, message_id: {menu.message_id}")

    # СОХРАНЯЕМ message_id в state
    await state.update_data(menu_message_id=menu.message_id)

    await log_state(state, "STATE ПОСЛЕ /start")


# ===== ГЛАВНОЕ МЕНЮ =====
@router.callback_query(F.data == "main_menu")
@debug_handler
async def go_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    logger.info(f"[MAIN_MENU] 🎯 Callback: {callback.data}")

    await state.clear()
    await state.set_state(MainMenuStates.main_menu)

    menu_message_id = callback.message.message_id
    logger.info(f"[MAIN_MENU] ✅ Message ID: {menu_message_id}")

    log_message_send(callback.from_user.id, MAIN_MENU_TEXT, 3)

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=MAIN_MENU_TEXT,
        keyboard=get_main_menu_keyboard(),
    )

    await state.update_data(menu_message_id=menu_message_id)
    await log_state(state, "STATE В ГЛАВНОМ МЕНЮ")


# ===== "ДЛЯ ДОМА" =====
@router.callback_query(F.data == "menu_home")
@debug_handler
async def home_menu(callback: CallbackQuery, state: FSMContext):
    """Меню "Для дома" """
    logger.info(f"[HOME_MENU] 🎯 Callback: {callback.data}")

    log_user_choice(callback.from_user.id, "Меню", "Для дома")

    await state.set_state(MainMenuStates.home_menu)
    logger.info(f"[HOME_MENU] ✅ State: home_menu")

    menu_message_id = callback.message.message_id

    log_message_send(callback.from_user.id, HOME_TEXT, 12)

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=HOME_TEXT,
        keyboard=get_home_rooms_keyboard(),
    )

    await state.update_data(menu_message_id=menu_message_id)
    await log_state(state, "STATE В МЕНЮ ДОМА")


# ===== "ДЛЯ БИЗНЕСА" =====
@router.callback_query(F.data == "menu_business")
@debug_handler
async def business_menu(callback: CallbackQuery, state: FSMContext):
    """Меню "Для бизнеса" """
    logger.info(f"[BUSINESS_MENU] 🎯 Callback: {callback.data}")

    log_user_choice(callback.from_user.id, "Меню", "Для бизнеса")

    await state.set_state(MainMenuStates.business_menu)
    logger.info(f"[BUSINESS_MENU] ✅ State: business_menu")

    menu_message_id = callback.message.message_id

    log_message_send(callback.from_user.id, BUSINESS_TEXT, 10)

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=BUSINESS_TEXT,
        keyboard=get_business_rooms_keyboard(),
    )

    await state.update_data(menu_message_id=menu_message_id)
    await log_state(state, "STATE В МЕНЮ БИЗНЕСА")


# ===== ВЫБОР КОМНАТЫ → ЭКРАН ВЫБОРА РЕЖИМА =====
@router.callback_query(F.data.startswith("room_"))
@debug_handler
async def room_selected(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора комнаты.
    НОВАЯ ЛОГИКА: После выбора комнаты показываем ЭКРАН ВЫБОРА РЕЖИМА
    """
    logger.info(f"[ROOM_SELECTED] 🎯 Callback: {callback.data}")

    # Извлекаем название комнаты из callback_data
    room_type = callback.data.replace("room_", "")
    logger.info(f"[ROOM_SELECTED] ✅ Выбрана комната: {room_type}")

    log_user_choice(callback.from_user.id, "Комната", room_type)

    # Сохраняем выбранную комнату
    await state.update_data(room=room_type)

    # Переходим в состояние выбора режима дизайна
    await state.set_state(CreationStates.choose_mode)
    logger.info(f"[ROOM_SELECTED] ✅ State: CreationStates.choose_mode")

    menu_message_id = callback.message.message_id

    # Формируем красивое название комнаты для отображения
    room_names = {
        'dining_room': 'Столовая',
        'kitchen': 'Кухня',
        'living_room': 'Гостиная',
        'bedroom': 'Спальня',
        'office_work': 'Кабинет для работы',
        'wardrobe_closet': 'Гардеробная',
        'kids_room': 'Детская комната',
        'entrance_hall': 'Прихожая',
        'toilet_restroom': 'Санузел',
        'bathroom_bath': 'Ванная',
        'balcony_terrace': 'Балкон',
        'manroom_den': 'Мужская берлога',
        'office_business': 'Офис',
        'restaurant': 'Ресторан',
        'cafe': 'Кафе',
        'dental': 'Стоматология',
        'massage': 'Массажный салон',
        'warehouse': 'Склад',
        'shop': 'Магазин',
        'salon': 'Салон красоты',
        'gym': 'Фитнес-клуб',
        'grocery': 'Продуктовый',
    }

    room_display_name = room_names.get(room_type, room_type.replace('_', ' ').title())

    # Показываем экран выбора режима
    design_mode_text = DESIGN_MODE_TEXT.format(room_name=room_display_name)

    log_message_send(callback.from_user.id, design_mode_text, 2)

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=design_mode_text,
        keyboard=get_design_mode_keyboard(),
    )

    await state.update_data(menu_message_id=menu_message_id)
    await log_state(state, "STATE ПОСЛЕ ВЫБОРА КОМНАТЫ → ВЫБОР РЕЖИМА")


# ===== РЕЖИМ 1: "ПОСМОТРЕТЬ И ВЫБРАТЬ ДИЗАЙН" =====
@router.callback_query(F.data == "mode_select_design")
@debug_handler
async def mode_select_design(callback: CallbackQuery, state: FSMContext):
    """
    Режим: Посмотреть и выбрать готовый дизайн.
    Ведет к выбору стилей → генерация
    """
    logger.info(f"[MODE_SELECT] 🎯 Выбран режим: Посмотреть и выбрать дизайн")

    log_user_choice(callback.from_user.id, "Режим", "Посмотреть и выбрать дизайн")

    # Переходим в состояние выбора стиля
    await state.set_state(CreationStates.choose_style)
    logger.info(f"[MODE_SELECT] ✅ State: CreationStates.choose_style")

    menu_message_id = callback.message.message_id

    # Показываем экран выбора стиля
    from keyboards.inline import get_style_keyboard
    from utils.texts import CHOOSE_STYLE_TEXT

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=CHOOSE_STYLE_TEXT,
        keyboard=get_style_keyboard(),
    )

    await state.update_data(menu_message_id=menu_message_id)
    await log_state(state, "STATE → ВЫБОР СТИЛЯ")


# ===== РЕЖИМ 2: "СОЗДАТЬ СВОЙ ИНТЕРЬЕР" =====
@router.callback_query(F.data == "mode_create_custom")
@debug_handler
async def mode_create_custom(callback: CallbackQuery, state: FSMContext):
    """
    Режим: Создать свой интерьер.
    Ведет к выбору мебели → цветов → генерация
    """
    logger.info(f"[MODE_CUSTOM] 🎯 Выбран режим: Создать свой интерьер")

    log_user_choice(callback.from_user.id, "Режим", "Создать свой интерьер")

    # Переходим в состояние выбора мебели
    await state.set_state(CreationStates.choose_furniture)
    logger.info(f"[MODE_CUSTOM] ✅ State: CreationStates.choose_furniture")

    menu_message_id = callback.message.message_id

    # Показываем экран выбора мебели
    try:
        from handlers.design_step1_furniture import show_furniture_screen
        logger.info(f"[MODE_CUSTOM] 📥 Импорт show_furniture_screen успешен")

        await show_furniture_screen(callback.message, state)
        logger.info(f"[MODE_CUSTOM] ✅ Экран мебели показан")

    except Exception as e:
        logger.error(f"[MODE_CUSTOM] ❌ Ошибка при показе экрана мебели: {e}", exc_info=True)
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
        return

    await state.update_data(menu_message_id=menu_message_id)
    await log_state(state, "STATE → ВЫБОР МЕБЕЛИ")


# ===== ПРОФИЛЬ =====
@router.callback_query(F.data == "menu_profile")
@debug_handler
async def profile_callback(callback: CallbackQuery, state: FSMContext):
    """Показать профиль пользователя"""
    logger.info(f"[PROFILE] 🎯 Callback: {callback.data}")

    await state.set_state(MainMenuStates.profile)
    logger.info(f"[PROFILE] ✅ State: profile")

    user_id = callback.from_user.id
    username = callback.from_user.username or "Не указано"

    # Получаем баланс пользователя
    balance = await db.get_balance(user_id)
    logger.info(f"[PROFILE] ✅ Баланс: {balance}")

    profile_text = PROFILE_TEXT.format(
        user_id=user_id,
        username=username,
        balance=balance,
        reg_date="Недавно"
    )

    menu_message_id = callback.message.message_id

    log_message_send(user_id, profile_text, 2)

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=profile_text,
        keyboard=get_profile_keyboard(),
    )

    await state.update_data(menu_message_id=menu_message_id)
    await log_state(state, "STATE В ПРОФИЛЕ")


# ===== BUY TOKENS =====
@router.callback_query(F.data == "buy_generations")
@debug_handler
async def buy_generations(callback: CallbackQuery, state: FSMContext):
    """Перейти к покупке токенов"""
    logger.info(f"[BUY] 🎯 Callback: {callback.data}")

    log_user_choice(callback.from_user.id, "Действие", "Купить токены")

    await callback.answer("💳 Переходим к покупке токенов...")
    logger.info(f"[BUY] ✅ Ответ отправлен")

# ===== НАЗАД К ВЫБОРУ КОМНАТ =====
@router.callback_query(F.data == "back_to_rooms")
@debug_handler
async def back_to_rooms(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору комнат"""
    logger.info(f"[BACK_TO_ROOMS] 🎯 Возврат к выбору комнат")

    data = await state.get_data()
    current_menu = data.get('current_menu', 'home')  # home или business

    if current_menu == 'business':
        await business_menu(callback, state)
    else:
        await home_menu(callback, state)


# ===== НАЗАД К ВЫБОРУ РЕЖИМА (ИЗ СТИЛЕЙ ИЛИ МЕБЕЛИ) =====
@router.callback_query(F.data == "back_to_mode_selection")
@debug_handler
async def back_to_mode_selection(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору режима (экран с 2 кнопками)"""
    logger.info(f"[BACK_TO_MODE] 🎯 Возврат к экрану выбора режима")

    # Получаем room из state
    data = await state.get_data()
    room_type = data.get('room')

    if not room_type:
        logger.error("[BACK_TO_MODE] ❌ Room не найден в state")
        await callback.answer("❌ Ошибка: комната не найдена", show_alert=True)
        return

    # ✅ ИСПРАВЛЕНИЕ: НЕ МЕНЯЕМ callback.data - вместо этого вызываем напрямую
    menu_message_id = callback.message.message_id

    # Формируем красивое название комнаты для отображения
    room_names = {
        'dining_room': 'Столовая',
        'kitchen': 'Кухня',
        'living_room': 'Гостиная',
        'bedroom': 'Спальня',
        'office_work': 'Кабинет для работы',
        'wardrobe_closet': 'Гардеробная',
        'kids_room': 'Детская комната',
        'entrance_hall': 'Прихожая',
        'toilet_restroom': 'Санузел',
        'bathroom_bath': 'Ванная',
        'balcony_terrace': 'Балкон',
        'manroom_den': 'Мужская берлога',
        'office_business': 'Офис',
        'restaurant': 'Ресторан',
        'cafe': 'Кафе',
        'dental': 'Стоматология',
        'massage': 'Массажный салон',
        'warehouse': 'Склад',
        'shop': 'Магазин',
        'salon': 'Салон красоты',
        'gym': 'Фитнес-клуб',
        'grocery': 'Продуктовый',
    }

    room_display_name = room_names.get(room_type, room_type.replace('_', ' ').title())

    # Переходим в состояние выбора режима дизайна
    await state.set_state(CreationStates.choose_mode)

    # Показываем экран выбора режима
    design_mode_text = DESIGN_MODE_TEXT.format(room_name=room_display_name)

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=design_mode_text,
        keyboard=get_design_mode_keyboard(),
    )

    await state.update_data(menu_message_id=menu_message_id)
    logger.info(f"[BACK_TO_MODE] ✅ Вернулись к выбору режима")
