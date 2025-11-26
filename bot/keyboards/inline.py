# bot/keyboards/inline.py

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


# ===== ГЛАВНОЕ МЕНЮ =====
def get_main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """
    Главное меню с 3 кнопками на полную ширину.
    Если is_admin=True, добавляет кнопку ⚙️ Админ-панель
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

    # ✅ КНОПКА ⚙️ ВИДНА ТОЛЬКО ДЛЯ АДМИНОВ
    if is_admin:
        builder.row(
            InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="open_admin_panel")
        )

    return builder.as_markup()


# ===== ПРОФИЛЬ - НА ПОЛНУЮ ШИРИНУ =====
def get_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура профиля на полную ширину экрана.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="💳 Купить токены", callback_data="buy_generations")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== МЕНЮ "ДЛЯ ДОМА" - 12 КНОПОК ПО 2 В РЯДУ =====
def get_home_rooms_keyboard() -> InlineKeyboardMarkup:
    """
    12 комнат для дома. По 2 кнопки в ряду.
    ВСЕ callback_data УНИКАЛЬНЫЕ!
    """
    builder = InlineKeyboardBuilder()

    rooms = [
        ("🛋️ Столовая", "room_dining_room"),
        ("🍳 Кухня", "room_kitchen"),
        ("🛋️ Гостиная", "room_living_room"),
        ("🛏️ Спальня", "room_bedroom"),
        ("💼 Кабинет для работы", "room_office_work"),
        ("🪟 Гардеробная", "room_wardrobe_closet"),
        ("👶 Детская комната", "room_kids_room"),
        ("🏡 Прихожая", "room_entrance_hall"),
        ("🚽 Санузел", "room_toilet_restroom"),
        ("🛁 Ванная", "room_bathroom_bath"),
        ("🪟 Балкон", "room_balcony_terrace"),
        ("🔳 Мужская берлога", "room_manroom_den"),
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


# ===== МЕНЮ "ДЛЯ БИЗНЕСА" - 10 КНОПОК ПО 2 В РЯДУ =====
def get_business_rooms_keyboard() -> InlineKeyboardMarkup:
    """
    10 типов помещений для бизнеса. По 2 кнопки в ряду.
    """
    builder = InlineKeyboardBuilder()

    business_types = [
        ("🏢 Офис", "room_office_business"),
        ("🍽️ Ресторан", "room_restaurant"),
        ("☕ Кафе", "room_cafe"),
        ("🦷 Стоматология", "room_dental"),
        ("💆 Массажный салон", "room_massage"),
        ("📦 Склад", "room_warehouse"),
        ("🛍️ Магазин", "room_shop"),
        ("💅 Салон красоты", "room_salon"),
        ("🏋️ Фитнес-клуб", "room_gym"),
        ("🏪 Продуктовый", "room_grocery"),
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
    Клавиатура выбора стиля дизайна. По 2 в ряду.
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

    # Добавляем по 2 кнопки в ряд
    for i in range(0, len(styles), 2):
        if i + 1 < len(styles):
            builder.row(
                InlineKeyboardButton(text=styles[i][0], callback_data=styles[i][1]),
                InlineKeyboardButton(text=styles[i + 1][0], callback_data=styles[i + 1][1])
            )
        else:
            builder.row(
                InlineKeyboardButton(text=styles[i][0], callback_data=styles[i][1])
            )

    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_room")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


# ===== ПОСЛЕ ГЕНЕРАЦИИ =====
def get_post_generation_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура после генерации дизайна.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🎨 Другой стиль", callback_data="change_style")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()

# ===== ВЫБОР РЕЖИМА ДИЗАЙНА (НОВОЕ!) =====
def get_design_mode_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора режима создания дизайна.
    Появляется ПОСЛЕ выбора комнаты.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🎨     Посмотреть и выбрать дизайн                ",
            callback_data="mode_select_design"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🛋️ Создать свой интерьер",
            callback_data="mode_create_custom"
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад к комнатам", callback_data="back_to_rooms")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()

# ===== ВЫБОР СТИЛЯ (для creation.py) =====
def get_style_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора стиля дизайна. По 2 в ряду.
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

    # Добавляем по 2 кнопки в ряд
    for i in range(0, len(styles), 2):
        if i + 1 < len(styles):
            builder.row(
                InlineKeyboardButton(text=styles[i][0], callback_data=styles[i][1]),
                InlineKeyboardButton(text=styles[i + 1][0], callback_data=styles[i + 1][1])
            )
        else:
            builder.row(
                InlineKeyboardButton(text=styles[i][0], callback_data=styles[i][1])
            )

    # ✅ ИСПРАВЛЕНО: callback_data для кнопки "Назад"
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_mode_selection")
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


