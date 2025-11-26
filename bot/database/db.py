# bot/database/db.py

import aiosqlite
from typing import Optional, Dict, Any
import logging

from config import config
from database.models import (
    CREATE_USERS_TABLE,
    CREATE_PAYMENTS_TABLE,
    CREATE_ANALYTICS_TABLE,
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
)

logger = logging.getLogger(__name__)


class Database:
    """Async database operations handler"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_USERS_TABLE)
            await db.execute(CREATE_PAYMENTS_TABLE)
            await db.commit()
            logger.info("✅ Database initialized")

    async def init_analytics_table(self):
        """Initialize analytics table"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_ANALYTICS_TABLE)
            await db.commit()
            logger.info("✅ Analytics table initialized")

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_USER, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def create_user(self, user_id: int, username: Optional[str] = None) -> bool:
        """Create new user if not exists"""
        user_exists = await self.get_user(user_id)
        if user_exists:
            return False

        initial_balance = config.FREE_GENERATIONS

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(CREATE_USER, (user_id, username, initial_balance))
            await db.commit()
            return True

    async def get_balance(self, user_id: int) -> int:
        """Get user's current balance"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_BALANCE, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def increase_balance(self, user_id: int, amount: int) -> bool:
        """Increase user's balance"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(UPDATE_BALANCE, (amount, user_id))
            await db.commit()
            return True

    async def decrease_balance(self, user_id: int) -> bool:
        """Decrease user's balance by 1"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(DECREASE_BALANCE, (user_id,))
            await db.commit()
            return True

    async def create_payment(self, user_id: int, payment_id: str,
                             amount: int, tokens: int) -> bool:
        """Create new payment record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(CREATE_PAYMENT,
                                 (user_id, payment_id, amount, tokens, 'pending'))
                await db.commit()
                return True
        except Exception:
            return False

    async def get_pending_payment(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's last pending payment"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_PENDING_PAYMENT, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def update_payment_status(self, payment_id: str, status: str) -> bool:
        """Update payment status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(UPDATE_PAYMENT_STATUS, (status, payment_id))
            await db.commit()
            return True

    # ===== ANALYTICS METHODS =====

    async def log_analytics(self, user_id: int, action: str, room: str = None,
                           style: str = None, status: str = "success", cost: float = 1):
        """Log user action to analytics"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(LOG_ANALYTICS, (user_id, action, room, style, status, cost))
            await db.commit()

    async def get_total_users(self) -> int:
        """Get total number of users"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_TOTAL_USERS) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_new_users_today(self) -> int:
        """Get new users registered today"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_NEW_USERS_TODAY) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_new_users_week(self) -> int:
        """Get new users registered this week"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_NEW_USERS_WEEK) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_new_users_month(self) -> int:
        """Get new users registered this month"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_NEW_USERS_MONTH) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_total_generations(self) -> int:
        """Get total generations"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_TOTAL_GENERATIONS) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_generations_today(self) -> int:
        """Get generations today"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_GENERATIONS_TODAY) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_total_revenue(self) -> float:
        """Get total revenue"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_TOTAL_REVENUE) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_revenue_today(self) -> float:
        """Get revenue today"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_REVENUE_TODAY) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_revenue_week(self) -> float:
        """Get revenue this week"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_REVENUE_WEEK) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_revenue_month(self) -> float:
        """Get revenue this month"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(GET_REVENUE_MONTH) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def get_popular_rooms(self):
        """Get most popular rooms"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_POPULAR_ROOMS) as cursor:
                return await cursor.fetchall()

    async def get_popular_styles(self):
        """Get most popular styles"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(GET_POPULAR_STYLES) as cursor:
                return await cursor.fetchall()

    async def get_all_users(self):
        """Get all users"""
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
