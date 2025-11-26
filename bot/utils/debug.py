# utils/debug.py
# ✅ УНИВЕРСАЛЬНЫЙ ОТЛАДЧИК

import logging
import functools
import inspect
from typing import Any, Callable
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

logger = logging.getLogger(__name__)


# ===== ЦВЕТА ДЛЯ ЛОГОВ (для наглядности) =====
class Colors:
    HEADER = '🔵'
    OKGREEN = '✅'
    WARNING = '⚠️'
    FAIL = '❌'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ===== ОТЛАДКА: ВОТ ЭТО ВЫПОЛНЯЕТСЯ =====
def debug_handler(func: Callable) -> Callable:
    """Декоратор для отладки любого handler'а"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        handler_name = func.__name__
        module_name = func.__module__

        # Определяем тип аргумента (CallbackQuery или Message)
        user_id = None
        callback_data = None
        message_text = None

        for arg in args:
            if isinstance(arg, CallbackQuery):
                user_id = arg.from_user.id
                callback_data = arg.data
                break
            elif isinstance(arg, Message):
                user_id = arg.from_user.id
                message_text = arg.text
                break

        logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.HEADER} HANDLER ВЫЗВАН
├─ Модуль: {module_name}
├─ Функция: {Colors.BOLD}{handler_name}{Colors.ENDC}
├─ User ID: {user_id}
├─ Callback: {callback_data}
├─ Message: {message_text}
╚════════════════════════════════════════════════════════════╝
        """)

        try:
            result = await func(*args, **kwargs)
            logger.info(f"{Colors.OKGREEN} ✅ {handler_name} завершена успешно\n")
            return result
        except Exception as e:
            logger.error(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.FAIL} ОШИБКА В HANDLER'E
├─ Функция: {handler_name}
├─ Ошибка: {type(e).__name__}
├─ Сообщение: {str(e)}
├─ Модуль: {module_name}
╚════════════════════════════════════════════════════════════╝
            """, exc_info=True)
            raise

    return wrapper


# ===== ОТЛАДКА: ВОТ СЕЙЧАС ПРОВЕРЯЮ STATE =====
async def log_state(state: FSMContext, label: str = "STATE CHECK"):
    """Выводит текущее состояние FSM"""
    current_state = await state.get_state()
    data = await state.get_data()

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.HEADER} {label}
├─ Current State: {Colors.BOLD}{current_state}{Colors.ENDC}
├─ State Data Keys: {list(data.keys())}
├─ Full Data: {data}
╚════════════════════════════════════════════════════════════╝
    """)


# ===== ОТЛАДКА: КАКОЙ CALLBACK ПРИШЕЛ =====
def log_callback(callback_data: str, expected_pattern: str = None):
    """Логирует пришедший callback"""
    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.HEADER} CALLBACK ПОЛУЧЕН
├─ Data: {Colors.BOLD}{callback_data}{Colors.ENDC}
├─ Expected: {expected_pattern}
├─ Match: {'✅ ДА' if expected_pattern and expected_pattern in callback_data else '⚠️ НЕТ'}
╚════════════════════════════════════════════════════════════╝
    """)


# ===== ОТЛАДКА: ФУНКЦИЯ ВЫЗЫВАЕТСЯ? =====
def log_function_call(func_name: str, params: dict = None):
    """Логирует вызов функции с параметрами"""
    params_str = "\n├─ ".join([f"{k}: {v}" for k, v in (params or {}).items()])

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.HEADER} ФУНКЦИЯ ВЫЗВАНА
├─ Функция: {Colors.BOLD}{func_name}{Colors.ENDC}
├─ {params_str if params else 'Параметров: нет'}
╚════════════════════════════════════════════════════════════╝
    """)


# ===== ОТЛАДКА: ROUTE ЗАРЕГИСТРИРОВАНА? =====
def log_router_registration(router_name: str, handlers: list = None):
    """Логирует регистрацию роутера"""
    handlers_str = "\n├─ ".join(handlers) if handlers else "Нет handlers"

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.OKGREEN} ROUTER ЗАРЕГИСТРИРОВАН
├─ Роутер: {Colors.BOLD}{router_name}{Colors.ENDC}
├─ Handlers:
├─ {handlers_str}
╚════════════════════════════════════════════════════════════╝
    """)


# ===== ОТЛАДКА: ПЕРЕХОД В НОВЫЙ STATE =====
async def log_state_transition(state: FSMContext, new_state, label: str = ""):
    """Логирует переход в новое состояние"""
    old_state = await state.get_state()

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.WARNING} STATE ИЗМЕНЯЕТСЯ
├─ Старый state: {old_state}
├─ Новый state: {Colors.BOLD}{new_state}{Colors.ENDC}
├─ Описание: {label}
╚════════════════════════════════════════════════════════════╝
    """)

    await state.set_state(new_state)


# ===== ОТЛАДКА: ВЫБОР ПОЛЬЗОВАТЕЛЯ =====
def log_user_choice(user_id: int, choice_type: str, choice_value: str):
    """Логирует выбор пользователя"""
    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.OKGREEN} ВЫБОР ПОЛЬЗОВАТЕЛЯ
├─ User ID: {user_id}
├─ Тип выбора: {choice_type}
├─ Выбрано: {Colors.BOLD}{choice_value}{Colors.ENDC}
╚════════════════════════════════════════════════════════════╝
    """)


# ===== ОТЛАДКА: ОТПРАВКА СООБЩЕНИЯ =====
def log_message_send(user_id: int, text: str = None, buttons_count: int = 0):
    """Логирует отправку сообщения"""
    text_preview = (text[:50] + "...") if text and len(text) > 50 else text

    logger.info(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.HEADER} СООБЩЕНИЕ ОТПРАВЛЯЕТСЯ
├─ User ID: {user_id}
├─ Текст: {text_preview}
├─ Кнопок: {buttons_count}
╚════════════════════════════════════════════════════════════╝
    """)


# ===== КРИТИЧЕСКАЯ ОШИБКА =====
def log_critical_error(error_type: str, error_msg: str, location: str = ""):
    """Логирует критическую ошибку"""
    logger.critical(f"""
╔════════════════════════════════════════════════════════════╗
{Colors.FAIL} КРИТИЧЕСКАЯ ОШИБКА!!!
├─ Тип: {error_type}
├─ Сообщение: {error_msg}
├─ Место: {location}
╚════════════════════════════════════════════════════════════╝
    """)
