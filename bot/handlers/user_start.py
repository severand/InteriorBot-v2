# bot/handlers/user_start.py

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
)
from utils.texts import (
    START_TEXT,
    MAIN_MENU_TEXT,
    PROFILE_TEXT,
    HOME_TEXT,
    BUSINESS_TEXT,
)
from utils.navigation import edit_menu
from states.fsm import MainMenuStates

logger = logging.getLogger(__name__)
router = Router()


# ===== СТАРТ БОТА =====
@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Команда /start — показать главное меню"""
    user_id = message.from_user.id

    # Создаём пользователя если его нет
    await db.create_user(user_id, message.from_user.username or "Unknown")

    await state.clear()
    await state.set_state(MainMenuStates.main_menu)

    # Отправляем главное меню
    menu = await message.answer(
        START_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

    # СОХРАНЯЕМ message_id в state
    await state.update_data(menu_message_id=menu.message_id)


# ===== ГЛАВНОЕ МЕНЮ =====
@router.callback_query(F.data == "main_menu")
async def go_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    await state.set_state(MainMenuStates.main_menu)

    # ПОЛУЧАЕМ message_id из callback.message, не из state!
    menu_message_id = callback.message.message_id

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=MAIN_MENU_TEXT,
        keyboard=get_main_menu_keyboard(),
    )

    # ОБНОВЛЯЕМ state с новым message_id
    await state.update_data(menu_message_id=menu_message_id)


# ===== "ДЛЯ ДОМА" =====
@router.callback_query(F.data == "menu_home")
async def home_menu(callback: CallbackQuery, state: FSMContext):
    """Меню "Для дома" — РЕДАКТИРУЕМ существующее сообщение"""
    await state.set_state(MainMenuStates.home_menu)

    # ПОЛУЧАЕМ message_id из callback.message, не из state!
    menu_message_id = callback.message.message_id

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=HOME_TEXT,
        keyboard=get_home_rooms_keyboard(),
    )

    # ОБНОВЛЯЕМ state с новым message_id
    await state.update_data(menu_message_id=menu_message_id)


# ===== "ДЛЯ БИЗНЕСА" =====
@router.callback_query(F.data == "menu_business")
async def business_menu(callback: CallbackQuery, state: FSMContext):
    """Меню "Для бизнеса" — РЕДАКТИРУЕМ существующее сообщение"""
    await state.set_state(MainMenuStates.business_menu)

    # ПОЛУЧАЕМ message_id из callback.message, не из state!
    menu_message_id = callback.message.message_id

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=BUSINESS_TEXT,
        keyboard=get_business_rooms_keyboard(),
    )

    # ОБНОВЛЯЕМ state с новым message_id
    await state.update_data(menu_message_id=menu_message_id)


# ===== ПРОФИЛЬ =====
@router.callback_query(F.data == "menu_profile")
async def profile_callback(callback: CallbackQuery, state: FSMContext):
    """Показать профиль пользователя — РЕДАКТИРУЕМ существующее сообщение"""
    await state.set_state(MainMenuStates.profile)

    user_id = callback.from_user.id
    username = callback.from_user.username or "Не указано"

    # Получаем баланс пользователя
    balance = await db.get_balance(user_id)

    profile_text = PROFILE_TEXT.format(
        user_id=user_id,
        username=username,
        balance=balance,
        reg_date="Недавно"
    )

    # ПОЛУЧАЕМ message_id из callback.message, не из state!
    menu_message_id = callback.message.message_id

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=profile_text,
        keyboard=get_profile_keyboard(),
    )

    # ОБНОВЛЯЕМ state с новым message_id
    await state.update_data(menu_message_id=menu_message_id)


# ===== BUY TOKENS (из профиля) =====
@router.callback_query(F.data == "buy_generations")
async def buy_generations(callback: CallbackQuery, state: FSMContext):
    """Перейти к покупке токенов"""
    await callback.answer()
