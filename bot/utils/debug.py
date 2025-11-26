# utils/debug.py
# ✅ ПРОДВИНУТЫЙ ОТЛАДЧИК С АВТОЛОГИРОВАНИЕМ ОШИБОК

import logging
import functools
import inspect
import traceback
import sys
from typing import Any, Callable
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

logger = logging.getLogger(__name__)


# ===== ЦВЕТА ДЛЯ ЛОГОВ =====
class Colors:
    HEADER = '🔵'
    OKGREEN = '✅'
    WARNING = '⚠️'
    FAIL = '❌'
    CRITICAL = '🔥'
    DEBUG = '🔧'
    INFO = 'ℹ️'


# ===== ГЛАВНЫЙ ДЕКОРАТОР - АВТОМАТИЧЕСКОЕ ЛОГИРОВАНИЕ =====
def debug_handler(func: Callable) -> Callable:
    """
    Продвинутый декоратор для автоматического логирования:
    - Входящие параметры
    - Текущий State
    - Все ошибки с полным traceback
    - Место возникновения ошибки
    - Номер строки и файл
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        handler_name = func.__name__
        module_name = func.__module__
        file_name = inspect.getfile(func)
        line_number = inspect.getsourcelines(func)[1]

        # Определяем тип аргумента (CallbackQuery или Message)
        user_id = None
        callback_data = None
        message_text = None
        state = None

        for arg in args:
            if isinstance(arg, CallbackQuery):
                user_id = arg.from_user.id
                callback_data = arg.data
                break
            elif isinstance(arg, Message):
                user_id = arg.from_user.id
                message_text = arg.text
                break

        # Ищем FSMContext в аргументах
        for arg in args:
            if isinstance(arg, FSMContext):
                state = arg
                break

        # Проверяем kwargs
        if not state and 'state' in kwargs:
            state = kwargs['state']

        # Получаем текущий State если есть
        current_state = None
        state_data = {}
        if state:
            try:
                current_state = await state.get_state()
                state_data = await state.get_data()
            except:
                pass

        # ===== ЛОГИРУЕМ ВХОД В ФУНКЦИЮ =====
        logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.HEADER} HANDLER ВЫЗВАН
╠════════════════════════════════════════════════════════════╣
║ 📍 Модуль:      {module_name}
║ 📍 Файл:        {file_name}
║ 📍 Строка:      {line_number}
║ 🎯 Функция:     {handler_name}()
║ 👤 User ID:     {user_id}
║ 📞 Callback:    {callback_data}
║ 💬 Message:     {message_text}
║ 🔄 State:       {current_state}
║ 📦 State Data:  {list(state_data.keys()) if state_data else 'нет'}
╚════════════════════════════════════════════════════════════╝
        """)

        try:
            # Выполняем функцию
            result = await func(*args, **kwargs)

            # ===== ЛОГИРУЕМ УСПЕШНОЕ ВЫПОЛНЕНИЕ =====
            logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.OKGREEN} УСПЕШНО ВЫПОЛНЕНО
╠════════════════════════════════════════════════════════════╣
║ Функция: {handler_name}()
║ Модуль:  {module_name}
╚════════════════════════════════════════════════════════════╝
            """)

            return result

        except Exception as e:
            # ===== ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ОШИБКИ =====

            # Получаем полный traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # Находим точное место ошибки
            tb_list = traceback.extract_tb(exc_traceback)
            error_location = tb_list[-1] if tb_list else None

            error_file = error_location.filename if error_location else "Unknown"
            error_line = error_location.lineno if error_location else "Unknown"
            error_function = error_location.name if error_location else "Unknown"
            error_code = error_location.line if error_location else "Unknown"

            # Форматируем полный traceback
            full_traceback = ''.join(traceback.format_tb(exc_traceback))

            # ===== КРИТИЧЕСКОЕ ЛОГИРОВАНИЕ =====
            logger.critical(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.CRITICAL} КРИТИЧЕСКАЯ ОШИБКА!!!
╠════════════════════════════════════════════════════════════╣
║ 🎯 ВЫЗВАНО В HANDLER:
║    ├─ Функция:    {handler_name}()
║    ├─ Модуль:     {module_name}
║    ├─ Файл:       {file_name}
║    └─ Строка:     {line_number}
║
║ 💥 ОШИБКА ПРОИЗОШЛА В:
║    ├─ Функция:    {error_function}()
║    ├─ Файл:       {error_file}
║    ├─ Строка:     {error_line}
║    └─ Код:        {error_code}
║
║ ⚠️ ТИП ОШИБКИ:
║    {exc_type.__name__}
║
║ 📝 СООБЩЕНИЕ ОШИБКИ:
║    {str(exc_value)}
║
║ 👤 КОНТЕКСТ:
║    ├─ User ID:    {user_id}
║    ├─ Callback:   {callback_data}
║    ├─ Message:    {message_text}
║    ├─ State:      {current_state}
║    └─ State Data: {state_data}
║
║ 📚 ПОЛНЫЙ TRACEBACK:
║ {full_traceback}
╚════════════════════════════════════════════════════════════╝
            """)

            # Пробрасываем ошибку дальше
            raise

    return wrapper


# ===== АВТОМАТИЧЕСКОЕ ЛОГИРОВАНИЕ ЛЮБОЙ ФУНКЦИИ =====
def auto_log(func: Callable) -> Callable:
    """
    Декоратор для автоматического логирования ЛЮБОЙ функции
    (не только handlers, но и обычных функций)
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = func.__module__
        file_name = inspect.getfile(func)
        line_number = inspect.getsourcelines(func)[1]

        logger.debug(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.DEBUG} ФУНКЦИЯ ВЫЗВАНА
╠════════════════════════════════════════════════════════════╣
║ Функция:  {func_name}()
║ Модуль:   {module_name}
║ Файл:     {file_name}
║ Строка:   {line_number}
║ Args:     {args if args else 'нет'}
║ Kwargs:   {kwargs if kwargs else 'нет'}
╚════════════════════════════════════════════════════════════╝
        """)

        try:
            result = await func(*args, **kwargs)
            logger.debug(f"{Colors.OKGREEN} {func_name}() выполнена успешно")
            return result
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            error_location = tb_list[-1] if tb_list else None

            logger.error(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.FAIL} ОШИБКА В ФУНКЦИИ
╠════════════════════════════════════════════════════════════╣
║ Функция:     {func_name}()
║ Модуль:      {module_name}
║ Ошибка в:    {error_location.filename if error_location else 'Unknown'}
║ Строка:      {error_location.lineno if error_location else 'Unknown'}
║ Тип ошибки:  {exc_type.__name__}
║ Сообщение:   {str(exc_value)}
╚════════════════════════════════════════════════════════════╝
            """, exc_info=True)
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = func.__module__
        file_name = inspect.getfile(func)
        line_number = inspect.getsourcelines(func)[1]

        logger.debug(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.DEBUG} ФУНКЦИЯ ВЫЗВАНА (SYNC)
╠════════════════════════════════════════════════════════════╣
║ Функция:  {func_name}()
║ Модуль:   {module_name}
║ Файл:     {file_name}
║ Строка:   {line_number}
╚════════════════════════════════════════════════════════════╝
        """)

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{Colors.OKGREEN} {func_name}() выполнена успешно")
            return result
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            error_location = tb_list[-1] if tb_list else None

            logger.error(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.FAIL} ОШИБКА В ФУНКЦИИ (SYNC)
╠════════════════════════════════════════════════════════════╣
║ Функция:     {func_name}()
║ Модуль:      {module_name}
║ Ошибка в:    {error_location.filename if error_location else 'Unknown'}
║ Строка:      {error_location.lineno if error_location else 'Unknown'}
║ Тип ошибки:  {exc_type.__name__}
║ Сообщение:   {str(exc_value)}
╚════════════════════════════════════════════════════════════╝
            """, exc_info=True)
            raise

    # Определяем async или sync функция
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# ===== ОСТАЛЬНЫЕ ПОЛЕЗНЫЕ ФУНКЦИИ (без изменений) =====

async def log_state(state: FSMContext, label: str = "STATE CHECK"):
    """Выводит текущее состояние FSM"""
    current_state = await state.get_state()
    data = await state.get_data()

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.HEADER} {label}
╠════════════════════════════════════════════════════════════╣
║ Current State: {current_state}
║ State Data:    {data}
╚════════════════════════════════════════════════════════════╝
    """)


def log_callback(callback_data: str, expected_pattern: str = None):
    """Логирует пришедший callback"""
    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.HEADER} CALLBACK ПОЛУЧЕН
╠════════════════════════════════════════════════════════════╣
║ Data:     {callback_data}
║ Expected: {expected_pattern}
║ Match:    {'✅ ДА' if expected_pattern and expected_pattern in callback_data else '⚠️ НЕТ'}
╚════════════════════════════════════════════════════════════╝
    """)


def log_function_call(func_name: str, params: dict = None):
    """Логирует вызов функции с параметрами"""
    params_str = "\n║ ".join([f"{k}: {v}" for k, v in (params or {}).items()])

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.HEADER} ФУНКЦИЯ ВЫЗВАНА
╠════════════════════════════════════════════════════════════╣
║ Функция: {func_name}()
║ {params_str if params else 'Параметров: нет'}
╚════════════════════════════════════════════════════════════╝
    """)


def log_router_registration(router_name: str, handlers: list = None):
    """Логирует регистрацию роутера"""
    handlers_str = "\n║ ".join(handlers) if handlers else "Нет handlers"

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.OKGREEN} ROUTER ЗАРЕГИСТРИРОВАН
╠════════════════════════════════════════════════════════════╣
║ Роутер:   {router_name}
║ Handlers: {handlers_str}
╚════════════════════════════════════════════════════════════╝
    """)


async def log_state_transition(state: FSMContext, new_state, label: str = ""):
    """Логирует переход в новое состояние"""
    old_state = await state.get_state()

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.WARNING} STATE ИЗМЕНЯЕТСЯ
╠════════════════════════════════════════════════════════════╣
║ Старый state: {old_state}
║ Новый state:  {new_state}
║ Описание:     {label}
╚════════════════════════════════════════════════════════════╝
    """)

    await state.set_state(new_state)


def log_user_choice(user_id: int, choice_type: str, choice_value: str):
    """Логирует выбор пользователя"""
    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.OKGREEN} ВЫБОР ПОЛЬЗОВАТЕЛЯ
╠════════════════════════════════════════════════════════════╣
║ User ID:      {user_id}
║ Тип выбора:   {choice_type}
║ Выбрано:      {choice_value}
╚════════════════════════════════════════════════════════════╝
    """)


def log_message_send(user_id: int, text: str = None, buttons_count: int = 0):
    """Логирует отправку сообщения"""
    text_preview = (text[:50] + "...") if text and len(text) > 50 else text

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.HEADER} СООБЩЕНИЕ ОТПРАВЛЯЕТСЯ
╠════════════════════════════════════════════════════════════╣
║ User ID: {user_id}
║ Текст:   {text_preview}
║ Кнопок:  {buttons_count}
╚════════════════════════════════════════════════════════════╝
    """)


def log_critical_error(error_type: str, error_msg: str, location: str = ""):
    """Логирует критическую ошибку вручную"""
    logger.critical(f"""
╔════════════════════════════════════════════════════════════╗
║ {Colors.CRITICAL} КРИТИЧЕСКАЯ ОШИБКА!!!
╠════════════════════════════════════════════════════════════╣
║ Тип:      {error_type}
║ Сообщение: {error_msg}
║ Место:    {location}
╚════════════════════════════════════════════════════════════╝
    """)
