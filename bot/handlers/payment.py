# payment

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.db import db
from keyboards.inline import get_payment_check_keyboard, get_payment_keyboard, get_main_menu_keyboard
from utils.texts import PAYMENT_CREATED, PAYMENT_SUCCESS_TEXT, PAYMENT_ERROR_TEXT, MAIN_MENU_TEXT
from services.payment_api import create_payment_yookassa, find_payment

router = Router()
logger = logging.getLogger(__name__)

# ✅ НОВАЯ ФУНКЦИЯ: Конвертация рублей в генерации
async def _convert_earnings_to_tokens(earnings_rub: int) -> int:
    """
    Конвертирует реферальное вознаграждение в рублях в генерации.
    Курс из settings: referral_exchange_rate (руб за 1 генерацию). Дефолт 29.
    """
    try:
        rate_raw = await db.get_setting("referral_exchange_rate")
        rate = int(rate_raw) if rate_raw else 29
        if rate <= 0:
            rate = 29
    except Exception:
        rate = 29

    tokens = earnings_rub // rate
    if tokens < 1 and earnings_rub > 0:
        tokens = 1
    return tokens

# ✅ НОВАЯ ФУНКЦИЯ: Начисление комиссии рефереру
async def _process_referral_commission(user_id: int, payment_id: str, amount: int, purchased_tokens: int):
    """
    Начисляет комиссию рефереру при успешной оплате.
    - Проверяет включена ли программа
    - Находит реферера
    - Начисляет рубли на реф. баланс + генерации на основной баланс
    - Логирует в referral_earnings
    """
    try:
        # 1. Проверяем включена ли программа
        enabled = await db.get_setting("referral_enabled")
        if str(enabled or "1") != "1":
            logger.info(f"[REFERRAL] Программа отключена, пропускаем")
            return

        # 2. Получаем данные покупателя
        user = await db.get_user_data(user_id)
        if not user:
            logger.info(f"[REFERRAL] User {user_id} не найден")
            return

        referrer_id = user.get("referred_by")
        if not referrer_id:
            logger.info(f"[REFERRAL] User {user_id} не имеет реферера")
            return

        # 3. Получаем % комиссии
        percent_raw = await db.get_setting("referral_commission_percent")
        commission_percent = int(percent_raw) if percent_raw is not None else 10
        if commission_percent <= 0:
            logger.info(f"[REFERRAL] Комиссия 0%, пропускаем")
            return

        # 4. Рассчитываем заработок в рублях
        earnings = int(amount * commission_percent / 100)
        logger.info(f"[REFERRAL] Расчёт: {amount} руб * {commission_percent}% = {earnings} руб")

        if earnings <= 0:
            logger.info(f"[REFERRAL] Заработок 0 руб, пропускаем")
            return

        # 5. Начисляем рубли на реферальный баланс
        await db.add_referral_balance(referrer_id, earnings)
        logger.info(f"[REFERRAL] Начислено {earnings} руб на реф. баланс реферера {referrer_id}")

        # 6. Конвертируем в генерации (дополнительная мотивация)
        tokens_to_give = await _convert_earnings_to_tokens(earnings)
        logger.info(f"[REFERRAL] Конвертация: {earnings} руб = {tokens_to_give} генераций")

        if tokens_to_give > 0:
            await db.add_tokens(referrer_id, tokens_to_give)
            logger.info(f"[REFERRAL] Начислено {tokens_to_give} генераций рефереру {referrer_id}")

        # 7. Логируем доход
        await db.log_referral_earning(
            referrer_id=referrer_id,
            referred_id=user_id,
            payment_id=payment_id,
            amount=amount,
            commission_percent=commission_percent,
            earnings=earnings,
            tokens=tokens_to_give
        )
        logger.info(f"[REFERRAL] ✅ Запись в referral_earnings создана")

    except Exception as e:
        logger.error(f"[REFERRAL] ❌ Ошибка при начислении комиссии: {e}", exc_info=True)


@router.callback_query(F.data == "buy_generations")
async def show_packages(callback: CallbackQuery):
    """Показать пакеты генераций с возвратом к главному меню"""
    await callback.message.edit_text(
        "Выберите пакет генераций:",
        reply_markup=get_payment_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    """Возврат к главному меню из экрана оплаты"""
    await callback.message.edit_text(
        MAIN_MENU_TEXT,
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay_"))
async def create_payment(callback: CallbackQuery):
    """Создать платеж в ЮКассе"""
    # Парсим данные из кнопки (pay_10_290) -> tokens=10, price=290
    _, tokens, price = callback.data.split("_")
    user_id = callback.from_user.id
    amount = int(price)
    tokens_amount = int(tokens)
    payment_data = create_payment_yookassa(amount, user_id, tokens_amount)
    if not payment_data:
        await callback.answer("Ошибка создания платежа", show_alert=True)
        return
    await db.create_payment(
        user_id=user_id,
        payment_id=payment_data['id'],
        amount=payment_data['amount'],
        tokens=payment_data['tokens']
    )
    await callback.message.edit_text(
        PAYMENT_CREATED.format(
            amount=amount,
            tokens=tokens_amount
        ),
        reply_markup=get_payment_check_keyboard(payment_data['confirmation_url'])
    )
    await callback.answer()

@router.callback_query(F.data == "check_payment")
async def check_payment(callback: CallbackQuery):
    """Проверить статус платежа + возврат к главному меню"""
    user_id = callback.from_user.id
    last_payment = await db.get_last_pending_payment(user_id)
    if not last_payment:
        await callback.answer("Нет активных платежей для проверки.", show_alert=True)
        return
    
    is_paid = find_payment(last_payment['yookassa_payment_id'])
    
    if is_paid:
        # ✅ НАЧИСЛЯЕМ ТОКЕНЫ ПОКУПАТЕЛЮ
        await db.set_payment_success(last_payment['yookassa_payment_id'])
        await db.add_tokens(user_id, last_payment['tokens'])
        
        # ✅ НОВОЕ: НАЧИСЛЯЕМ КОМИССИЮ РЕФЕРЕРУ
        await _process_referral_commission(
            user_id=user_id,
            payment_id=last_payment['yookassa_payment_id'],
            amount=last_payment['amount'],
            purchased_tokens=last_payment['tokens']
        )
        
        await callback.message.edit_text(
            PAYMENT_SUCCESS_TEXT.format(balance=await db.get_balance(user_id)),
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await callback.answer(PAYMENT_ERROR_TEXT, show_alert=True)

@router.callback_query(F.data == "show_profile")
async def show_profile_payment(callback: CallbackQuery):
    from keyboards.inline import get_profile_keyboard
    from utils.texts import PROFILE_TEXT
    user_id = callback.from_user.id
    balance = await db.get_balance(user_id)
    username = callback.from_user.username or "Не указано"
    await callback.message.edit_text(
        PROFILE_TEXT.format(
            user_id=user_id,
            username=username,
            balance=balance,
            reg_date="Недавно"
        ),
        reply_markup=get_profile_keyboard()
    )
    await callback.answer()
