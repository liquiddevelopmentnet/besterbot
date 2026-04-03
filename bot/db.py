"""SQLite database — connection management and schema initialisation.

All persistent user data (balances, cooldowns, inventory items) lives here.
The JSON store (wallets.json) is the legacy format; use scripts/migrate.py to
import it once, then wallet.py takes over.

Thread safety
-------------
A single module-level connection is opened in WAL mode so concurrent reads
never block writes.  wallet.py wraps multi-step operations in a threading.Lock
(same pattern as before) to keep compound operations atomic.
"""

import sqlite3
import threading
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "besterbot.db"
_conn: sqlite3.Connection | None = None
_conn_lock = threading.Lock()


def get_db() -> sqlite3.Connection:
    """Return the shared database connection, opening it if necessary."""
    global _conn
    if _conn is None:
        with _conn_lock:
            if _conn is None:
                _conn = _open()
    return _conn


def _open() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(
        str(_DB_PATH),
        check_same_thread=False,
        isolation_level=None,   # autocommit — we manage transactions manually
    )
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")   # safe with WAL, faster than FULL
    _create_schema(conn)
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        BEGIN;

        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance INTEGER NOT NULL DEFAULT 5000
        );

        -- Flexible key/value store for all cooldown timestamps.
        -- Numeric timestamps (last_beg, last_fish, …) are stored as TEXT
        -- representations of floats; last_daily is stored as "YYYY-MM-DD".
        CREATE TABLE IF NOT EXISTS cooldowns (
            user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            key     TEXT NOT NULL,
            value   TEXT NOT NULL,
            PRIMARY KEY (user_id, key)
        );

        -- Each row is one inventory item belonging to a user.
        CREATE TABLE IF NOT EXISTS items (
            id         TEXT PRIMARY KEY,
            user_id    TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            weapon     TEXT NOT NULL,
            skin       TEXT NOT NULL,
            rarity     TEXT NOT NULL,
            float      REAL NOT NULL,
            wear       TEXT NOT NULL,
            wear_abbr  TEXT NOT NULL,
            pattern    INTEGER NOT NULL,
            stattrak   INTEGER NOT NULL DEFAULT 0,
            sell_price INTEGER NOT NULL,
            image_url  TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_items_user ON items(user_id);

        -- Cumulative gambling / earning income log for .bip graphs.
        -- Each row is one income event (earn, sell, game win, etc.).
        CREATE TABLE IF NOT EXISTS earnings (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            amount  INTEGER NOT NULL,
            ts      REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_earnings_user_ts ON earnings(user_id, ts);

        COMMIT;
    """)


def init_db() -> None:
    """Ensure the database is open and the schema exists.

    Call this once at bot startup (main.py) before any wallet operations.
    """
    get_db()
