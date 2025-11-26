# handlers/design_step1_furniture.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

router = Router()
logger = logging.getLogger(__name__)

logger.info("🔧 [design_step1_furniture.py] Модуль загружен")


class FurnitureState(StatesGroup):
    selecting = State()


KITCHEN_FURNITURE = {
    'table': ('🍽️', 'Обеденный стол               '),
    'kitchen_set': ('🍳', 'Гарнитур               '),
    'fridge': ('🧊', 'Холодильник                  '),
    'bar': ('🍷', 'Барная                         '),
    'lighting': ('💡', 'Подсветка                 '),
    'trash': ('🪣', 'Мусор                         '),
    'microwave': ('🔧', 'Микро                     '),
    'shelves': ('📚', 'Полки                      '),
}

BEDROOM_FURNITURE = {
    'bed': ('🛏️', 'Кровать'),
    'nightstands': ('🌙', 'Тумбочки'),
    'wardrobe': ('👕', 'Шкаф'),
    'desk': ('📝', 'Стол'),
    'mirror': ('🪞', 'Зеркало'),
    'shelves': ('📚', 'Полки'),
}

LIVING_ROOM_FURNITURE = {
    'sofa': ('🛋️', 'Диван'),
    'armchair': ('🪑', 'Кресло'),
    'table': ('📱', 'Столик'),
    'tv_stand': ('📺', 'ТВ'),
    'shelves': ('📚', 'Полки'),
    'cabinet': ('🗄️', 'Шкаф'),
}

OFFICE_FURNITURE = {
    'desk': ('📝', 'Стол'),
    'chair': ('🪑', 'Кресло'),
    'shelves': ('📚', 'Полки'),
    'cabinet': ('🗄️', 'Шкаф'),
    'monitor': ('💻', 'Монитор'),
    'lamp': ('💡', 'Лампа'),
}

# ✅ ТОЛЬКО ЭТО ИЗМЕНИЛ - добавил маппинг для office_work
FURNITURE_BY_ROOM = {
    'kitchen': KITCHEN_FURNITURE,
    'bedroom': BEDROOM_FURNITURE,
    'living_room': LIVING_ROOM_FURNITURE,
    'office': OFFICE_FURNITURE,
    'office_work': OFFICE_FURNITURE,  # ← ДОБАВИЛ ТОЛЬКО ЭТУ СТРОКУ!
}


async def show_furniture_screen(message: types.Message, state: FSMContext):
    """Показывает экран мебели"""

    logger.info(f"[FURNITURE_SCREEN] 🎯 Показываю экран мебели")

    try:
        data = await state.get_data()
        room = data.get('room')
        selected = data.get('furniture', {})

        logger.info(f"[FURNITURE_SCREEN] ✅ Room: {room}, Selected: {len(selected)} items")

        furniture_options = FURNITURE_BY_ROOM.get(room, {})
        logger.info(f"[FURNITURE_SCREEN] ✅ Furniture options loaded: {len(furniture_options)}")

        text = f"🛋️ <b>{room.upper()} - выберите обстановку</b>\n\n"

        if selected:
            text += "✅ <b>выбрано:</b>\n"
            for key in selected.keys():
                if key in furniture_options:
                    emoji, label = furniture_options[key]
                    text += f"• {label}\n"
            text += "\n"

       #  text += "🔄 <b>ДОСТУПНЫЕ:</b>\n"

        buttons = []
        for key, (emoji, label) in furniture_options.items():
            status = "✅" if key in selected else " "
            buttons.append(
                types.InlineKeyboardButton(
                    text=f"{status} {label}\u2063\u2063\u2063",
                    callback_data=f"furn:{key}"
                )
            )

        logger.info(f"[FURNITURE_SCREEN] ✅ Created {len(buttons)} buttons")

        keyboard_buttons = [
            [buttons[i], buttons[i + 1]] if i + 1 < len(buttons) else [buttons[i]]
            for i in range(0, len(buttons), 2)
        ]

        # ✅ ДОБАВИЛ ТОЛЬКО ЭТУ КНОПКУ!
        keyboard_buttons.append([
            types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_mode_selection"),
        ])
        keyboard_buttons.append([
            types.InlineKeyboardButton(text="➡️ ДАЛЕЕ: ЦВЕТА", callback_data="to_colors"),
        ])

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        logger.info(f"[FURNITURE_SCREEN] 📤 Отправляю сообщение")
        await message.edit_text(text, reply_markup=keyboard)
        logger.info(f"[FURNITURE_SCREEN] ✅ Сообщение отправлено")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в show_furniture_screen: {e}", exc_info=True)


@router.callback_query(F.data.startswith("furn:"))
async def toggle_furniture(query: types.CallbackQuery, state: FSMContext):
    """Toggle мебель"""

    logger.info(f"[FURNITURE_TOGGLE] 🎯 Callback: {query.data}")

    try:
        key = query.data.split(":")[1]
        logger.info(f"[FURNITURE_TOGGLE] ✅ Key: {key}")

        data = await state.get_data()
        selected = data.get('furniture', {})
        room = data.get('room')
        furniture_options = FURNITURE_BY_ROOM.get(room, {})

        if key in selected:
            del selected[key]
            action = "❌ УБРАНО"
        else:
            selected[key] = True
            action = "✅ ДОБАВЛЕНО"

        logger.info(f"[FURNITURE_TOGGLE] ✅ {action}")

        await state.update_data(furniture=selected)
        await show_furniture_screen(query.message, state)

        await query.answer()
        logger.info(f"[FURNITURE_TOGGLE] ✅ Answer отправлен (без уведомления)")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в toggle_furniture: {e}", exc_info=True)
        await query.answer(f"❌ Ошибка: {e}", show_alert=True)


@router.callback_query(F.data == "to_colors")
async def go_to_colors(query: types.CallbackQuery, state: FSMContext):
    """Переход к цветам"""

    logger.info(f"[GO_TO_COLORS] 🎯 Переходим к цветам")

    try:
        await query.answer()
        logger.info(f"[GO_TO_COLORS] ✅ Answer отправлен")

        from handlers.design_step2_colors import show_colors_screen
        logger.info(f"[GO_TO_COLORS] 📥 Импорт успешен")

        await show_colors_screen(query.message, state, step="walls")
        logger.info(f"[GO_TO_COLORS] ✅ Экран цветов показан")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в go_to_colors: {e}", exc_info=True)
        await query.answer(f"❌ Ошибка: {e}", show_alert=True)
