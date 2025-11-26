# handlers/design_step2_colors.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

router = Router()
logger = logging.getLogger(__name__)

logger.info("🔧 [design_step2_colors.py] Модуль загружен")


class ColorsState(StatesGroup):
    selecting = State()


WALL_COLORS = {
    'light_gray': ('💡', 'Светло-серый'),
    'white': ('⚪', 'Белый'),
    'soft_blue': ('🔵', 'Голубой'),
    'beige': ('🟨', 'Бежевый'),
    'light_green': ('🟢', 'Зелёный'),
    'pale_pink': ('🩷', 'Розовый'),
    'warm_gray': ('🩶', 'Серый'),
    'light_terracotta': ('🟠', 'Терракота'),
    'cream': ('💛', 'Кремовый'),
    'powder_blue': ('💙', 'Пудра'),
    'sage_green': ('🟩', 'Шалфей'),
    'soft_lavender': ('🟣', 'Лаванда'),
}

FLOOR_COLORS = {
    'light_oak': ('🟫', 'Светлый дуб'),
    'dark_oak': ('🟤', 'Тёмный дуб'),
    'gray_parquet': ('🩶', 'Серый'),
    'white_oak': ('⚪', 'Белый дуб'),
    'walnut': ('🟤', 'Орех'),
    'natural_pine': ('🟨', 'Сосна'),
    'ash': ('🩶', 'Ясень'),
    'cherry': ('🔴', 'Вишня'),
    'concrete': ('⚫', 'Бетон'),
    'light_laminat': ('💡', 'Ламинат'),
}

CEILING_COLORS = {
    'white': ('⚪', 'Белый'),
    'soft_gray': ('🩶', 'Серый'),
    'warm_white': ('💛', 'Тёплый'),
    'light_gray': ('💡', 'Светло-серый'),
    'natural_white': ('🤍', 'Натуральный'),
}


async def show_colors_screen(message: types.Message, state: FSMContext, step: str = "walls"):
    """Показывает экран цветов"""

    logger.info(f"[COLORS_SCREEN] 🎯 Шаг: {step}")

    try:
        data = await state.get_data()
        colors = data.get('colors', {})
        room = data.get('room')

        logger.info(f"[COLORS_SCREEN] ✅ Room: {room}, Colors: {colors}")

        if step == "walls":
            options = WALL_COLORS
            step_num = "1️⃣"
            step_name = "СТЕНЫ"
            next_step = "floor"
        elif step == "floor":
            options = FLOOR_COLORS
            step_num = "2️⃣"
            step_name = "ПОЛ"
            next_step = "ceiling"
        else:
            options = CEILING_COLORS
            step_num = "3️⃣"
            step_name = "ПОТОЛОК"
            next_step = "generate"

        logger.info(f"[COLORS_SCREEN] ✅ Options loaded: {len(options)}")

        text = f"🎨 <b>{room.upper()} - {step_num} ЦВЕТ {step_name}</b>\n\n"
        text += "✅ <b>ВЫБРАННЫЕ:</b>\n"

        if colors.get('walls'):
            emoji, label = WALL_COLORS.get(colors['walls'], ('❓', '?'))
            text += f"• 🧱 {label}\n"
        if colors.get('floor'):
            emoji, label = FLOOR_COLORS.get(colors['floor'], ('❓', '?'))
            text += f"• 🪵 {label}\n"
        if colors.get('ceiling'):
            emoji, label = CEILING_COLORS.get(colors['ceiling'], ('❓', '?'))
            text += f"• ☁️ {label}\n"
        if not colors:
            text += "Ещё ничего\n"
        text += "\n"

        buttons = []
        for key, (emoji, label) in options.items():
            current = colors.get(step)
            status = "✅" if current == key else "➕"
            buttons.append(
                types.InlineKeyboardButton(
                    text=f"{status} {emoji} {label}",
                    callback_data=f"col:{step}:{key}"
                )
            )

        logger.info(f"[COLORS_SCREEN] ✅ Created {len(buttons)} buttons")

        keyboard_buttons = [[btn] for btn in buttons]

        nav = []
        if next_step != "generate":
            nav.append(
                types.InlineKeyboardButton(
                    text=f"➡️ ДАЛЕЕ",
                    callback_data=f"col_step:{next_step}"
                )
            )
        else:
            nav.append(
                types.InlineKeyboardButton(
                    text="🎬 ГЕНЕРИРОВАТЬ",
                    callback_data="final:generate"
                )
            )

        nav.append(
            types.InlineKeyboardButton(text="↩️ К МЕБЕЛИ", callback_data="back_furniture")
        )

        keyboard_buttons.append(nav)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        logger.info(f"[COLORS_SCREEN] 📤 Отправляю сообщение")
        await message.edit_text(text, reply_markup=keyboard)
        logger.info(f"[COLORS_SCREEN] ✅ Сообщение отправлено")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в show_colors_screen: {e}", exc_info=True)


@router.callback_query(F.data.startswith("col:"))
async def toggle_color(query: types.CallbackQuery, state: FSMContext):
    """Toggle цвет"""

    logger.info(f"[COLOR_TOGGLE] 🎯 Callback: {query.data}")

    try:
        parts = query.data.split(":")
        step = parts[1]
        key = parts[2]

        logger.info(f"[COLOR_TOGGLE] ✅ Step: {step}, Key: {key}")

        data = await state.get_data()
        colors = data.get('colors', {})

        if colors.get(step) == key:
            del colors[step]
            action = "❌ УБРАНО"
        else:
            colors[step] = key
            action = "✅ ВЫБРАНО"

        logger.info(f"[COLOR_TOGGLE] ✅ {action}")

        await state.update_data(colors=colors)
        await show_colors_screen(query.message, state, step=step)

        options_map = {
            'walls': WALL_COLORS,
            'floor': FLOOR_COLORS,
            'ceiling': CEILING_COLORS,
        }
        emoji, label = options_map[step].get(key, ('❓', '?'))
        await query.answer(f"{action}: {label}", show_alert=False)
        logger.info(f"[COLOR_TOGGLE] ✅ Answer отправлен")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в toggle_color: {e}", exc_info=True)
        await query.answer(f"❌ Ошибка: {e}", show_alert=True)


@router.callback_query(F.data.startswith("col_step:"))
async def next_color_step(query: types.CallbackQuery, state: FSMContext):
    """Следующий шаг"""

    logger.info(f"[COL_STEP] 🎯 Callback: {query.data}")

    try:
        next_step = query.data.split(":")[1]
        logger.info(f"[COL_STEP] ✅ Next step: {next_step}")

        await show_colors_screen(query.message, state, step=next_step)
        await query.answer()
        logger.info(f"[COL_STEP] ✅ Переход выполнен")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в next_color_step: {e}", exc_info=True)
        await query.answer(f"❌ Ошибка: {e}", show_alert=True)


@router.callback_query(F.data == "back_furniture")
async def back_to_furniture(query: types.CallbackQuery, state: FSMContext):
    """Назад к мебели"""

    logger.info(f"[BACK_FURNITURE] 🎯 Возвращаемся к мебели")

    try:
        await query.answer("↩️ К мебели...")
        logger.info(f"[BACK_FURNITURE] ✅ Answer отправлен")

        from handlers.design_step1_furniture import show_furniture_screen
        logger.info(f"[BACK_FURNITURE] 📥 Импорт успешен")

        await show_furniture_screen(query.message, state)
        logger.info(f"[BACK_FURNITURE] ✅ Экран мебели показан")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в back_to_furniture: {e}", exc_info=True)
        await query.answer(f"❌ Ошибка: {e}", show_alert=True)


@router.callback_query(F.data == "final:generate")
async def final_generate(query: types.CallbackQuery, state: FSMContext):
    """Финальная генерация"""

    logger.info(f"[FINAL_GEN] 🎯 Начинаем генерацию")

    try:
        data = await state.get_data()
        logger.info(f"[FINAL_GEN] ✅ Data: {data}")

        await query.message.edit_text("🎬 Генерирую дизайн...\n⏳ Подождите...")
        logger.info(f"[FINAL_GEN] 📤 Сообщение о генерации отправлено")

        await query.answer("Генерируем!")
        logger.info(f"[FINAL_GEN] ✅ Answer отправлен")

    except Exception as e:
        logger.error(f"[ERROR] ❌ Ошибка в final_generate: {e}", exc_info=True)
        await query.answer(f"❌ Ошибка: {e}", show_alert=True)
