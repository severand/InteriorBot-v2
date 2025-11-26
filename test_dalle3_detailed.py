# test_dalle3_detailed.py

import replicate
import os

# ✅ ПРАВИЛЬНЫЙ ТОКЕН В КАВЫЧКАХ
os.environ["REPLICATE_API_TOKEN"] = "r8_U5d7rljYIDPGnffQkcVKHixtJNVsUHN1BspkN"

# ✅ ЖЁСТКИЙ ДЕТАЛЬНЫЙ ПРОМТ
ULTRA_DETAILED_PROMPT = """
CHILDREN'S ROOM - ARCHITECTURAL DESIGN WITH HARD REQUIREMENTS

ROOM DIMENSIONS:
- Width: 3 meters
- Length: 4 meters
- Ceiling height: 2.7 meters
- Minimalism in space, functionality

FURNITURE ARRANGEMENT (MANDATORY):
- LEFT WALL: Single white bed, wooden frame, light blue mattress, pillows
- RIGHT WALL: Light wood desk (~100 cm wide), gray computer chair
- ON THE DESK: Computer monitor, keyboard, mouse, desk lamp with yellow lampshade
- ABOVE THE DESK ON THE WALL: 3 Boy's photos in black frames (20x20cm square)

WALLS:
- Main color: Light gray walls (RAL 7035)
- Accent wall (above the bed): Soft blue paint (baby blue)
- Material: Matte paint, smooth walls
- NO posters, NO stickers

FLOOR:
- Light oak laminate or parquet
- Color: Natural oak (honey shade)
- Small rectangular rug (1.5m x 2m) in light gray

CEILING:
- White ceiling, matte finish
- Recessed spotlights (4-5 fixtures)
- No chandelier

WINDOW:
- Large window with white frames
- Light beige linen Roman shades
- Natural daylight enters the room

OBJECTS AND DETAILS:
- Bookshelf on the wall between the bed and desk (white, minimalist)
- On the shelf: 10-15 children's books, a few toys
- Toy basket under the table (light gray fabric)
- Built-in white cabinet along the left wall
- No unnecessary decorations, maximum minimalism

LIGHTING AND ATMOSPHERE:
- Daylight from the window perfectly illuminates half the room
- Soft, natural light from the recessed lamps
- Warm light bulbs (3000K)
- No harsh shadows, professional architectural lighting

STYLE:
- Children's minimalism
- Scandinavian + functionality
- Practical children's room for a boy aged 8-10
- No cartoon characters

PHOTOGRAPHY:
- Interior photo taken from eye level (approximately 1.5 m from the floor)
- View from the door looks into the room
- Professional architectural photo from Dwell magazine
- Perfect lighting, sharp photo, 4K quality
- Realistic proportions, correct perspective

EXCLUDE (DO NOT DRAW):
- No posters of characters
- No bright colors
- No clutter
- No toys on the floor
- No bizarre shapes
- Only a clean, organized, functional room
"""

print("🧪 ТЕСТИРОВАНИЕ ЖЁСТКОГО ПРОМТА...")
print(f"📝 Промт длина: {len(ULTRA_DETAILED_PROMPT)} символов")
print("⏳ Генерирую изображение...")

try:
    output = replicate.run(
        "openai/dall-e-3",
        input={
            "prompt": ULTRA_DETAILED_PROMPT,
            "size": "1024x1024",
        }
    )

    print(f"🔍 Output type: {type(output)}")
    print(f"🔍 Output: {output}")

    # ✅ ПРАВИЛЬНАЯ ОБРАБОТКА
    if output:
        if isinstance(output, list) and len(output) > 0:
            file_obj = output[0]
            if hasattr(file_obj, 'url'):
                image_url = file_obj.url
            else:
                image_url = str(file_obj)
        elif hasattr(output, 'url'):
            image_url = output.url
        else:
            image_url = str(output)

        print(f"✅ УСПЕШНО!")
        print(f"📸 URL: {image_url}")

        # Открыть в браузере
        import webbrowser

        webbrowser.open(image_url)
        print("🌐 Открыто в браузере")
    else:
        print("❌ Ошибка: Пустой ответ")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
