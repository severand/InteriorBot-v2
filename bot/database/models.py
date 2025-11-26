# bot/database/models.py

# ===== USERS TABLE =====
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER DEFAULT 3,
    reg_date DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

GET_USER = "SELECT * FROM users WHERE user_id = ?"
CREATE_USER = "INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)"
UPDATE_BALANCE = "UPDATE users SET balance = balance + ? WHERE user_id = ?"
DECREASE_BALANCE = "UPDATE users SET balance = balance - 1 WHERE user_id = ?"
GET_BALANCE = "SELECT balance FROM users WHERE user_id = ?"

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

# ===== ANALYTICS TABLE (НОВОЕ) =====
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

# Analytics queries
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
