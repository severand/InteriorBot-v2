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
    """

    # Ожидаем загрузку фото комнаты
    waiting_for_photo = State()

    # Выбираем тип комнаты (спальня, гостиная и т.д.)
    choose_room = State()

    # ✅ НОВОЕ: Выбираем режим создания дизайна
    choose_mode = State()

    # ✅ НОВОЕ: Выбираем мебель (для режима "Создать свой")
    choose_furniture = State()

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


# ===== НОВЫЕ СОСТОЯНИЯ ДЛЯ РЕФЕРАЛЬНОЙ СИСТЕМЫ =====

class ReferralStates(StatesGroup):
    """
    Состояния для реферальной системы и выплат.
    """

    # Ввод суммы для выплаты
    entering_payout_amount = State()

    # Ввод количества генераций для обмена
    entering_exchange_amount = State()

    # Ввод реквизитов (номер карты)
    entering_card_number = State()

    # Ввод реквизитов (YooMoney)
    entering_yoomoney = State()

    # Ввод реквизитов (номер телефона для СБП)
    entering_phone = State()

    # Ввод другого способа выплаты
    entering_other_method = State()


class AdminStates(StatesGroup):
    """
    Состояния для админ-панели.
    """

    # Редактирование настроек реферальной программы
    editing_referral_settings = State()

    # Ввод нового значения для настройки
    entering_setting_value = State()

    # Создание нового пакета - ввод количества генераций
    creating_package_tokens = State()

    # Создание нового пакета - ввод цены
    creating_package_price = State()

    # Редактирование пакета - выбор поля
    editing_package = State()

    # Редактирование пакета - ввод нового значения
    editing_package_value = State()

    # Обработка заявки на выплату - ввод примечания
    processing_payout = State()
