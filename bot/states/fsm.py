# bot/states/fsm.py

from aiogram.fsm.state import StatesGroup, State


class MainMenuStates(StatesGroup):
    """
    Состояния для главного меню и навигации.
    """

    # Находимся в главном меню
    main_menu = State()

    # Находимся в меню "Для дома"
    home_menu = State()

    # Находимся в меню "Для бизнеса"
    business_menu = State()

    # Находимся в профиле
    profile = State()


class CreationStates(StatesGroup):
    """
    Состояния для процесса создания дизайна.
    (Сохранено для совместимости со старыми обработчиками)
    """

    # Ожидаем загрузку фото комнаты
    waiting_for_photo = State()

    # Выбираем тип комнаты (спальня, гостиная и т.д.)
    choose_room = State()

    # Выбираем стиль дизайна
    choose_style = State()


class RoomSelectionStates(StatesGroup):
    """
    Состояния для выбора помещения (новая система).
    """

    # Выбираем помещение для дома
    selecting_home_room = State()

    # Выбираем помещение для бизнеса
    selecting_business_room = State()


class StyleSelectionStates(StatesGroup):
    """
    Состояния для выбора стиля.
    """

    # Выбираем стиль
    selecting_style = State()


class DesignGenerationStates(StatesGroup):
    """
    Состояния для процесса генерации дизайна.
    """

    # Ожидаем загрузку фото/видео
    waiting_for_media = State()

    # Генерируем дизайн
    generating_design = State()

    # Показываем результат
    showing_result = State()


class OtherStates(StatesGroup):
    """
    Прочие состояния (оставлено для совместимости).
    """
    pass
