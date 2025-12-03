# bot/database/db.py

import aiosqlite
from typing import Optional, Dict, Any
import logging
import secrets

from config import config
from database.models import (
    CREATE_USERS_TABLE,
    CREATE_PAYMENTS_TABLE,
    CREATE_ANALYTICS_TABLE,
    CREATE_SETTINGS_TABLE,
    DEFAULT_SETTINGS,
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
    # === НОВЫЕ ИМПОРТЫ ===
    GET_USER_BY_REFERRAL_CODE,
    UPDATE_REFERRAL_CODE,
    UPDATE_REFERRED_BY,
    INCREMENT_REFERRALS_COUNT,
    GET_REFERRALS_COUNT,
    GET_SETTING,
    SET_SETTING,
    GET_ALL_SETTINGS,
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
            await db.commit()
            
            # Инициализация дефолтных настроек
            for key, value in DEFAULT_SETTINGS:
                await db.execute(SET_SETTING, (key, value))
            await db.commit()
            
            logger.info("✅ Database initialized with all tables")

    async def init_analytics_table(self):
        """Инициализация таблицы аналитики"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_ANALYTICS_TABLE)
            await db.commit()
            logger.info("✅ Analytics table initialized")

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

    # === СУЩЕСТВУЮЩИЕ МЕТОДЫ (НЕ ИЗМЕНЯТЬ) ===

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

    # Legacy methods for compatibility
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
