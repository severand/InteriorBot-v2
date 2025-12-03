# --- Новый файл: bot/utils/helpers.py ---
import asyncio
import logging

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

# Ключ для хранения ID Пина
NAV_MSG_ID_KEY = "navigation_message_id"


def format_balance_footer(balance: int) -> str:
    """
    Форматирует футер с балансом генераций для добавления в конец любого сообщения
    
    Args:
        balance: Количество доступных генераций
        
    Returns:
        Отформатированная строка с балансом
    """
    return f"\n\n━━━━━━━━━━━━━━━━\n💰 **Доступно генераций:** {balance}"


def format_message_with_balance(text: str, balance: int) -> str:
    """
    Добавляет футер с балансом к существующему тексту сообщения
    
    Args:
        text: Основной текст сообщения
        balance: Количество доступных генераций
        
    Returns:
        Текст с добавленным футером баланса
    """
    return text + format_balance_footer(balance)


async def delete_message_after_delay(message: Message, delay: int = 3):
    """
    Удаляет сообщение через указанное количество секунд.
    """
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить временное сообщение (ID: {message.message_id}): {e}")


async def edit_nav_message(bot, chat_id, state: FSMContext, text: str, reply_markup=None):
    """
    Универсальная функция для редактирования навигационного сообщения (Пина).
    Возвращает True, если редактирование прошло успешно.
    """
    data = await state.get_data()
    nav_msg_id = data.get(NAV_MSG_ID_KEY)

    if nav_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=nav_msg_id,
                text=text,
                reply_markup=reply_markup,  # Здесь может быть InlineKeyboardMarkup, если нужно
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except TelegramBadRequest as e:
            logger.warning(f"Ошибка редактирования Пина (ID:{nav_msg_id}): {e}")

    # Если редактирование не удалось, это должно быть исправлено в хэндлере,
    # который должен отправить новое сообщение и сохранить его ID.
    return False
