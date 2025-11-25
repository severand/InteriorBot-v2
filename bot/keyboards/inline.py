# bot/keyboards/inline.py

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


# ===== ГЛАВНОЕ МЕНЮ =====
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню с 3 кнопками на полную ширину.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🏠 Для дома", callback_data="menu_home")
    )
    builder.row(
        InlineKeyboardButton(text="💼 Для бизнеса", callback_data="menu_business")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")
    )

    return builder.as_markup()


# ===== ПРОФИЛЬ - НА ПОЛНУЮ ШИРИНУ =====
def get_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура профиля на полную ширину экрана.
    Добавлены пробелы для расширения кнопок.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💳 Купить токены", callback_data="buy_generations")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== МЕНЮ "ДЛЯ ДОМА" - 10 КНОПОК ПО 2 В РЯДУ НА ПОЛНУЮ ШИРИНУ =====
def get_home_rooms_keyboard() -> InlineKeyboardMarkup:
    """
    10 комнат для дома. По 2 кнопки в ряду на полную ширину.
    Добавлены пробелы для расширения кнопок.
    """
    builder = InlineKeyboardBuilder()

    rooms = [
        ("🍳 Кухня       ", "room_kitchen"),
        ("🛏️ Спальня     ", "room_bedroom"),
        ("🛋️ Гостиная    ", "room_living_room"),
        ("💼 Кабинет     ", "room_office"),
        ("👶 Детская     ", "room_kids_room"),
        ("🚪 Коридор     ", "room_corridor"),
        ("🚽 Туалет      ", "room_toilet"),
        ("🛁 Ванная      ", "room_bathroom"),
        ("🏡 Прихожая    ", "room_entrance"),
        ("          .   ", "room_placeholder_1"),
    ]

    # Добавляем по 2 кнопки в ряд
    for i in range(0, len(rooms), 2):
        if i + 1 < len(rooms):
            builder.row(
                InlineKeyboardButton(text=rooms[i][0], callback_data=rooms[i][1]),
                InlineKeyboardButton(text=rooms[i + 1][0], callback_data=rooms[i + 1][1])
            )
        else:
            builder.row(
                InlineKeyboardButton(text=rooms[i][0], callback_data=rooms[i][1])
            )

    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== МЕНЮ "ДЛЯ БИЗНЕСА" - 10 КНОПОК ПО 2 В РЯДУ НА ПОЛНУЮ ШИРИНУ =====
def get_business_rooms_keyboard() -> InlineKeyboardMarkup:
    """
    10 типов помещений для бизнеса. По 2 кнопки в ряду на полную ширину.
    """
    builder = InlineKeyboardBuilder()

    business_types = [
        ("🏢 Офис", "room_office_business"),
        ("🍽️ Ресторан", "room_restaurant"),
        ("☕ Кафе", "room_cafe"),
        ("🦷 Стоматология", "room_dental"),
        ("💆 Массажный кабинет", "room_massage"),
        ("📦 Склад", "room_warehouse"),
        ("🛍️ Магазин", "room_shop"),
        ("💅 Салон красоты", "room_salon"),
        ("🏋️ Фитнес-клуб", "room_gym"),
        (".", "room_placeholder_2"),
    ]

    # Добавляем по 2 кнопки в ряд
    for i in range(0, len(business_types), 2):
        if i + 1 < len(business_types):
            builder.row(
                InlineKeyboardButton(text=business_types[i][0], callback_data=business_types[i][1]),
                InlineKeyboardButton(text=business_types[i + 1][0], callback_data=business_types[i + 1][1])
            )
        else:
            builder.row(
                InlineKeyboardButton(text=business_types[i][0], callback_data=business_types[i][1])
            )

    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== ОПЛАТА - ПАКЕТЫ =====
def get_payment_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора пакетов оплаты.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💎 10 токенов - 290₽", callback_data="pay_10_290")
    )
    builder.row(
        InlineKeyboardButton(text="💎 25 токенов - 490₽", callback_data="pay_25_490")
    )
    builder.row(
        InlineKeyboardButton(text="💎 60 токенов - 990₽", callback_data="pay_60_990")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== ОПЛАТА - ПРОВЕРКА =====
def get_payment_check_keyboard(confirmation_url: str) -> InlineKeyboardMarkup:
    """
    Клавиатура после создания платежа.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔗 Перейти к оплате", url=confirmation_url)
    )
    builder.row(
        InlineKeyboardButton(text="✅ Проверить платёж", callback_data="check_payment")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== ВЫБОР СТИЛЯ (для creation.py) =====
def get_style_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора стиля дизайна.
    """
    builder = InlineKeyboardBuilder()

    styles = [
        ("🏢 Современный", "style_modern"),
        ("⬜ Минимализм", "style_minimalism"),
        ("🇸🇪 Скандинавский", "style_scandinavian"),
        ("🏭 Лофт", "style_loft"),
        ("🌾 Рустик", "style_rustic"),
        ("🏜️ Джапанди", "style_japandi"),
        ("🌸 Бохо", "style_boho"),
        ("🌊 Средиземноморский", "style_mediterranean"),
        ("📻 Mid-century", "style_midcentury"),
        ("💎 Ар-деко", "style_art_deco"),
    ]

    for text, callback in styles:
        builder.row(
            InlineKeyboardButton(text=text, callback_data=callback)
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_room")
    )

    return builder.as_markup()


# ===== ПОСЛЕ ГЕНЕРАЦИИ =====
def get_post_generation_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура после генерации дизайна.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎨 Попробовать другой стиль", callback_data="change_style")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== ВЫБОР КОМНАТЫ (для creation.py) =====
def get_room_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора типа комнаты для дизайна. По 2 в ряду.
    """
    builder = InlineKeyboardBuilder()

    rooms = [
        ("🍳 Кухня       ", "room_kitchen"),
        ("🛏️ Спальня     ", "room_bedroom"),
        ("🛋️ Гостиная    ", "room_living_room"),
        ("💼 Кабинет     ", "room_office"),
        ("👶 Детская     ", "room_kids_room"),
        ("🚪 Коридор     ", "room_corridor"),
        ("🚽 Туалет      ", "room_toilet"),
        ("🛁 Ванная      ", "room_bathroom"),
    ]

    for i in range(0, len(rooms), 2):
        if i + 1 < len(rooms):
            builder.row(
                InlineKeyboardButton(text=rooms[i][0], callback_data=rooms[i][1]),
                InlineKeyboardButton(text=rooms[i + 1][0], callback_data=rooms[i + 1][1])
            )
        else:
            builder.row(
                InlineKeyboardButton(text=rooms[i][0], callback_data=rooms[i][1])
            )

    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()
