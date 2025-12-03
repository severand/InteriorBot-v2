# bot/handlers/referral.py
# Реферальная система: выплаты, обмены, реквизиты

import logging
import re
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import db
from states.fsm import ReferralStates

logger = logging.getLogger(__name__)
router = Router()

logger.info("🔧 [referral.py] Модуль загружен")


# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

def format_number(num: int) -> str:
    """Форматирование числа с пробелами"""
    return "{:,}".format(num).replace(",", " ")


def validate_phone(phone: str) -> tuple[bool, str]:
    """
    Валидация и форматирование номера телефона
    Returns: (valid: bool, formatted_phone: str)
    """
    # Убираем все кроме цифр и +
    phone = re.sub(r'[^\d+]', '', phone)
    
    # Приводим к +7
    if phone.startswith('8'):
        phone = '+7' + phone[1:]
    elif phone.startswith('7'):
        phone = '+' + phone
    elif not phone.startswith('+7'):
        return False, ""
    
    # Проверяем длину (+7 + 10 цифр)
    if len(phone) != 12:
        return False, ""
    
    # Форматируем для отображения: +7 (999) 123-45-67
    formatted = f"+7 ({phone[2:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:]}"
    
    return True, formatted


# ===== ОБМЕН РЕФЕРАЛЬНОГО БАЛАНСА НА ГЕНЕРАЦИИ =====

@router.callback_query(F.data == "referral_exchange_tokens")
async def exchange_to_tokens(callback: CallbackQuery, state: FSMContext):
    """Начало обмена реферального баланса на генерации"""
    user_id = callback.from_user.id
    
    balance = await db.get_referral_balance(user_id)
    exchange_rate = int(await db.get_setting("referral_exchange_rate") or "29")
    
    max_tokens = balance // exchange_rate
    
    if max_tokens < 1:
        await callback.answer(
            f"⚠️ Недостаточно средств для обмена.\n"
            f"Минимум: {exchange_rate} руб. = 1 генерация",
            show_alert=True
        )
        return
    
    text = (
        "💎 **ОБМЕН НА ГЕНЕРАЦИИ**\n\n"
        f"💰 Реферальный баланс: **{format_number(balance)} руб.**\n"
        f"🎨 Курс обмена: 1 генерация = {exchange_rate} руб.\n\n"
        f"Вы можете обменять до **{max_tokens} генераций**\n\n"
        f"📝 Введите количество генераций:\n"
        f"(или /all для обмена всей суммы)"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ReferralStates.entering_exchange_amount)


@router.message(ReferralStates.entering_exchange_amount)
async def process_exchange_amount(message: Message, state: FSMContext):
    """Обработка ввода количества генераций для обмена"""
    user_id = message.from_user.id
    
    balance = await db.get_referral_balance(user_id)
    exchange_rate = int(await db.get_setting("referral_exchange_rate") or "29")
    max_tokens = balance // exchange_rate
    
    # Парсим количество
    if message.text == "/all":
        tokens = max_tokens
    else:
        try:
            tokens = int(message.text)
        except ValueError:
            await message.answer("⚠️ Введите число или /all")
            return
    
    # Проверки
    if tokens < 1:
        await message.answer("⚠️ Минимум 1 генерация")
        return
    
    if tokens > max_tokens:
        await message.answer(
            f"⚠️ Недостаточно средств.\n"
            f"Максимум: {max_tokens} генераций"
        )
        return
    
    # Расчёт
    cost = tokens * exchange_rate
    remaining = balance - cost
    current_balance = await db.get_balance(user_id)
    new_balance = current_balance + tokens
    
    # Подтверждение
    text = (
        "💎 **ПОДТВЕРЖДЕНИЕ ОБМЕНА**\n\n"
        f"Генераций: **{tokens}**\n"
        f"Стоимость: **{format_number(cost)} руб.**\n\n"
        f"После обмена:\n"
        f"• Реферальный баланс: **{format_number(remaining)} руб.**\n"
        f"• Баланс генераций: {current_balance} → **{new_balance}**\n\n"
        f"⚡️ Обмен мгновенный!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Обменять", callback_data=f"confirm_exchange_{tokens}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="show_profile")
        ]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.clear()


@router.callback_query(F.data.startswith("confirm_exchange_"))
async def confirm_exchange(callback: CallbackQuery):
    """Подтверждение обмена"""
    user_id = callback.from_user.id
    tokens = int(callback.data.split("_")[-1])
    
    balance = await db.get_referral_balance(user_id)
    exchange_rate = int(await db.get_setting("referral_exchange_rate") or "29")
    cost = tokens * exchange_rate
    
    # Финальная проверка
    if cost > balance:
        await callback.answer("⚠️ Недостаточно средств", show_alert=True)
        return
    
    # Выполняем обмен
    await db.decrease_referral_balance(user_id, cost)
    await db.increase_balance(user_id, tokens)
    
    # Логируем
    await db.log_referral_exchange(user_id, cost, tokens, exchange_rate)
    
    # Уведомление
    new_token_balance = await db.get_balance(user_id)
    new_referral_balance = await db.get_referral_balance(user_id)
    
    text = (
        "✅ **Обмен завершён!**\n\n"
        f"+{tokens} генераций начислено на ваш счёт\n"
        f"Реферальный баланс: **{format_number(new_referral_balance)} руб.**\n"
        f"Баланс генераций: **{new_token_balance}**\n\n"
        f"Приятного использования! 🎨"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer("✅ Обмен выполнен!", show_alert=True)


# ===== ЗАПРОС ВЫПЛАТЫ =====

@router.callback_query(F.data == "referral_request_payout")
async def request_payout(callback: CallbackQuery, state: FSMContext):
    """Начало запроса выплаты"""
    user_id = callback.from_user.id
    
    balance = await db.get_referral_balance(user_id)
    min_payout = int(await db.get_setting("referral_min_payout") or "500")
    
    if balance < min_payout:
        await callback.answer(
            f"⚠️ Минимальная сумма вывода: {format_number(min_payout)} руб.",
            show_alert=True
        )
        return
    
    # Проверяем наличие реквизитов
    payment_details = await db.get_payment_details(user_id)
    
    if not payment_details or not payment_details.get('payment_method'):
        await callback.answer(
            "⚠️ Сначала укажите реквизиты для выплаты",
            show_alert=True
        )
        return
    
    text = (
        "💸 **ЗАПРОС ВЫПЛАТЫ**\n\n"
        f"💰 Доступно к выводу: **{format_number(balance)} руб.**\n"
        f"⚠️ Минимальная сумма: {format_number(min_payout)} руб.\n\n"
        f"📝 Введите сумму для вывода:\n"
        f"(или /all для вывода всей суммы)"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ReferralStates.entering_payout_amount)


@router.message(ReferralStates.entering_payout_amount)
async def process_payout_amount(message: Message, state: FSMContext):
    """Обработка ввода суммы выплаты"""
    user_id = message.from_user.id
    
    balance = await db.get_referral_balance(user_id)
    min_payout = int(await db.get_setting("referral_min_payout") or "500")
    
    # Парсим сумму
    if message.text == "/all":
        amount = balance
    else:
        try:
            amount = int(message.text)
        except ValueError:
            await message.answer("⚠️ Введите число или /all")
            return
    
    # Проверки
    if amount < min_payout:
        await message.answer(f"⚠️ Минимальная сумма вывода: {format_number(min_payout)} руб.")
        return
    
    if amount > balance:
        await message.answer(
            f"⚠️ Недостаточно средств. Доступно: {format_number(balance)} руб."
        )
        return
    
    # Получаем реквизиты
    payment_details = await db.get_payment_details(user_id)
    method = payment_details.get('payment_method', 'Не указан')
    details = payment_details.get('payment_details', 'Не указаны')
    
    # Маскируем реквизиты
    if method == 'card' and len(details) >= 16:
        masked_details = f"{details[:4]} {'*' * 4} {'*' * 4} {details[-4:]}"
    elif method == 'sbp' and len(details) >= 10:
        masked_details = f"+7 ({details[2:5]}) ***-**-{details[-2:]}"
    else:
        masked_details = details[:10] + '***' if len(details) > 10 else details
    
    method_names = {
        'card': '💳 Банковская карта',
        'yoomoney': '💵 YooMoney',
        'sbp': '📱 СБП',
        'other': '💰 Другой способ'
    }
    method_display = method_names.get(method, method)
    
    remaining = balance - amount
    
    # Подтверждение
    text = (
        "💸 **ПОДТВЕРЖДЕНИЕ ВЫПЛАТЫ**\n\n"
        f"Сумма: **{format_number(amount)} руб.**\n"
        f"Способ: {method_display}\n"
        f"Реквизиты: `{masked_details}`\n\n"
        f"После вывода останется: **{format_number(remaining)} руб.**\n\n"
        f"⏳ Обработка: 1-3 рабочих дня"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_payout_{amount}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="show_profile")
        ]
    ])
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    await state.clear()


@router.callback_query(F.data.startswith("confirm_payout_"))
async def confirm_payout(callback: CallbackQuery):
    """Подтверждение заявки на выплату"""
    user_id = callback.from_user.id
    amount = int(callback.data.split("_")[-1])
    
    balance = await db.get_referral_balance(user_id)
    
    # Финальная проверка
    if amount > balance:
        await callback.answer("⚠️ Недостаточно средств", show_alert=True)
        return
    
    # Получаем реквизиты
    payment_details = await db.get_payment_details(user_id)
    method = payment_details.get('payment_method')
    details = payment_details.get('payment_details')
    
    # Создаём заявку
    payout_id = await db.create_payout_request(user_id, amount, method, details)
    
    # Уменьшаем баланс
    await db.decrease_referral_balance(user_id, amount)
    
    text = (
        "✅ **ЗАЯВКА ОТПРАВЛЕНА!**\n\n"
        f"№ заявки: #{payout_id}\n"
        f"Сумма: **{format_number(amount)} руб.**\n\n"
        f"⏳ Ваша заявка поступила в обработку.\n"
        f"Выплата произойдёт в течение 1-3 рабочих дней.\n\n"
        f"Вы получите уведомление после обработки."
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer("✅ Заявка отправлена!", show_alert=True)


# ===== НАСТРОЙКА РЕКВИЗИТОВ =====

@router.callback_query(F.data == "referral_setup_payment")
async def setup_payment_method(callback: CallbackQuery):
    """Выбор способа выплаты"""
    text = (
        "⚙️ **НАСТРОЙКА РЕКВИЗИТОВ**\n\n"
        "Выберите способ получения выплат:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Банковская карта", callback_data="payment_method_card")],
        [InlineKeyboardButton(text="💵 YooMoney", callback_data="payment_method_yoomoney")],
        [InlineKeyboardButton(text="📱 СБП (по номеру телефона)", callback_data="payment_method_sbp")],
        [InlineKeyboardButton(text="💰 Другой способ", callback_data="payment_method_other")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="show_profile")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "payment_method_card")
async def setup_card(callback: CallbackQuery, state: FSMContext):
    """Настройка банковской карты"""
    text = (
        "💳 **ПРИВЯЗКА КАРТЫ**\n\n"
        "Введите номер банковской карты:\n\n"
        "Формат: 1234 5678 9012 3456\n"
        "или: 1234567890123456\n\n"
        "Отправьте номер или /cancel для отмены"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ReferralStates.entering_card_number)


@router.message(ReferralStates.entering_card_number)
async def process_card_number(message: Message, state: FSMContext):
    """Обработка номера карты"""
    card = re.sub(r'[^\d]', '', message.text)
    
    if len(card) not in [16, 18, 19]:  # Поддерживаем разные длины
        await message.answer(
            "⚠️ Неверный формат номера карты.\n"
            "Используйте формат: 1234 5678 9012 3456"
        )
        return
    
    # Сохраняем
    await db.set_payment_details(message.from_user.id, "card", card)
    
    # Маскируем для отображения
    masked = f"{card[:4]} {'*' * 4} {'*' * 4} {card[-4:]}"
    
    text = (
        "✅ **Карта привязана!**\n\n"
        f"Номер карты: `{masked}`\n"
        f"Способ: Банковская карта\n\n"
        "Теперь вы можете запрашивать выплаты."
    )
    
    await message.answer(text, parse_mode="Markdown")
    await state.clear()


@router.callback_query(F.data == "payment_method_sbp")
async def setup_sbp(callback: CallbackQuery, state: FSMContext):
    """Настройка СБП"""
    text = (
        "📱 **ПРИВЯЗКА НОМЕРА ТЕЛЕФОНА**\n\n"
        "Введите номер телефона для СБП:\n\n"
        "Формат: +7XXXXXXXXXX\n"
        "Пример: +79991234567\n\n"
        "Отправьте номер или /cancel для отмены"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ReferralStates.entering_phone)


@router.message(ReferralStates.entering_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона"""
    phone = message.text.strip()
    
    # Валидация и форматирование
    valid, formatted = validate_phone(phone)
    
    if not valid:
        await message.answer(
            "⚠️ Неверный формат номера.\n"
            "Используйте формат: +79991234567"
        )
        return
    
    # Сохраняем (храним без форматирования)
    clean_phone = re.sub(r'[^\d+]', '', phone)
    if clean_phone.startswith('8'):
        clean_phone = '+7' + clean_phone[1:]
    elif clean_phone.startswith('7'):
        clean_phone = '+' + clean_phone
    
    await db.set_payment_details(message.from_user.id, "sbp", clean_phone)
    
    text = (
        "✅ **Номер привязан!**\n\n"
        f"Телефон: `{formatted}`\n"
        f"Способ: СБП (Система быстрых платежей)\n\n"
        "Теперь вы можете запрашивать выплаты.\n"
        "При выводе администратор свяжется для уточнения банка."
    )
    
    await message.answer(text, parse_mode="Markdown")
    await state.clear()


@router.callback_query(F.data == "payment_method_yoomoney")
async def setup_yoomoney(callback: CallbackQuery, state: FSMContext):
    """Настройка YooMoney"""
    text = (
        "💵 **ПРИВЯЗКА YooMoney**\n\n"
        "Введите номер кошелька YooMoney:\n\n"
        "Пример: 410012345678901\n\n"
        "Отправьте номер или /cancel для отмены"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ReferralStates.entering_yoomoney)


@router.message(ReferralStates.entering_yoomoney)
async def process_yoomoney(message: Message, state: FSMContext):
    """Обработка номера YooMoney"""
    wallet = re.sub(r'[^\d]', '', message.text)
    
    if len(wallet) < 11 or len(wallet) > 15:
        await message.answer(
            "⚠️ Неверный формат номера кошелька.\n"
            "Пример: 410012345678901"
        )
        return
    
    # Сохраняем
    await db.set_payment_details(message.from_user.id, "yoomoney", wallet)
    
    text = (
        "✅ **Кошелёк привязан!**\n\n"
        f"Кошелёк: `{wallet}`\n"
        f"Способ: YooMoney\n\n"
        "Теперь вы можете запрашивать выплаты."
    )
    
    await message.answer(text, parse_mode="Markdown")
    await state.clear()


@router.callback_query(F.data == "payment_method_other")
async def setup_other(callback: CallbackQuery, state: FSMContext):
    """Настройка другого способа"""
    text = (
        "💰 **ДРУГОЙ СПОСОБ**\n\n"
        "Опишите ваш способ получения выплаты:\n\n"
        "Пример:\n"
        "• Qiwi: +79991234567\n"
        "• WebMoney: R123456789012\n"
        "• PayPal: email@example.com\n\n"
        "Отправьте реквизиты или /cancel для отмены"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await state.set_state(ReferralStates.entering_other_method)


@router.message(ReferralStates.entering_other_method)
async def process_other_method(message: Message, state: FSMContext):
    """Обработка другого способа"""
    details = message.text.strip()
    
    if len(details) < 5:
        await message.answer("⚠️ Слишком короткое описание. Укажите детали.")
        return
    
    # Сохраняем
    await db.set_payment_details(message.from_user.id, "other", details)
    
    text = (
        "✅ **Реквизиты сохранены!**\n\n"
        f"Способ: Другой\n"
        f"Реквизиты: `{details[:50]}...`\n\n"
        "Теперь вы можете запрашивать выплаты."
    )
    
    await message.answer(text, parse_mode="Markdown")
    await state.clear()


# ===== ОТМЕНА ВВОДА =====

@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    """Отмена текущего действия"""
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer("❌ Отменено")
