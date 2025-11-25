# bot/utils/navigation.py

from aiogram.types import CallbackQuery, InlineKeyboardMarkup


async def edit_menu(
    callback: CallbackQuery,
    message_id: int,
    text: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    """
    Редактирует СУЩЕСТВУЮЩЕЕ сообщение меню (НЕ создает новое).

    Это главный принцип навигации:
    - Одно сообщение меню
    - Только его редактируем, не создаём новые
    - Пользователь видит "плавный" переход между экранами
    """
    if not message_id:
        print("[navigation.edit_menu] Ошибка: message_id is None!")
        return

    try:
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"[navigation.edit_menu] Ошибка при редактировании сообщения {message_id}: {e}")

    # Удаляем "крутящееся" состояние кнопки (не оставляем "часики")
    await callback.answer()
