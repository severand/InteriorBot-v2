# bot/database/models.py

# ===== USERS TABLE (РАСШИРЕННАЯ) =====
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 3,
    reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    referral_code TEXT UNIQUE,
    referred_by INTEGER,
    referrals_count INTEGER DEFAULT 0,
    FOREIGN KEY (referred_by) REFERENCES users (user_id)
)
"""

# === НОВЫЕ ПОЛЯ ДЛЯ СТАТИСТИКИ И РЕФЕРАЛЮНОЙ ПРОГРАММЫ ===
# Выполнять при миграции базы:
ALTER_USERS_ADD_STATS = """
ALTER TABLE users ADD COLUMN total_generations INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN successful_payments INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN total_spent INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN referral_balance INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN referral_total_earned INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN referral_total_paid INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN payment_method TEXT;
ALTER TABLE users ADD COLUMN payment_details TEXT;
ALTER TABLE users ADD COLUMN sbp_bank TEXT;
"""

GET_USER = "SELECT * FROM users WHERE user_id = ?"
CREATE_USER = "INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)"
UPDATE_BALANCE = "UPDATE users SET balance = balance + ? WHERE user_id = ?"
DECREASE_BALANCE = "UPDATE users SET balance = balance - 1 WHERE user_id = ?"
GET_BALANCE = "SELECT balance FROM users WHERE user_id = ?"

# === РЕФЕРАЛЬНЫЕ ЗАПРОСЫ ===
GET_USER_BY_REFERRAL_CODE = "SELECT * FROM users WHERE referral_code = ?"
UPDATE_REFERRAL_CODE = "UPDATE users SET referral_code = ? WHERE user_id = ?"
UPDATE_REFERRED_BY = "UPDATE users SET referred_by = ? WHERE user_id = ?"
INCREMENT_REFERRALS_COUNT = "UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?"
GET_REFERRALS_COUNT = "SELECT referrals_count FROM users WHERE user_id = ?"

# ===== PAYMENTS TABLE =====
CREATE_PAYMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    yookassa_payment_id TEXT UNIQUE NOT NULL,
    amount INTEGER NOT NULL,
    tokens INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
"""

CREATE_PAYMENT = """
INSERT INTO payments (user_id, yookassa_payment_id, amount, tokens, status)
VALUES (?, ?, ?, ?, ?)
"""
GET_PENDING_PAYMENT = "SELECT * FROM payments WHERE user_id = ? AND status = 'pending' ORDER BY created_at DESC LIMIT 1"
UPDATE_PAYMENT_STATUS = "UPDATE payments SET status = ? WHERE yookassa_payment_id = ?"

# ===== ANALYTICS TABLE =====
CREATE_ANALYTICS_TABLE = """
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT,
    room TEXT,
    style TEXT,
    status TEXT,
    cost REAL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
"""

LOG_ANALYTICS = """
INSERT INTO analytics (user_id, action, room, style, status, cost)
VALUES (?, ?, ?, ?, ?, ?)
"""

GET_ANALYTICS_TODAY = "SELECT * FROM analytics WHERE DATE(created_at) = DATE('now') ORDER BY created_at DESC"
GET_ANALYTICS_WEEK = "SELECT * FROM analytics WHERE created_at >= datetime('now', '-7 days') ORDER BY created_at DESC"
GET_ANALYTICS_MONTH = "SELECT * FROM analytics WHERE created_at >= datetime('now', '-30 days') ORDER BY created_at DESC"
GET_ALL_ANALYTICS = "SELECT * FROM analytics ORDER BY created_at DESC LIMIT 1000"

GET_TOTAL_USERS = "SELECT COUNT(*) FROM users"
GET_NEW_USERS_TODAY = "SELECT COUNT(*) FROM users WHERE DATE(reg_date) = DATE('now')"
GET_NEW_USERS_WEEK = "SELECT COUNT(*) FROM users WHERE reg_date >= datetime('now', '-7 days')"
GET_NEW_USERS_MONTH = "SELECT COUNT(*) FROM users WHERE reg_date >= datetime('now', '-30 days')"

GET_TOTAL_GENERATIONS = "SELECT COUNT(*) FROM analytics WHERE action = 'generation'"
GET_GENERATIONS_TODAY = "SELECT COUNT(*) FROM analytics WHERE action = 'generation' AND DATE(created_at) = DATE('now')"

GET_TOTAL_REVENUE = "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'succeeded'"
GET_REVENUE_TODAY = "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'succeeded' AND DATE(created_at) = DATE('now')"
GET_REVENUE_WEEK = "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'succeeded' AND created_at >= datetime('now', '-7 days')"
GET_REVENUE_MONTH = "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = 'succeeded' AND created_at >= datetime('now', '-30 days')"

GET_POPULAR_ROOMS = "SELECT room, COUNT(*) as count FROM analytics WHERE action = 'generation' GROUP BY room ORDER BY count DESC"
GET_POPULAR_STYLES = "SELECT style, COUNT(*) as count FROM analytics WHERE action = 'generation' GROUP BY style ORDER BY count DESC"

GET_ALL_USERS = "SELECT user_id, username, balance, reg_date FROM users ORDER BY reg_date DESC"

# ===== SETTINGS TABLE =====
CREATE_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

DEFAULT_SETTINGS = [
    ("welcome_bonus", "3"),
    ("referral_bonus_inviter", "2"),
    ("referral_bonus_invited", "2"),
    ("referral_enabled", "1"),
    ("referral_commission_percent", "10"),
    ("referral_min_payout", "500"),
    ("referral_exchange_rate", "29"),
]

GET_SETTING = "SELECT value FROM settings WHERE key = ?"
SET_SETTING = "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)"
GET_ALL_SETTINGS = "SELECT * FROM settings"

# ===== PAYMENT PACKAGES TABLE (НОВОЕ) =====
CREATE_PAYMENT_PACKAGES_TABLE = """
CREATE TABLE IF NOT EXISTS payment_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tokens INTEGER NOT NULL,
    price INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    is_featured INTEGER DEFAULT 0,
    discount_percent INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

DEFAULT_PACKAGES = [
    (10, 290, '10 генераций', '', 1, 0, 0, 1),
    (25, 490, '25 генераций', '', 1, 1, 0, 2),
    (60, 990, '60 генераций', '', 1, 0, 0, 3),
]

GET_ACTIVE_PACKAGES = "SELECT * FROM payment_packages WHERE is_active = 1 ORDER BY sort_order"
GET_PACKAGE_BY_ID = "SELECT * FROM payment_packages WHERE id = ?"
CREATE_PACKAGE = "INSERT INTO payment_packages (tokens, price, name, description, sort_order) VALUES (?, ?, ?, ?, ?)"
UPDATE_PACKAGE = "UPDATE payment_packages SET tokens = ?, price = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
TOGGLE_PACKAGE_STATUS = "UPDATE payment_packages SET is_active = NOT is_active WHERE id = ?"

# ===== REFERRAL EARNINGS TABLE (НОВОЕ) =====
CREATE_REFERRAL_EARNINGS_TABLE = """
CREATE TABLE IF NOT EXISTS referral_earnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER NOT NULL,
    referred_id INTEGER NOT NULL,
    payment_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    commission_percent INTEGER NOT NULL,
    earnings INTEGER NOT NULL,
    tokens_given INTEGER NOT NULL,
    status TEXT DEFAULT 'credited',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users (user_id),
    FOREIGN KEY (referred_id) REFERENCES users (user_id)
)
"""

LOG_REFERRAL_EARNING = """
INSERT INTO referral_earnings (referrer_id, referred_id, payment_id, amount, commission_percent, earnings, tokens_given)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

GET_USER_REFERRAL_EARNINGS = "SELECT * FROM referral_earnings WHERE referrer_id = ? ORDER BY created_at DESC"
GET_TOTAL_REFERRAL_STATS = """
SELECT 
    COUNT(*) as total_referrals,
    COALESCE(SUM(earnings), 0) as total_earnings,
    COALESCE(SUM(tokens_given), 0) as total_tokens
FROM referral_earnings
"""

# ===== REFERRAL EXCHANGES TABLE (НОВОЕ) =====
CREATE_REFERRAL_EXCHANGES_TABLE = """
CREATE TABLE IF NOT EXISTS referral_exchanges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    tokens INTEGER NOT NULL,
    exchange_rate INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
"""

LOG_REFERRAL_EXCHANGE = """
INSERT INTO referral_exchanges (user_id, amount, tokens, exchange_rate)
VALUES (?, ?, ?, ?)
"""

GET_USER_EXCHANGES = "SELECT * FROM referral_exchanges WHERE user_id = ? ORDER BY created_at DESC LIMIT 20"
GET_TOTAL_EXCHANGES_STATS = """
SELECT 
    COUNT(*) as count,
    COALESCE(SUM(amount), 0) as total_amount,
    COALESCE(SUM(tokens), 0) as total_tokens
FROM referral_exchanges
"""

# ===== REFERRAL PAYOUTS TABLE (НОВОЕ) =====
CREATE_REFERRAL_PAYOUTS_TABLE = """
CREATE TABLE IF NOT EXISTS referral_payouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    payment_method TEXT,
    payment_details TEXT,
    status TEXT DEFAULT 'pending',
    admin_note TEXT,
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    processed_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
"""

CREATE_PAYOUT_REQUEST = """
INSERT INTO referral_payouts (user_id, amount, payment_method, payment_details)
VALUES (?, ?, ?, ?)
"""

GET_PENDING_PAYOUTS = "SELECT * FROM referral_payouts WHERE status = 'pending' ORDER BY requested_at ASC"
GET_USER_PAYOUTS = "SELECT * FROM referral_payouts WHERE user_id = ? ORDER BY requested_at DESC LIMIT 20"
UPDATE_PAYOUT_STATUS = """
UPDATE referral_payouts 
SET status = ?, processed_at = CURRENT_TIMESTAMP, processed_by = ?, admin_note = ?
WHERE id = ?
"""

GET_PAYOUT_STATS = """
SELECT
    COUNT(*) as total_payouts,
    COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as total_paid,
    COALESCE(SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END), 0) as pending_amount
FROM referral_payouts
"""
