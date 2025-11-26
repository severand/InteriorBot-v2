# bot/services/replicate_api.py

import logging
import os

from config import config

logger = logging.getLogger(__name__)

# ===== ВЫБОР МОДЕЛИ =====
# True = DALL-E 3 (Replicate), False = SD 3.5 Large
USE_DALLE3_REPLICATE = True  # ← НОВАЯ ВЕРСИЯ!

logger.info(
    f"🎨 ИСПОЛЬЗУЕТСЯ МОДЕЛЬ: {'DALL-E 3 (Replicate)' if USE_DALLE3_REPLICATE else 'Stable Diffusion 3.5 Large'}")

# ===== STYLE DESCRIPTIONS ДЛЯ DALLE-3 =====
STYLE_DESCRIPTIONS_DALLE3 = {
    'modern': '''
    Modern minimalist style with clean geometric lines, contemporary furniture, 
    neutral color palette (whites, greys, beiges), minimal decorations, 
    functional design, sleek surfaces, modern lighting fixtures.
    ''',
    'minimalist': '''
    Minimalist design with extreme simplicity, uncluttered spaces, 
    white and grey color scheme, functional every element, 
    zen aesthetic, maximum negative space, barely any decorations.
    ''',
    'scandinavian': '''
    Scandinavian interior with light wood furniture, natural materials, 
    white and light grey walls, plenty of natural daylight, 
    cozy atmosphere, minimalist yet warm, functional beauty.
    ''',
    'industrial': '''
    Industrial loft style with exposed brick walls, metal fixtures and pipes, 
    concrete floors, high ceilings, raw materials, 
    vintage industrial elements, open floor plan, urban aesthetic.
    ''',
    'rustic': '''
    Rustic cozy interior with natural wood beams, warm earthy tones, 
    stone accents, vintage wooden furniture, cottage-like atmosphere, 
    warm lighting, traditional craftsmanship, natural materials.
    ''',
    'japandi': '''
    Japandi style blending Japanese minimalism with Scandinavian simplicity, 
    natural wood elements, zen aesthetic, clean lines, 
    warm neutral colors, balanced emptiness and function, 
    peaceful and harmonious atmosphere.
    ''',
    'boho': '''
    Bohemian eclectic style with colorful layered patterns, 
    plants and greenery, vintage decorations and textiles, 
    natural materials, artistic elements, warm lighting, 
    free-spirited and worldly atmosphere.
    ''',
    'mediterranean': '''
    Mediterranean style with terracotta and warm ochre tones, 
    blue and white accents, natural stone and clay materials, 
    arched doorways, warm sunlight, rustic charm, 
    inviting and warm aesthetic inspired by coastal regions.
    ''',
    'midcentury': '''
    Mid-century modern design with retro furniture from 1950s-60s, 
    organic shapes and curves, warm wood tones, iconic design pieces, 
    subtle color palette, timeless elegance, nostalgic yet sophisticated.
    ''',
    'artdeco': '''
    Art Deco glamorous style with geometric patterns and symmetry, 
    luxurious materials like marble and brass, bold jewel tones, 
    ornamental details, dramatic lighting, sophisticated and lavish atmosphere.
    ''',
}

# ===== STYLE PROMPTS SD 3.5 (СТАРЫЕ) =====
STYLE_PROMPTS_SD35 = {
    'modern': 'modern minimalist interior design, clean lines, neutral colors, contemporary furniture, professional architectural photography, 4K, realistic',
    'minimalist': 'minimalist interior, simple forms, functional space, uncluttered, zen aesthetic, white and grey palette, professional, 4K, realistic',
    'scandinavian': 'Scandinavian interior design, light wood furniture, white walls, natural daylight, cozy and warm, professional, 4K, realistic',
    'industrial': 'industrial loft interior, exposed brick walls, metal fixtures, concrete floors, open space, professional, 4K, realistic',
    'rustic': 'rustic cozy interior, natural wood beams, warm earthy tones, stone accents, cottage style, professional, 4K, realistic',
    'japandi': 'Japandi interior design, Japanese minimalism meets Scandinavian style, wood elements, zen, professional, 4K, realistic',
    'boho': 'bohemian interior, colorful layered patterns, plants, vintage decorations, eclectic style, professional, 4K, realistic',
    'mediterranean': 'Mediterranean interior design, terracotta tones, blue and white accents, natural materials, warm and inviting, professional, 4K, realistic',
    'midcentury': 'mid-century modern interior, retro furniture, organic shapes, warm wood tones, professional, 4K, realistic',
    'artdeco': 'Art Deco interior design, geometric patterns, luxurious materials, bold colors, glamorous style, professional, 4K, realistic',
}

# ===== ROOM DESCRIPTIONS =====
ROOM_DESCRIPTIONS = {
    'living_room': 'spacious living room area with seating',
    'bedroom': 'comfortable bedroom space with bed',
    'kitchen': 'functional kitchen with cooking area',
    'bathroom': 'modern bathroom with fixtures',
    'office': 'home office workspace with desk',
    'dining_room': 'dining area with table',
    'entrance': 'narrow entrance hallway, approximately 2m wide and 3m long',
    'wardrobe': 'closet or storage space',
    'kids_room': 'children\'s bedroom',
    'toilet': 'small toilet room',
    'balcony': 'apartment balcony or terrace',
    'manroom': 'man cave or lounge space',
}

# ===== ROOM PROMPTS SD 3.5 (СТАРЫЕ) =====
ROOM_PROMPTS_SD35 = {
    'living_room': 'spacious living room',
    'bedroom': 'bedroom',
    'kitchen': 'kitchen interior',
    'bathroom': 'modern bathroom',
    'office': 'home office workspace',
    'dining_room': 'dining room',
    'entrance': 'narrow entrance hallway',
    'wardrobe': 'closet storage space',
    'kids_room': 'children bedroom',
    'toilet': 'small toilet room',
    'balcony': 'apartment balcony',
    'manroom': 'man cave lounge',
}


# ===== DALLE-3 (REPLICATE) PROMPT =====
def get_dalle3_replicate_prompt(style: str, room: str) -> str:
    """
    Генерирует СУПЕР-ДЕТАЛЬНЫЙ промт для DALL-E 3 на Replicate
    """
    style_desc = STYLE_DESCRIPTIONS_DALLE3.get(style, STYLE_DESCRIPTIONS_DALLE3['modern']).strip()
    room_desc = ROOM_DESCRIPTIONS.get(room, room.replace('_', ' '))

    prompt = f"""
    Interior design photograph of a {room_desc}.

    STYLE: {style_desc}

   You are a Russian architect with world-class training.
You are a super designer who understands everything a Russian client wants.
Create a design that meets these requirements!

SETTING: Residential apartment, practical modern design.

LIGHTING: Soft, balanced natural and artificial lighting, without harsh shadows,
realistic daylight, professional photography lighting.

COLOR PALETTE: Harmonious, not oversaturated, delicate and refined colors,
warm shades, realistic interior colors, sophisticated mood.

DETAILS: Professional architectural interior photography, high quality,
good composition, magazine-worthy, realistic proportions and perspective,
attention to design detail, obvious practicality.

MOOD: Sophisticated, cozy, professional, thoughtful,
livable and functional, beautiful yet practical.

PHOTOGRAPHY: Shot by a professional interior designer photographer,
studio lighting, perfect exposure, sharp focus,
photography for a premium interior design magazine,
realistic rendering, no artificial effects.

NO: No cartoonish style, no unrealistic colors, no oversaturation,
no harsh lighting, no amateur photography, no cluttered spaces,
no overstuffed elements, only realism and professionalism.
    """

    return prompt.strip()


# ===== SD 3.5 PROMPT (СТАРОЕ) =====
def get_sd35_prompt(style: str, room: str) -> str:
    """
    Генерирует промт для Stable Diffusion 3.5 Large (СТАРАЯ ВЕРСИЯ)
    """
    style_desc = STYLE_PROMPTS_SD35.get(style, STYLE_PROMPTS_SD35['modern'])
    room_name = ROOM_PROMPTS_SD35.get(room, room.replace('_', ' '))

    prompt = f"""
    {room_name} interior design in {style_desc} style.
    Russian apartment setting, practical and functional design.
    Soft natural lighting, balanced colors, realistic mood.
    Professional interior design magazine photography.
    High quality, well-lit, realistic.
    """

    return prompt.strip()


# ===== MAIN GENERATE FUNCTION =====
async def generate_image(photo_file_id: str, room: str, style: str, bot_token: str) -> str | None:
    """
    Главная функция генерации изображения.
    Использует DALL-E 3 (Replicate) или SD 3.5 в зависимости от USE_DALLE3_REPLICATE
    """

    if USE_DALLE3_REPLICATE:
        return await generate_dalle3_replicate(room, style)
    else:
        return await generate_sd35(room, style)



# ===== DALL-E 3 (REPLICATE) GENERATE =====
async def generate_dalle3_replicate(room: str, style: str) -> str | None:
    """
    Генерирует изображение используя DALL-E 3 на Replicate
    ✅ ОБХОДИТ ГЕОГРАФИЧЕСКИЕ БЛОКИРОВКИ!
    """
    if not config.REPLICATE_API_TOKEN:
        logger.error("❌ REPLICATE_API_TOKEN не установлен в .env")
        return None

    try:
        import replicate
        os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN

        prompt = get_dalle3_replicate_prompt(style, room)
        logger.info(f"🎨 DALL-E 3 (Replicate): {room} → {style}")
        logger.debug(f"📝 Промт длина: {len(prompt)} символов")

        # ✅ DALL-E 3 НА REPLICATE
        output = replicate.run(
            "openai/dall-e-3",
            input={
                "prompt": prompt,
                "size": "1024x1024",
            }
        )

        logger.debug(f"🔍 Output type: {type(output)}, value: {output}")

        # ✅ ИСПРАВКА: Проверяем тип и извлекаем URL
        if output:
            # Если это список объектов FileOutput
            if isinstance(output, list) and len(output) > 0:
                file_obj = output[0]
                if hasattr(file_obj, 'url'):
                    image_url = file_obj.url  # ← Получаем .url из объекта
                else:
                    image_url = str(file_obj)  # ← Или просто конвертируем в строку
            # Если это один объект FileOutput
            elif hasattr(output, 'url'):
                image_url = output.url  # ← Получаем .url из объекта
            else:
                image_url = str(output)  # ← Или просто конвертируем в строку

            logger.info(f"✅ DALL-E 3 готово!")
            logger.debug(f"📸 Image URL: {image_url}")
            return image_url
        else:
            logger.error("❌ Пустой ответ от DALL-E 3 (Replicate)")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка DALL-E 3 (Replicate): {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ===== SD 3.5 LARGE GENERATE (СТАРАЯ ВЕРСИЯ) =====
async def generate_sd35(room: str, style: str) -> str | None:
    """
    Генерирует изображение используя Stable Diffusion 3.5 Large
    (РЕЗЕРВНАЯ ВЕРСИЯ)
    """
    if not config.REPLICATE_API_TOKEN:
        logger.warning("⚠️ REPLICATE_API_TOKEN не установлен")
        return None

    try:
        import replicate
        os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN

        prompt = get_sd35_prompt(style, room)
        logger.info(f"🎨 SD 3.5 Large: {room} → {style}")

        output = replicate.run(
            "stability-ai/stable-diffusion-3.5-large",
            input={
                "prompt": prompt,
                "cfg": 5.5,
                "steps": 50,
                "width": 1024,
                "height": 1024,
                "negative_prompt": "oversaturated, high contrast, harsh lighting, unrealistic",
                "aspect_ratio": "1:1",
                "output_format": "webp",
                "output_quality": 85,
            }
        )

        if output:
            try:
                image_url = output.url()
                logger.info(f"✅ SD 3.5 готово: {image_url[:50]}...")
                return image_url
            except:
                return str(output)
        return None

    except Exception as e:
        logger.error(f"❌ Ошибка SD 3.5: {e}")
        return None
