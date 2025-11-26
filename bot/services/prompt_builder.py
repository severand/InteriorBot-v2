# bot/services/prompt_builder.py

def build_custom_prompt(room: str, furniture: dict, colors: dict, style: str) -> str:
    """
    Собирает ЖЁСТКИЙ промт с точными требованиями
    """

    # Расшифровываем выбранные элементы
    furniture_list = build_furniture_description(room, furniture)
    colors_description = build_colors_description(colors)

    # Основной промт
    prompt = f"""
    {room.upper()} INTERIOR DESIGN - CUSTOM USER DESIGN

    ROOM DIMENSIONS:
    - Standard apartment room, realistic proportions
    - Ceiling height: 2.7 meters
    - Professional architectural photography

    FURNITURE REQUIREMENTS (MUST INCLUDE):
{furniture_list}

    COLOR PALETTE (EXACT):
{colors_description}

    STYLE: {style.capitalize()}

    REQUIREMENTS:
    - Realistic Russian apartment interior
    - Professional architectural photography quality
    - Natural balanced lighting
    - Correct perspective and proportions
    - Clean organized space
    - No clutter, no unnecessary elements
    - Magazine-worthy image quality
    - Practical functional design

    PHOTOGRAPHY STANDARDS:
    - Shot from eye level (1.5m from floor)
    - Professional interior designer photography
    - Perfect exposure and focus
    - 4K quality, sharp details
    - Natural color representation

    EXCLUDE COMPLETELY:
    - Cartoon characters or unrealistic elements
    - Oversaturated or unrealistic colors
    - Clutter or messy spaces
    - Harsh lighting or unrealistic shadows
    - Amateur rendering
    - Anything not explicitly required
    """

    return prompt.strip()


def build_furniture_description(room: str, furniture: dict) -> str:
    """Описывает мебель которую нужно включить"""

    if not furniture:
        return "    - Room can be partially furnished\n"

    description = ""
    for key in furniture.keys():
        description += f"    - Include: {key.replace('_', ' ').title()}\n"

    return description


def build_colors_description(colors: dict) -> str:
    """Описывает цвета комнаты"""

    wall_colors_map = {
        'light_gray': 'Light gray RAL 7035',
        'white': 'White matte finish',
        'soft_blue': 'Soft blue matte',
        'beige': 'Beige warm tone',
        'light_green': 'Light green sage',
        'pale_pink': 'Pale pink matte',
    }

    floor_colors_map = {
        'light_oak': 'Light oak wood',
        'dark_oak': 'Dark oak wood',
        'gray_parquet': 'Gray parquet',
        'white_oak': 'White oak wood',
        'walnut': 'Walnut wood',
    }

    ceiling_colors_map = {
        'white': 'White matte ceiling',
        'soft_gray': 'Soft gray matte',
        'warm_white': 'Warm white matte',
        'light_gray': 'Light gray matte',
    }

    description = ""

    if colors.get('walls'):
        wall = wall_colors_map.get(colors['walls'], colors['walls'])
        description += f"    - Walls: {wall}\n"

    if colors.get('floor'):
        floor = floor_colors_map.get(colors['floor'], colors['floor'])
        description += f"    - Floor: {floor}\n"

    if colors.get('ceiling'):
        ceiling = ceiling_colors_map.get(colors['ceiling'], colors['ceiling'])
        description += f"    - Ceiling: {ceiling}\n"

    return description if description else "    - Neutral colors palette\n"
