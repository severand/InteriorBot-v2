# bot/services/replicate_api.py
# ===== ВЫБОР МОДЕЛИ =====
# True = DALL-E 3 (Replicate), False = SD 3.5 Large
# https://replicate.com/openai/dall-e-3
# новая моделb:
# interior-design https://replicate.com/adirik/interior-design?prediction=dh7semz89drma0ctrne94ha4y4
# https://huggingface.co/SG161222/Realistic_Vision_V3.0_VAE/tree/main
# interior-design-sdxl-lightning - https://replicate.com/rocketdigitalai/interior-design-sdxl-lightning?prediction=dzkrvgvhksrj00ctrn1rhr5mfc
# interior-design-v2 - https://replicate.com/adirik/interior-design-v2?prediction=4bx2x1463srma0ctrn3abe6484
# sdxl - https://replicate.com/lucataco/sdxl?prediction=hd0cj5yw01rm80ctrnary3gvvr
#  stabledesign_interiordesign - https://replicate.com/melgor/stabledesign_interiordesign?prediction=0aqm3rfwmsrmc0ctpy7tq5d3em
#  interior-design-sdxl - https://replicate.com/rocketdigitalai/interior-design-sdxl?prediction=v1h6crggk9rj00ctpy3rm85eym


# bot/services/replicate_api.py

import logging
import os
from typing import Optional

from config import config

logger = logging.getLogger(__name__)

# ===== СИСТЕМА ВЫБОРА МОДЕЛИ (TRUE/FALSE) =====

# 🎯 ВЫБЕРИТЕ ТОЛЬКО ОДНУ МОДЕЛЬ (остальные должны быть False):
USE_DALLE3 = False  # DALL-E 3 (text-to-image, без входного фото)
USE_SD35 = False  # Stable Diffusion 3.5 Large (text-to-image)
USE_NANO_BANANA = True  # Google Nano Banana (универсальная)

# 🔧 РЕЖИМ NANO BANANA (работает только если USE_NANO_BANANA = True):
NANO_TEXT_TO_IMAGE = True  # True = генерация с нуля, False = трансформация фото


# ===== ВАЛИДАЦИЯ НАСТРОЕК =====
def _validate_model_selection():
    """Проверяет что выбрана только одна модель"""
    active_models = sum([USE_DALLE3, USE_SD35, USE_NANO_BANANA])

    if active_models == 0:
        logger.error("❌ ОШИБКА: Не выбрана ни одна модель! Установите одну из USE_* = True")
        raise ValueError("Не выбрана модель для генерации")

    if active_models > 1:
        logger.error("❌ ОШИБКА: Выбрано несколько моделей! Только одна должна быть True")
        raise ValueError("Выбрано больше одной модели")

    # Логируем активную модель
    if USE_DALLE3:
        logger.info("🎨 АКТИВНАЯ МОДЕЛЬ: DALL-E 3 (text-to-image)")
    elif USE_SD35:
        logger.info("🎨 АКТИВНАЯ МОДЕЛЬ: Stable Diffusion 3.5 Large")
    elif USE_NANO_BANANA:
        mode = "TEXT-TO-IMAGE" if NANO_TEXT_TO_IMAGE else "IMAGE-TO-IMAGE"
        logger.info(f"🎨 АКТИВНАЯ МОДЕЛЬ: Google Nano Banana ({mode})")


# Проверяем при загрузке модуля
_validate_model_selection()

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

# ===== NANO BANANA TEXT-TO-IMAGE PROMPTS =====
STYLE_PROMPTS_NANO_TEXT2IMG = {
    'modern': '''
    Create a modern minimalist interior design photograph.
    Clean geometric lines, contemporary furniture with sleek surfaces.
    Neutral sophisticated color palette: pristine whites, soft greys, warm beiges, occasional black accents.
    Minimal decorations, every element serves a purpose.
    Modern LED lighting fixtures with indirect illumination.
    High-quality materials: polished concrete, glass, brushed metal, smooth wood.
    Open space planning, uncluttered surfaces, geometric shapes.
    Large windows with natural daylight, simple window treatments.
    Professional architectural photography, magazine quality.
    Sophisticated, practical, elegant atmosphere.
    Russian apartment standards: functional and beautiful.
    Photorealistic rendering, natural lighting, perfect composition.
    ''',

    'minimalist': '''
    Create a pure minimalist interior design photograph.
    Extreme simplicity, zen aesthetic, maximum negative space.
    Color scheme: pristine white walls, light grey accents, occasional matte black.
    Every element is essential and functional, nothing extra.
    Simple geometric furniture, clean lines, unobstructed surfaces.
    Hidden storage solutions, seamless built-ins.
    Natural light emphasis through large windows, minimal artificial lighting.
    Materials: white plaster, light wood, glass, simple fabrics.
    Calm, meditative, breathable space with perfect balance.
    Professional architectural photography, minimalist composition.
    Russian apartment: practical minimalism without coldness.
    Photorealistic, natural lighting, serene atmosphere.
    ''',

    'scandinavian': '''
    Create a Scandinavian (Nordic) interior design photograph.
    Light natural wood furniture: birch, pine, oak with organic textures.
    White and light grey walls, maximized natural daylight through large windows.
    Cozy hygge atmosphere with soft textiles and warm ambient lighting.
    Minimalist yet warm, functional beauty with personality.
    Indoor plants in simple pots, simple decorations, open shelving.
    Natural materials: light wood, linen, wool, leather, cotton.
    Neutral color palette with occasional pastels or muted colors.
    Inviting, comfortable, lived-in feeling without clutter.
    Professional interior photography, warm and welcoming.
    Russian apartment: Scandi style adapted for comfort.
    Photorealistic rendering, natural soft lighting, cozy mood.
    ''',

    'industrial': '''
    Create an industrial loft style interior photograph.
    Exposed red brick or grey brick walls, raw concrete surfaces.
    Visible metal elements: black steel pipes, ducts, beams, frames.
    High ceilings, open floor plan, warehouse aesthetic.
    Raw unfinished materials combined with modern comfort.
    Utilitarian furniture: metal shelving, reclaimed wood tables, leather seating.
    Vintage industrial elements: factory pendant lights, metal lockers, gears.
    Urban warehouse atmosphere, edgy yet livable.
    Edison bulbs, track lighting, exposed filaments, metal fixtures.
    Large factory-style windows, natural daylight.
    Professional architectural photography, dramatic lighting.
    Russian loft apartment: industrial style with warmth.
    Photorealistic, moody lighting, authentic industrial feel.
    ''',

    'rustic': '''
    Create a rustic cozy cottage interior photograph.
    Natural wood beams on ceiling, warm earthy color palette.
    Stone or brick fireplace accent wall, vintage wooden furniture with patina.
    Cottage-like atmosphere with traditional craftsmanship details.
    Warm ambient lighting: lantern-style fixtures, warm LED, candles.
    Natural materials: reclaimed wood, natural stone, wrought iron, clay.
    Comfortable textiles: linen, wool, cotton in warm tones.
    Homey decorations: vintage finds, handmade items, family heirlooms.
    Inviting countryside retreat feeling, lived-in charm.
    Professional interior photography, warm cozy lighting.
    Russian dacha style meets modern comfort.
    Photorealistic rendering, golden hour lighting, welcoming atmosphere.
    ''',

    'japandi': '''
    Create a Japandi fusion style interior photograph.
    Blend of Japanese minimalism with Scandinavian warmth and functionality.
    Natural wood elements in light honey tones, clean architectural lines.
    Zen aesthetic with wabi-sabi imperfection and Scandi practicality.
    Warm neutral colors: beige, sand, soft grey, natural wood, cream.
    Balance between emptiness (Japanese ma) and cozy functionality (Scandi hygge).
    Low-profile furniture, natural materials, simple organic forms.
    Peaceful, harmonious, meditative atmosphere.
    Indoor plants: bonsai, simple greenery in ceramic pots.
    Paper lanterns or simple pendant lights, soft ambient lighting.
    Tatami-inspired elements mixed with Scandi textiles.
    Professional interior photography, serene composition.
    Russian apartment: East meets North in practical harmony.
    Photorealistic, natural soft lighting, calm zen mood.
    ''',

    'boho': '''
    Create a bohemian eclectic interior photograph.
    Layer upon layer of colorful patterns: textiles, rugs, cushions, wall hangings.
    Abundant plants and greenery throughout: hanging plants, potted palms, succulents.
    Vintage and global decorations: macramé wall hangings, woven baskets, ethnic art.
    Mix of natural materials: rattan furniture, jute rugs, wood, ceramics.
    Artistic elements: gallery wall with mixed frames, unique finds, treasures.
    Warm ambient lighting: string lights, Moroccan lanterns, candles.
    Free-spirited, worldly, creative atmosphere with personality.
    Rich color palette: terracotta, mustard, teal, burgundy, natural tones.
    Cozy maximalist vibe without overwhelming chaos.
    Professional interior photography, vibrant but balanced.
    Russian bohemian apartment: artistic and lived-in.
    Photorealistic, warm golden lighting, inviting eclectic mood.
    ''',

    'mediterranean': '''
    Create a Mediterranean coastal interior photograph.
    Warm terracotta and ochre wall tones, sun-baked earth colors.
    Blue and white accents inspired by sea and sky: cobalt, azure, cream.
    Natural materials: natural stone, clay tiles, weathered wood, wrought iron.
    Arched doorways or window frames with rustic charm.
    Warm sunlight atmosphere, golden hour glow, rustic elegance.
    Textured plaster walls with imperfect stucco effect.
    Decorative elements: ceramic pottery, terracotta planters, woven baskets.
    Mediterranean plants: olive branches, lavender, citrus in pots.
    Inviting, warm, vacation-like aesthetic, coastal breeze feeling.
    Professional interior photography, sun-drenched composition.
    Russian apartment: Mediterranean dream adapted for comfort.
    Photorealistic rendering, warm natural lighting, sunny relaxed mood.
    ''',

    'midcentury': '''
    Create a mid-century modern interior design photograph.
    Retro furniture from 1950s-60s era: iconic Eames, Saarinen, Noguchi pieces.
    Organic shapes and curves, tapered wooden legs, sculptural forms.
    Warm wood tones: walnut, teak, rosewood with natural grain.
    Vibrant accent colors: mustard yellow, burnt orange, teal, olive green.
    Geometric patterns on textiles and wall art, atomic age decorations.
    Sunburst clocks, starburst mirrors, abstract artwork, vinyl records.
    Clean lines with playful retro personality and optimism.
    Nostalgic yet sophisticated, timeless elegance, Mad Men aesthetic.
    Period-appropriate lighting: Sputnik chandeliers, arc floor lamps, pendant lights.
    Professional interior photography, vintage yet fresh feel.
    Russian apartment: mid-century style with modern comfort.
    Photorealistic rendering, warm nostalgic lighting, sophisticated retro mood.
    ''',

    'artdeco': '''
    Create an Art Deco glamorous interior photograph.
    Geometric patterns and symmetrical designs: zigzags, chevrons, sunbursts.
    Luxurious materials: white marble, polished brass, gold accents, large mirrors.
    Bold jewel tones: emerald green, sapphire blue, ruby red, amethyst purple, gold.
    Ornamental details: decorative moldings, elegant curves, stepped forms.
    Dramatic lighting: crystal chandeliers, wall sconces, statement fixtures.
    High-end finishes: lacquered surfaces, polished wood, velvet upholstery.
    Opulent textiles: silk, velvet, satin with geometric patterns.
    Sophisticated and lavish atmosphere, 1920s-30s Hollywood glamour.
    Mirrored surfaces, glossy finishes, metallic accents everywhere.
    Professional interior photography, dramatic luxurious composition.
    Russian luxury apartment: Art Deco elegance and grandeur.
    Photorealistic rendering, dramatic lighting, opulent sophisticated mood.
    ''',
}

# ===== NANO BANANA IMAGE-TO-IMAGE PROMPTS =====
STYLE_PROMPTS_NANO_IMG2IMG = {
    'modern': '''
    Transform this room into modern minimalist interior design.
    Use clean geometric lines, contemporary furniture with sleek surfaces.
    Apply neutral color palette: whites, soft greys, warm beiges.
    Minimal decorations, functional design elements.
    Add modern LED lighting fixtures and indirect illumination.
    Create sophisticated, uncluttered space with practical elegance.
    Keep the original room layout and architectural features.
    Make the scene natural, realistic, and professionally designed.
    ''',

    'minimalist': '''
    Redesign this room in pure minimalist style.
    Extreme simplicity, maximum negative space, zen aesthetic.
    Color scheme: pristine white, light grey, occasional black accents.
    Every element must be functional and essential.
    Remove all unnecessary decorations and clutter.
    Simple geometric furniture, clean lines, unobstructed surfaces.
    Natural light emphasis, minimal artificial lighting.
    Create calm, meditative, breathable space.
    Keep original room proportions. Make the scene natural.
    ''',

    'scandinavian': '''
    Transform this room into Scandinavian (Nordic) interior design.
    Light natural wood furniture (birch, pine, oak), organic textures.
    White and light grey walls, maximized natural daylight.
    Cozy hygge atmosphere with soft textiles and warm lighting.
    Minimalist yet warm, functional beauty with personality.
    Add indoor plants, simple decorations, practical storage.
    Use natural materials: wood, linen, wool, leather.
    Create inviting, comfortable, lived-in feeling.
    Preserve room layout. Make the scene natural and realistic.
    ''',

    'industrial': '''
    Convert this room into industrial loft style interior.
    Expose brick walls (red or grey brick), concrete surfaces.
    Visible metal fixtures: pipes, ducts, beams, steel frames.
    High ceilings if possible, open floor plan aesthetic.
    Raw unfinished materials, utilitarian furniture.
    Vintage industrial elements: factory lights, metal shelving.
    Urban warehouse atmosphere, edgy and modern.
    Add Edison bulbs, track lighting, metal accents.
    Keep original room structure. Make the scene natural and authentic.
    ''',

    'rustic': '''
    Redesign this room in rustic cozy cottage style.
    Natural wood beams on ceiling, warm earthy color tones.
    Stone or brick accents, vintage wooden furniture with patina.
    Cottage-like atmosphere, traditional craftsmanship details.
    Warm ambient lighting with lantern-style fixtures.
    Natural materials: reclaimed wood, stone, wrought iron.
    Comfortable textiles, homey decorations, lived-in charm.
    Create inviting countryside retreat feeling.
    Maintain room layout. Make the scene natural and welcoming.
    ''',

    'japandi': '''
    Transform this room into Japandi fusion style.
    Blend Japanese minimalism with Scandinavian warmth.
    Natural wood elements in light tones, clean architectural lines.
    Zen aesthetic with functional Scandi practicality.
    Warm neutral colors: beige, sand, soft grey, natural wood.
    Balance between emptiness (ma) and cozy functionality.
    Low furniture profiles, natural materials, simple forms.
    Peaceful, harmonious, meditative atmosphere.
    Indoor plants, paper lanterns, minimal decorations.
    Keep room proportions. Make the scene natural and serene.
    ''',

    'boho': '''
    Redesign this room in bohemian eclectic style.
    Layer colorful patterns: textiles, rugs, cushions, wall hangings.
    Abundant plants and greenery throughout the space.
    Vintage and global decorations: macramé, woven baskets, art.
    Mix of natural materials: rattan, jute, wood, ceramics.
    Artistic elements, gallery wall, unique finds and treasures.
    Warm ambient lighting with string lights and lanterns.
    Free-spirited, worldly, creative atmosphere.
    Create cozy maximalist vibe with personality.
    Preserve room layout. Make the scene natural and vibrant.
    ''',

    'mediterranean': '''
    Convert this room into Mediterranean coastal interior.
    Terracotta and warm ochre wall tones, sun-baked earth colors.
    Blue and white accents inspired by sea and sky.
    Natural materials: stone, clay, weathered wood, wrought iron.
    Arched doorways or window frames if architecturally possible.
    Warm sunlight atmosphere, rustic charm with elegance.
    Textured walls (stucco effect), decorative tiles, pottery.
    Inviting, warm, vacation-like aesthetic.
    Keep room structure. Make the scene natural and sunny.
    ''',

    'midcentury': '''
    Transform this room into mid-century modern design.
    Retro furniture from 1950s-60s era: iconic classic pieces.
    Organic shapes and curves, tapered wooden legs.
    Warm wood tones (walnut, teak), vibrant accent colors.
    Geometric patterns, atomic age decorations.
    Sunburst clocks, starburst mirrors, vintage artwork.
    Clean lines with playful retro personality.
    Nostalgic yet sophisticated, timeless elegance.
    Add period-appropriate lighting fixtures.
    Maintain room layout. Make the scene natural and authentic.
    ''',

    'artdeco': '''
    Redesign this room in Art Deco glamorous style.
    Geometric patterns and symmetrical designs everywhere.
    Luxurious materials: marble, brass, gold accents, mirrors.
    Bold jewel tones: emerald green, sapphire blue, ruby red.
    Ornamental details, decorative moldings, elegant curves.
    Dramatic lighting: chandeliers, sconces, statement fixtures.
    Sophisticated and lavish atmosphere, 1920s-30s glamour.
    High-end finishes, polished surfaces, opulent textiles.
    Keep room proportions. Make the scene natural and luxurious.
    ''',
}

# ===== STYLE PROMPTS SD 3.5 =====
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


# ===== DALLE-3 PROMPT =====
def get_dalle3_prompt(style: str, room: str) -> str:
    """Генерирует детальный промпт для DALL-E 3"""
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


# ===== NANO BANANA PROMPTS =====
def get_nano_banana_prompt(style: str, room: str, is_text_to_image: bool) -> str:
    """
    Генерирует промпт для Nano Banana в зависимости от режима

    Args:
        style: Стиль дизайна
        room: Тип комнаты
        is_text_to_image: True = text-to-image, False = image-to-image
    """
    if is_text_to_image:
        # TEXT-TO-IMAGE MODE
        style_instructions = STYLE_PROMPTS_NANO_TEXT2IMG.get(style, STYLE_PROMPTS_NANO_TEXT2IMG['modern']).strip()
        room_desc = ROOM_DESCRIPTIONS.get(room, room.replace('_', ' '))

        prompt = f"""
        TASK: Create a professional interior design photograph of a {room_desc}.

        STYLE INSTRUCTIONS:
        {style_instructions}

        ROOM TYPE: {room_desc}

        QUALITY REQUIREMENTS:
        - Professional architectural photography quality
        - Realistic lighting and shadows with natural light sources
        - Accurate perspective and realistic proportions
        - Magazine-worthy composition and framing
        - Natural, lived-in appearance, not staged
        - High attention to material details and textures
        - Practical and functional design that people can actually live in
        - Sophisticated color harmony, avoid oversaturation

        TECHNICAL EXECUTION:
        - Photorealistic rendering, not cartoon or illustration
        - Natural lighting conditions appropriate for time of day
        - Proper depth of field with professional camera simulation
        - Realistic material properties: wood grain, fabric texture, metal finish
        - Believable furniture scale and room proportions
        - Authentic Russian apartment standards and dimensions

        ATMOSPHERE:
        Russian apartment interior designed by world-class architect.
        Practical, functional, beautiful design that Russian clients love.
        Create a space people actually want to live in.
        Make the scene natural, realistic, and professionally executed.
        """
    else:
        # IMAGE-TO-IMAGE MODE
        style_instructions = STYLE_PROMPTS_NANO_IMG2IMG.get(style, STYLE_PROMPTS_NANO_IMG2IMG['modern']).strip()
        room_desc = ROOM_DESCRIPTIONS.get(room, room.replace('_', ' '))

        prompt = f"""
        TASK: Interior design transformation of this {room_desc}.

        STYLE INSTRUCTIONS:
        {style_instructions}

        QUALITY REQUIREMENTS:
        - Professional architectural photography quality
        - Realistic lighting and shadows
        - Accurate perspective and proportions
        - Magazine-worthy composition
        - Natural, lived-in appearance
        - High attention to detail
        - Practical and functional design
        - Sophisticated color harmony

        TECHNICAL:
        - Preserve original room dimensions and layout
        - Keep existing windows and door positions
        - Maintain architectural features (if suitable for style)
        - Natural lighting conditions
        - Photorealistic rendering

        Russian apartment standards: practical, functional, beautiful.
        Create a design that a Russian client would love and want to live in.
        Make the scene natural, realistic, and professionally executed.
        """

    return prompt.strip()


# ===== SD 3.5 PROMPT =====
def get_sd35_prompt(style: str, room: str) -> str:
    """Генерирует промпт для Stable Diffusion 3.5 Large"""
    style_desc = STYLE_PROMPTS_SD35.get(style, STYLE_PROMPTS_SD35['modern'])
    room_name = room.replace('_', ' ')

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
    Автоматически выбирает модель на основе флагов USE_*

    Args:
        photo_file_id: ID файла фотографии в Telegram (может быть None для text-to-image)
        room: Тип комнаты
        style: Стиль дизайна
        bot_token: Токен Telegram бота

    Returns:
        URL сгенерированного изображения или None при ошибке
    """

    if USE_NANO_BANANA:
        return await generate_nano_banana(photo_file_id, room, style, bot_token)
    elif USE_DALLE3:
        return await generate_dalle3(room, style)
    elif USE_SD35:
        return await generate_sd35(room, style)
    else:
        logger.error("❌ Не выбрана модель для генерации")
        return None


# ===== NANO BANANA GENERATE =====
async def generate_nano_banana(
    photo_file_id: Optional[str],
    room: str,
    style: str,
    bot_token: str
) -> str | None:
    """
    Генерирует изображение используя Google Nano Banana
    Автоматически выбирает режим на основе NANO_TEXT_TO_IMAGE
    """
    if not config.REPLICATE_API_TOKEN:
        logger.error("❌ REPLICATE_API_TOKEN не установлен в .env")
        return None

    try:
        import replicate
        os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN

        # Генерируем промпт для нужного режима
        prompt = get_nano_banana_prompt(style, room, NANO_TEXT_TO_IMAGE)

        if NANO_TEXT_TO_IMAGE:
            # ===== TEXT-TO-IMAGE MODE =====
            logger.info(f"🎨 Nano Banana (Text-to-Image): {room} → {style}")
            logger.debug(f"📝 Промпт длина: {len(prompt)} символов")

            output = replicate.run(
                "google/nano-banana",
                input={"prompt": prompt}
            )

        else:
            # ===== IMAGE-TO-IMAGE MODE =====
            if not photo_file_id:
                logger.error("❌ Для Image-to-Image режима нужно фото!")
                return None

            logger.info(f"🎨 Nano Banana (Image-to-Image): {room} → {style}")
            logger.debug(f"📝 Промпт длина: {len(prompt)} символов")

            # Скачиваем фото из Telegram
            import aiohttp
            photo_url = f"https://api.telegram.org/file/bot{bot_token}/{photo_file_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(photo_url) as resp:
                    if resp.status != 200:
                        logger.error(f"❌ Не удалось скачать фото: {resp.status}")
                        return None
                    photo_data = await resp.read()

            # Сохраняем во временный файл
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(photo_data)
                tmp_file_path = tmp_file.name

            try:
                output = replicate.run(
                    "google/nano-banana",
                    input={
                        "prompt": prompt,
                        "image_input": [open(tmp_file_path, 'rb')]
                    }
                )
            finally:
                # Удаляем временный файл
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass

        # Извлекаем URL из ответа
        logger.debug(f"🔍 Output type: {type(output)}")

        if output:
            if hasattr(output, 'url'):
                image_url = output.url
            elif isinstance(output, str):
                image_url = output
            else:
                image_url = str(output)

            logger.info(f"✅ Nano Banana готово!")
            logger.debug(f"📸 Image URL: {image_url}")
            return image_url
        else:
            logger.error("❌ Пустой ответ от Nano Banana")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка Nano Banana: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ===== DALLE-3 GENERATE =====
async def generate_dalle3(room: str, style: str) -> str | None:
    """Генерирует изображение используя DALL-E 3 на Replicate"""
    if not config.REPLICATE_API_TOKEN:
        logger.error("❌ REPLICATE_API_TOKEN не установлен")
        return None

    try:
        import replicate
        os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN

        prompt = get_dalle3_prompt(style, room)
        logger.info(f"🎨 DALL-E 3: {room} → {style}")
        logger.debug(f"📝 Промпт длина: {len(prompt)} символов")

        output = replicate.run(
            "openai/dall-e-3",
            input={"prompt": prompt, "size": "1024x1024"}
        )

        if output:
            if isinstance(output, list) and len(output) > 0:
                file_obj = output[0]
                image_url = file_obj.url if hasattr(file_obj, 'url') else str(file_obj)
            elif hasattr(output, 'url'):
                image_url = output.url
            else:
                image_url = str(output)

            logger.info(f"✅ DALL-E 3 готово!")
            return image_url
        else:
            logger.error("❌ Пустой ответ от DALL-E 3")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка DALL-E 3: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


# ===== SD 3.5 GENERATE =====
async def generate_sd35(room: str, style: str) -> str | None:
    """Генерирует изображение используя Stable Diffusion 3.5 Large"""
    if not config.REPLICATE_API_TOKEN:
        logger.error("❌ REPLICATE_API_TOKEN не установлен")
        return None

    try:
        import replicate
        os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN

        prompt = get_sd35_prompt(style, room)
        logger.info(f"🎨 SD 3.5: {room} → {style}")

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
                logger.info(f"✅ SD 3.5 готово!")
                return image_url
            except:
                return str(output)
        return None

    except Exception as e:
        logger.error(f"❌ Ошибка SD 3.5: {e}")
        return None
