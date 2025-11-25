# bot/handlers/user_start.py

# bot/handlers/user_start.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import db
from keyboards.inline import (
    get_main_menu_keyboard,
    get_profile_keyboard,
)
from utils.texts import START_TEXT, PROFILE_TEXT
from utils.navigation import edit_menu, show_main_menu

router = Router()


async def ensure_user(user_id: int) -> None:
    """
    Гарантирует, что пользователь есть в базе.
    Если нет — создаёт запись.
    """
    user = await db.get_user(user_id)
    if not user:
        await db.add_user(user_id=user_id)


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """
    Стартовая команда.

    1) Чистим состояние.
    2) Гарантируем пользователя в БД.
    3) Показываем ЕДИНОЕ главное меню:
       - 🏠 Для дома
       - 💼 Для бизнеса
       - 👤 Профиль
    """
    await state.clear()
    user_id = message.from_user.id

    await ensure_user(user_id)

    # Текст приветствия: объясняем, что тут идеи для дома и бизнеса
    text = START_TEXT

    # Отправляем новое сообщение с главным меню
    sent = await message.answer(
        text=text,
        reply_markup=get_main_menu_keyboard(),
    )

    # Сохраняем id сообщения меню в state, чтобы дальше всегда его редактировать
    await state.update_data(menu_message_id=sent.message_id)


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """
    Возврат в главное меню из любых мест.
    ВСЕГДА возвращаемся к одному сообщению с тремя кнопками.
    """
    await state.clear()
    await show_main_menu(
        callback=callback,
        text=START_TEXT,
        keyboard=get_main_menu_keyboard(),
    )


@router.callback_query(F.data == "menu_home")
async def home_menu_callback(callback: CallbackQuery, state: FSMContext):
    """
    Ветка 'Для дома'.

    ВАЖНО: здесь пока ТОЛЬКО переход на следующий экран.
    На этом шаге НЕ трогаем список помещений и стили.
    Просто проверяем, что:
    - старое меню ЗАМЕНЯЕТСЯ новым
    - нет двух сообщений с кнопками
    - всегда есть кнопка 'Главное меню'
    """
    data = await state.get_data()
    menu_message_id = data.get("menu_message_id")

    text = (
        "🏠 Интерьеры для дома\n\n"
        "Здесь вы сможете выбрать помещение (кухня, спальня, кабинет и т.д.) "
        "и получить идеи дизайна.\n\n"
        "Сейчас мы настраиваем структуру меню. "
        "Позже добавим конкретный список помещений и генерацию."
    )

    # Меняем ТО ЖЕ сообщение, а не создаём новое
    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=text,
        keyboard=get_main_menu_keyboard(),  # временно оставляем то же меню
    )


@router.callback_query(F.data == "menu_business")
async def business_menu_callback(callback: CallbackQuery, state: FSMContext):
    """
    Ветка 'Для бизнеса'.

    Аналогично 'Для дома': пока только демонстрируем экран.
    Позже сюда добавим выбор типа помещения для бизнеса.
    """
    data = await state.get_data()
    menu_message_id = data.get("menu_message_id")

    text = (
        "💼 Интерьеры для бизнеса\n\n"
        "Здесь будут варианты помещений для вашего бизнеса: офис, ресторан, "
        "кафе, магазин, салон красоты и многое другое.\n\n"
        "Сейчас настраиваем навигацию. "
        "Дальше добавим список помещений и генерацию."
    )

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=text,
        keyboard=get_main_menu_keyboard(),  # временно то же меню
    )


@router.callback_query(F.data == "menu_profile")
async def profile_callback(callback: CallbackQuery, state: FSMContext):
    """
    Профиль пользователя.

    Показываем:
    - имя / username
    - количество токенов / генераций (что есть в БД)
    - кнопки управления (например, покупка токенов)
    И ОБЯЗАТЕЛЬНО кнопку 'Главное меню'.
    """
    data = await state.get_data()
    menu_message_id = data.get("menu_message_id")

    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    text = PROFILE_TEXT.format(
        first_name=callback.from_user.first_name or "Пользователь",
        username=f"@{callback.from_user.username}" if callback.from_user.username else "—",
        tokens=user.tokens if user else 0,
        generations=user.generated_images if user else 0,
    )

    await edit_menu(
        callback=callback,
        message_id=menu_message_id,
        text=text,
        keyboard=get_profile_keyboard(),
    )
