# bot/services/replicate_api.py

import logging
import os
import tempfile
import time
from typing import Optional

import aiohttp
import replicate

from config import config

logger = logging.getLogger(__name__)

# ===== CONSTANTS =====
TELEGRAM_FILE_URL = "https://api.telegram.org/file/bot{bot_token}/{file_id}"
REPLICATE_MODEL = "google/nano-banana"

# ===== ROOM DESCRIPTIONS =====
ROOM_DESCRIPTIONS = {
    'living_room': 'spacious living room',
    'bedroom': 'comfortable bedroom',
    'kitchen': 'functional kitchen',
    'bathroom': 'modern bathroom',
    'office': 'home office workspace',
    'dining_room': 'dining area',
    'entrance': 'entrance hallway',
    'wardrobe': 'closet space',
    'kids_room': 'children bedroom',
    'toilet': 'small toilet room',
    'balcony': 'apartment balcony',
    'manroom': 'man cave lounge',
}

# ===== CUSTOM PROMPT =====
# Редактируй этот промпт по своему желанию
# room и style будут автоматически добавлены в конец
CUSTOM_PROMPT = """

You are a world-renowned professional interior designer.

You know all the latest trends in interior design, from basements to ducal villas. You create masterpieces for everyday people.

Your goal is to create a simple, modern, yet practical design for your client.

You select furniture, interiors, paint colors, and lighting based on the chosen space and style.

You detail every detail in the interior so that the client says, "WOW, that's exactly what I need."

Prohibited:
1. Carpets on the floor

"""


# ===== HELPER FUNCTIONS =====
def _build_full_prompt(custom_prompt: str, room: str, style: str) -> str:
    """
    Строит финальный промпт: CUSTOM_PROMPT + room + style

    Args:
        custom_prompt: Кастомный промпт (твои особенности)
        room: Тип комнаты
        style: Стиль дизайна

    Returns:
        Готовый промпт для генерации
    """
    room_desc = ROOM_DESCRIPTIONS.get(room, room.replace('_', ' '))

    # Убираем лишние пробелы и переносы строк
    custom_part = custom_prompt.strip()

    # Собираем финальный промпт: твой текст + room + style
    full_prompt = f"{custom_part}\nRoom type: {room_desc}\nDesign style: {style}"

    return full_prompt


async def _download_telegram_photo(bot_token: str, file_id: str) -> Optional[bytes]:
    """
    Скачивает фото из Telegram

    Args:
        bot_token: Токен Telegram бота
        file_id: ID файла в Telegram

    Returns:
        Байты изображения или None при ошибке
    """
    url = TELEGRAM_FILE_URL.format(bot_token=bot_token, file_id=file_id)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f"❌ Не удалось скачать фото: HTTP {resp.status}")
                    return None
                return await resp.read()
    except Exception as e:
        logger.error(f"❌ Ошибка при скачивании фото: {e}")
        return None


def _save_temp_file(data: bytes) -> Optional[str]:
    """
    Сохраняет данные во временный файл

    Args:
        data: Байты для сохранения

    Returns:
        Путь к временному файлу или None при ошибке
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(data)
            return tmp_file.name
    except Exception as e:
        logger.error(f"❌ Ошибка создания временного файла: {e}")
        return None


def _cleanup_temp_file(file_path: str) -> None:
    """Удаляет временный файл"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить временный файл {file_path}: {e}")


def _extract_image_url(output) -> Optional[str]:
    """
    Извлекает URL изображения из ответа Replicate

    Args:
        output: Ответ от Replicate API

    Returns:
        URL изображения или None
    """
    if not output:
        return None

    # Проверяем различные форматы ответа
    if hasattr(output, 'url'):
        return output.url
    elif isinstance(output, str):
        return output
    elif isinstance(output, list) and output:
        return str(output[0])
    else:
        return str(output)


# ===== MAIN GENERATE FUNCTION =====
async def generate_image(
    photo_file_id: Optional[str],
    room: str,
    style: str,
    bot_token: str
) -> Optional[str]:
    """
    Генерирует изображение используя Google Nano Banana

    Args:
        photo_file_id: ID файла фотографии в Telegram (None = text-to-image режим)
        room: Тип комнаты
        style: Стиль дизайна
        bot_token: Токен Telegram бота

    Returns:
        URL сгенерированного изображения или None при ошибке
    """

    # Проверка API токена
    if not config.REPLICATE_API_TOKEN:
        logger.error("❌ REPLICATE_API_TOKEN не установлен в .env")
        return None

    # Устанавливаем токен в окружение
    os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN

    # Подготовка промпта: CUSTOM_PROMPT + room + style
    prompt = _build_full_prompt(CUSTOM_PROMPT, room, style)

    start_time = time.time()
    tmp_file_path: Optional[str] = None

    try:
        if photo_file_id:
            # ===== IMAGE-TO-IMAGE MODE =====
            logger.info(f"🎨 Nano Banana (Image-to-Image): {room} → {style}")
            logger.debug(f"📝 Промпт: {prompt}")

            # Скачиваем фото
            photo_data = await _download_telegram_photo(bot_token, photo_file_id)
            if not photo_data:
                return None

            # Сохраняем во временный файл
            tmp_file_path = _save_temp_file(photo_data)
            if not tmp_file_path:
                return None

            # Генерируем изображение
            with open(tmp_file_path, 'rb') as img_file:
                output = replicate.run(
                    REPLICATE_MODEL,
                    input={
                        "prompt": prompt,
                        "image_input": [img_file]
                    }
                )
        else:
            # ===== TEXT-TO-IMAGE MODE =====
            logger.info(f"🎨 Nano Banana (Text-to-Image): {room} → {style}")
            logger.debug(f"📝 Промпт: {prompt}")

            output = replicate.run(
                REPLICATE_MODEL,
                input={"prompt": prompt}
            )

        # Извлекаем URL из ответа
        image_url = _extract_image_url(output)

        if image_url:
            elapsed_time = time.time() - start_time
            logger.info(f"✅ Nano Banana готово за {elapsed_time:.2f}с")
            logger.debug(f"📸 Image URL: {image_url}")
            return image_url
        else:
            logger.error("❌ Пустой ответ от Nano Banana")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка Nano Banana: {e}")
        logger.exception("Полный traceback:")
        return None

    finally:
        # Всегда очищаем временный файл
        if tmp_file_path:
            _cleanup_temp_file(tmp_file_path)
