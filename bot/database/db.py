# bot/database/db.py

import aiosqlite
from typing import Optional, Dict, Any, List
import logging
import secrets

from config import config
from database.models import (
    CREATE_USERS_TABLE,
    CREATE_PAYMENTS_TABLE,
    CREATE_ANALYTICS_TABLE,
    CREATE_SETTINGS_TABLE,
    CREATE_PAYMENT_PACKAGES_TABLE,
    CREATE_REFERRAL_EARNINGS_TABLE,
    CREATE_REFERRAL_EXCHANGES_TABLE,
    CREATE_REFERRAL_PAYOUTS_TABLE,
    DEFAULT_SETTINGS,
    DEFAULT_PACKAGES,
    GET_USER,
    CREATE_USER,
    UPDATE_BALANCE,
    DECREASE_BALANCE,
    GET_BALANCE,
    CREATE_PAYMENT,
    GET_PENDING_PAYMENT,
    UPDATE_PAYMENT_STATUS,
    LOG_ANALYTICS,
    GET_TOTAL_USERS,
    GET_NEW_USERS_TODAY,
    GET_NEW_USERS_WEEK,
    GET_NEW_USERS_MONTH,
    GET_TOTAL_GENERATIONS,
    GET_GENERATIONS_TODAY,
    GET_TOTAL_REVENUE,
    GET_REVENUE_TODAY,
    GET_REVENUE_WEEK,
    GET_REVENUE_MONTH,
    GET_POPULAR_ROOMS,
    GET_POPULAR_STYLES,
    GET_ALL_USERS,
    GET_USER_BY_REFERRAL_CODE,
    UPDATE_REFERRAL_CODE,
    UPDATE_REFERRED_BY,
    INCREMENT_REFERRALS_COUNT,
    GET_REFERRALS_COUNT,
    GET_SETTING,
    SET_SETTING,
    GET_ALL_SETTINGS,
    GET_ACTIVE_PACKAGES,
    GET_PACKAGE_BY_ID,
    CREATE_PACKAGE,
    UPDATE_PACKAGE,
    TOGGLE_PACKAGE_STATUS,
    LOG_REFERRAL_EARNING,
    GET_USER_REFERRAL_EARNINGS,
    GET_TOTAL_REFERRAL_STATS,
    LOG_REFERRAL_EXCHANGE,
    GET_USER_EXCHANGES,
    GET_TOTAL_EXCHANGES_STATS,
    CREATE_PAYOUT_REQUEST,
    GET_PENDING_PAYOUTS,
    GET_USER_PAYOUTS,
    UPDATE_PAYOUT_STATUS,
    GET_PAYOUT_STATS,
)

logger = logging.getLogger(__name__)


class Database:
    """Асинхронный класс для работы с базой данных"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных со всеми таблицами"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_USERS_TABLE)
            await db.execute(CREATE_PAYMENTS_TABLE)
            await db.execute(CREATE_ANALYTICS_TABLE)
            await db.execute(CREATE_SETTINGS_TABLE)
            await db.execute(CREATE_PAYMENT_PACKAGES_TABLE)
            await db.execute(CREATE_REFERRAL_EARNINGS_TABLE)
            await db.execute(CREATE_REFERRAL_EXCHANGES_TABLE)
            await db.execute(CREATE_REFERRAL_PAYOUTS_TABLE)
            await db.commit()
            
            # Инициализация дефолтных настроек
            for key, value in DEFAULT_SETTINGS:
                await db.execute(SET_SETTING, (key, value))
            await db.commit()
            
            # Инициализация дефолтных пакетов
            for pkg in DEFAULT_PACKAGES:
                await db.execute(
                    "INSERT OR IGNORE INTO payment_packages (tokens, price, name, description, is_active, is_featured, discount_percent, sort_order) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    pkg
                )
            await db.commit()
            
            logger.info("✅ Database initialized with all tables")

    async def init_analytics_table(self):
        """Инициализация таблицы аналитики"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_ANALYTICS_TABLE)
            await db.commit()
            logger.info("✅ Analytics table initialized")

    # ===== СУЩЕСТВУЮЩИЕ МЕТОДЫ (НЕ ИЗМЕНЯТЬ) =====

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_USER, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def create_user(self, user_id: int, username: Optional[str] = None, referrer_code: Optional[str] = None) -> bool:
        """
        Создать нового пользователя с реферальной системой
        
        Args:
            user_id: ID пользователя
            username: Имя пользователя
            referrer_code: Реферальный код того, кто пригласил
        """
        user_exists = await self.get_user(user_id)
        if user_exists:
            return False

        # Получаем начальный баланс из настроек
        welcome_bonus = int(await self.get_setting("welcome_bonus") or "3")
        initial_balance = welcome_bonus

        async with aiosqlite.connect(self.db_path) as db:
            # Создаём пользователя
            await db.execute(CREATE_USER, (user_id, username, initial_balance))
            
            # Генерируем уникальный реферальный код
            ref_code = secrets.token_urlsafe(8)
            await db.execute(UPDATE_REFERRAL_CODE, (ref_code, user_id))
            
            await db.commit()
            
            # Если есть реферер, обрабатываем реферальную систему
            if referrer_code:
                await self.process_referral(user_id, referrer_code)
            
            return True

    async def process_referral(self, new_user_id: int, referrer_code: str):
        """
        Обработка реферальной системы
        Добавляет бонусы обоим пользователям
        """
        referrer = await self.get_user_by_referral_code(referrer_code)
        if not referrer:
            return False
        
        referrer_id = referrer['user_id']
        
        # Получаем бонусы из настроек
        inviter_bonus = int(await self.get_setting("referral_bonus_inviter") or "2")
        invited_bonus = int(await self.get_setting("referral_bonus_invited") or "2")
        
        async with aiosqlite.connect(self.db_path) as db:
            # Устанавливаем referred_by для нового пользователя
            await db.execute(UPDATE_REFERRED_BY, (referrer_id, new_user_id))
            
            # Увеличиваем счётчик рефералов у реферера
            await db.execute(INCREMENT_REFERRALS_COUNT, (referrer_id,))
            
            # Добавляем бонусы
            await db.execute(UPDATE_BALANCE, (inviter_bonus, referrer_id))
            await db.execute(UPDATE_BALANCE, (invited_bonus, new_user_id))
            
            await db.commit()
            
            logger.info(f"✅ Referral processed: {referrer_id} invited {new_user_id}")
            return True

    async def get_user_by_referral_code(self, referral_code: str) -> Optional[Dict[str, Any]]:
        """Получить пользователя по реферальному коду"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_USER_BY_REFERRAL_CODE, (referral_code,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_referrals_count(self, user_id: int) -> int:
        """Получить количество рефералов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_REFERRALS_COUNT, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row and row[0] else 0

    # === МЕТОДЫ ДЛЯ НАСТРОЕК ===
    
    async def get_setting(self, key: str) -> Optional[str]:
        """Получить значение настройки"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_SETTING, (key,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def set_setting(self, key: str, value: str) -> bool:
        """Установить значение настройки"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(SET_SETTING, (key, value))
            await db.commit()
            return True

    async def get_all_settings(self) -> Dict[str, str]:
        """Получить все настройки"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_ALL_SETTINGS) as cursor:
                rows = await cursor.fetchall()
                return {row['key']: row['value'] for row in rows}

    async def get_balance(self, user_id: int) -> int:
        """Получить баланс пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_BALANCE, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def increase_balance(self, user_id: int, amount: int) -> bool:
        """Увеличить баланс пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(UPDATE_BALANCE, (amount, user_id))
            await db.commit()
            return True

    async def decrease_balance(self, user_id: int) -> bool:
        """Уменьшить баланс пользователя на 1"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(DECREASE_BALANCE, (user_id,))
            await db.commit()
            return True

    async def create_payment(self, user_id: int, payment_id: str,
                             amount: int, tokens: int) -> bool:
        """Создать запись о платеже"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(CREATE_PAYMENT,
                                 (user_id, payment_id, amount, tokens, 'pending'))
                await db.commit()
                return True
        except Exception:
            return False

    async def get_pending_payment(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить последний пендинг платёж пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_PENDING_PAYMENT, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def update_payment_status(self, payment_id: str, status: str) -> bool:
        """Обновить статус платежа"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(UPDATE_PAYMENT_STATUS, (status, payment_id))
            await db.commit()
            return True

    # ===== ANALYTICS METHODS =====

    async def log_analytics(self, user_id: int, action: str, room: str = None,
                           style: str = None, status: str = "success", cost: float = 1):
        """Залогировать действие пользователя в аналитику"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(LOG_ANALYTICS, (user_id, action, room, style, status, cost))
            await db.commit()

    async def get_total_users(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_TOTAL_USERS) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_new_users_today(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_NEW_USERS_TODAY) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_new_users_week(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_NEW_USERS_WEEK) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_new_users_month(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_NEW_USERS_MONTH) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_total_generations(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_TOTAL_GENERATIONS) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_generations_today(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_GENERATIONS_TODAY) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_total_revenue(self) -> float:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_TOTAL_REVENUE) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_revenue_today(self) -> float:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_REVENUE_TODAY) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_revenue_week(self) -> float:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_REVENUE_WEEK) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_revenue_month(self) -> float:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_REVENUE_MONTH) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_popular_rooms(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_POPULAR_ROOMS) as cursor:
                return await cursor.fetchall()

    async def get_popular_styles(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_POPULAR_STYLES) as cursor:
                return await cursor.fetchall()

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_ALL_USERS) as cursor:
                return await cursor.fetchall()

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ PAYMENT PACKAGES =====

    async def get_active_packages(self) -> List[Dict[str, Any]]:
        """Получить активные пакеты"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_ACTIVE_PACKAGES) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_package_by_id(self, package_id: int) -> Optional[Dict[str, Any]]:
        """Получить пакет по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_PACKAGE_BY_ID, (package_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_package(self, tokens: int, price: int, name: str, description: str = "", sort_order: int = 0) -> int:
        """Создать новый пакет"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(CREATE_PACKAGE, (tokens, price, name, description, sort_order))
            await db.commit()
            return cursor.lastrowid

    async def update_package(self, package_id: int, tokens: int, price: int) -> bool:
        """Обновить пакет"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(UPDATE_PACKAGE, (tokens, price, package_id))
            await db.commit()
            return True

    async def toggle_package_status(self, package_id: int) -> bool:
        """Включить/отключить пакет"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(TOGGLE_PACKAGE_STATUS, (package_id,))
            await db.commit()
            return True

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ REFERRAL EARNINGS =====

    async def log_referral_earning(self, referrer_id: int, referred_id: int, payment_id: str,
                                   amount: int, commission_percent: int, earnings: int, tokens_given: int) -> bool:
        """Залогировать заработок реферера"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(LOG_REFERRAL_EARNING, 
                           (referrer_id, referred_id, payment_id, amount, commission_percent, earnings, tokens_given))
            await db.commit()
            return True

    async def get_user_referral_earnings(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить историю заработков реферера"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_USER_REFERRAL_EARNINGS, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_total_referral_stats(self) -> Dict[str, Any]:
        """Общая статистика реферальной программы"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_TOTAL_REFERRAL_STATS) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else {'total_referrals': 0, 'total_earnings': 0, 'total_tokens': 0}

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ REFERRAL EXCHANGES =====

    async def log_referral_exchange(self, user_id: int, amount: int, tokens: int, exchange_rate: int) -> bool:
        """Залогировать обмен реферального баланса на генерации"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(LOG_REFERRAL_EXCHANGE, (user_id, amount, tokens, exchange_rate))
            await db.commit()
            return True

    async def get_user_exchanges(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить историю обменов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_USER_EXCHANGES, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_total_exchanges_stats(self) -> Dict[str, Any]:
        """Статистика всех обменов"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_TOTAL_EXCHANGES_STATS) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else {'count': 0, 'total_amount': 0, 'total_tokens': 0}

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ REFERRAL PAYOUTS =====

    async def create_payout_request(self, user_id: int, amount: int, payment_method: str, payment_details: str) -> int:
        """Создать заявку на выплату"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(CREATE_PAYOUT_REQUEST, (user_id, amount, payment_method, payment_details))
            await db.commit()
            return cursor.lastrowid

    async def get_pending_payouts(self) -> List[Dict[str, Any]]:
        """Получить все ожидающие выплаты"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_PENDING_PAYOUTS) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_user_payouts(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить историю выплат пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_USER_PAYOUTS, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def update_payout_status(self, payout_id: int, status: str, admin_id: int, note: str = "") -> bool:
        """Обновить статус выплаты"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(UPDATE_PAYOUT_STATUS, (status, admin_id, note, payout_id))
            await db.commit()
            return True

    async def get_payout_stats(self) -> Dict[str, Any]:
        """Статистика выплат"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_PAYOUT_STATS) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else {'total_payouts': 0, 'total_paid': 0, 'pending_amount': 0}

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С РЕФЕРАЛЬНЫМ БАЛАНСОМ =====

    async def get_referral_balance(self, user_id: int) -> int:
        """Получить реферальный баланс (руб)"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COALESCE(referral_balance, 0) FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def add_referral_balance(self, user_id: int, amount: int) -> bool:
        """Добавить к реферальному балансу"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET referral_balance = COALESCE(referral_balance, 0) + ?, "
                "referral_total_earned = COALESCE(referral_total_earned, 0) + ? "
                "WHERE user_id = ?",
                (amount, amount, user_id)
            )
            await db.commit()
            return True

    async def decrease_referral_balance(self, user_id: int, amount: int) -> bool:
        """Уменьшить реферальный баланс"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET referral_balance = COALESCE(referral_balance, 0) - ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()
            return True

    async def get_user_total_earned(self, user_id: int) -> int:
        """Получить общую сумму заработка реферера"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COALESCE(referral_total_earned, 0) FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ СТАТИСТИКИ ПОЛЬЗОВАТЕЛЯ =====

    async def increment_user_generations(self, user_id: int) -> bool:
        """Увеличить счётчик генераций"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET total_generations = COALESCE(total_generations, 0) + 1 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
            return True

    async def increment_user_payments(self, user_id: int) -> bool:
        """Увеличить счётчик оплат"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET successful_payments = COALESCE(successful_payments, 0) + 1 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
            return True

    async def add_to_total_spent(self, user_id: int, amount: int) -> bool:
        """Добавить к общей сумме потраченного"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET total_spent = COALESCE(total_spent, 0) + ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()
            return True

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить полную статистику пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT total_generations, successful_payments, total_spent, "
                "referral_balance, referral_total_earned, referrals_count "
                "FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return {
                    'total_generations': 0,
                    'successful_payments': 0,
                    'total_spent': 0,
                    'referral_balance': 0,
                    'referral_total_earned': 0,
                    'referrals_count': 0
                }

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ РЕКВИЗИТОВ =====

    async def set_payment_details(self, user_id: int, method: str, details: str, sbp_bank: str = None) -> bool:
        """Установить реквизиты для выплат"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET payment_method = ?, payment_details = ?, sbp_bank = ? WHERE user_id = ?",
                (method, details, sbp_bank, user_id)
            )
            await db.commit()
            return True

    async def get_payment_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить реквизиты пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT payment_method, payment_details, sbp_bank FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    # ===== Legacy methods for compatibility =====
    
    async def get_last_pending_payment(self, user_id: int):
        return await self.get_pending_payment(user_id)

    async def set_payment_success(self, payment_id: str) -> bool:
        return await self.update_payment_status(payment_id, 'succeeded')

    async def add_tokens(self, user_id: int, tokens: int) -> bool:
        return await self.increase_balance(user_id, tokens)

    async def get_user_data(self, user_id: int):
        return await self.get_user(user_id)


# Инициализация БД
db = Database(config.DB_PATH)
