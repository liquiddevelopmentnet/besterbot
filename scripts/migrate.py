"""One-time migration: wallets.json → SQLite (besterbot.db).

Usage (run from the project root):
    python scripts/migrate.py

Safety guarantees
-----------------
1. A timestamped backup of wallets.json is created in data/backups/ BEFORE
   anything is written to the database.  If the backup fails the script
   aborts immediately.
2. The migration runs inside a single SQLite transaction.  If any row fails
   the whole import is rolled back and the database is left untouched.
3. The script is idempotent: re-running it will not create duplicate rows
   (INSERT OR IGNORE is used throughout).
4. After import, user count, item count, and total balance are compared
   between the JSON source and the database.  Any mismatch is reported and
   the script exits with code 1.

The original wallets.json is never modified or deleted.
"""

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT       = Path(__file__).resolve().parents[1]
JSON_PATH  = ROOT / "data" / "wallets.json"
DB_PATH    = ROOT / "data" / "besterbot.db"
BACKUP_DIR = ROOT / "data" / "backups"


# ── Step 1: Backup ────────────────────────────────────────────────────────────

def backup_json() -> Path:
    if not JSON_PATH.exists():
        print(f"[SKIP] {JSON_PATH} does not exist — nothing to migrate.")
        sys.exit(0)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp       = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"wallets_{stamp}.json"

    shutil.copy2(JSON_PATH, backup_path)
    print(f"[OK]   Backup written -> {backup_path}")
    return backup_path


# ── Step 2: Load JSON ─────────────────────────────────────────────────────────

def load_wallets() -> dict:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Step 3: Ensure schema ─────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    balance INTEGER NOT NULL DEFAULT 5000
);

CREATE TABLE IF NOT EXISTS cooldowns (
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    key     TEXT NOT NULL,
    value   TEXT NOT NULL,
    PRIMARY KEY (user_id, key)
);

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
"""

COOLDOWN_KEYS = {
    "last_daily",
    "last_beg",
    "last_fish",
    "last_work",
    "last_crime",
    "last_scam",
    "last_steal",
}


def open_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA)
    return conn


# ── Step 4: Migrate ───────────────────────────────────────────────────────────

def migrate(wallets: dict, conn: sqlite3.Connection) -> None:
    """Insert all users, cooldowns, and items inside one transaction."""
    users_inserted    = 0
    cooldowns_inserted = 0
    items_inserted    = 0
    items_skipped     = 0

    conn.execute("BEGIN")
    try:
        for uid, data in wallets.items():
            balance = data.get("balance", 5000)

            # --- users ---
            cur = conn.execute(
                "INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)",
                (uid, balance),
            )
            users_inserted += cur.rowcount

            # --- cooldowns ---
            for key in COOLDOWN_KEYS:
                if key in data:
                    cur = conn.execute(
                        """INSERT OR IGNORE INTO cooldowns (user_id, key, value)
                           VALUES (?, ?, ?)""",
                        (uid, key, str(data[key])),
                    )
                    cooldowns_inserted += cur.rowcount

            # --- inventory items ---
            for item in data.get("inventory", []):
                item_id = item.get("id")
                if not item_id:
                    print(f"  [WARN] User {uid}: item missing 'id', skipping.")
                    items_skipped += 1
                    continue

                cur = conn.execute(
                    """INSERT OR IGNORE INTO items
                       (id, user_id, weapon, skin, rarity, float, wear,
                        wear_abbr, pattern, stattrak, sell_price, image_url)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        item_id,
                        uid,
                        item.get("weapon", ""),
                        item.get("skin", ""),
                        item.get("rarity", ""),
                        item.get("float", 0.0),
                        item.get("wear", ""),
                        item.get("wear_abbr", ""),
                        item.get("pattern", 0),
                        int(item.get("stattrak", False)),
                        item.get("sell_price", 0),
                        item.get("image_url"),
                    ),
                )
                if cur.rowcount:
                    items_inserted += 1
                else:
                    items_skipped += 1

        conn.execute("COMMIT")

    except Exception as exc:
        conn.execute("ROLLBACK")
        print(f"[FAIL] Migration rolled back due to error: {exc}")
        raise

    print(f"[OK]   Users inserted:     {users_inserted}")
    print(f"[OK]   Cooldowns inserted: {cooldowns_inserted}")
    print(f"[OK]   Items inserted:     {items_inserted}")
    if items_skipped:
        print(f"[WARN] Items skipped:      {items_skipped}")


# ── Step 5: Verify ────────────────────────────────────────────────────────────

def verify(wallets: dict, conn: sqlite3.Connection) -> bool:
    """Compare source JSON totals against the database. Returns True if OK."""
    ok = True

    # User count
    src_users = len(wallets)
    db_users  = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if src_users != db_users:
        print(f"[FAIL] User count mismatch: JSON={src_users}  DB={db_users}")
        ok = False
    else:
        print(f"[OK]   User count matches: {db_users}")

    # Item count
    src_items = sum(len(d.get("inventory", [])) for d in wallets.values())
    db_items  = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    if src_items != db_items:
        print(f"[FAIL] Item count mismatch: JSON={src_items}  DB={db_items}")
        ok = False
    else:
        print(f"[OK]   Item count matches: {db_items}")

    # Total balance
    src_balance = sum(d.get("balance", 0) for d in wallets.values())
    db_balance  = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM users").fetchone()[0]
    if src_balance != db_balance:
        print(f"[FAIL] Balance mismatch: JSON={src_balance}  DB={db_balance}")
        ok = False
    else:
        print(f"[OK]   Total balance matches: {db_balance}")

    return ok


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 55)
    print("  BesterBot - wallets.json -> SQLite migration")
    print("=" * 55)

    # 1. Backup first — abort if it fails
    try:
        backup_json()
    except Exception as exc:
        print(f"[FAIL] Could not create backup: {exc}")
        print("       Aborting — database was NOT modified.")
        sys.exit(1)

    # 2. Load source data
    wallets = load_wallets()
    print(f"[OK]   Loaded {len(wallets)} users from wallets.json")

    # 3. Open / initialise DB
    conn = open_db()
    print(f"[OK]   Database ready at {DB_PATH}")

    # 4. Migrate
    migrate(wallets, conn)

    # 5. Verify
    print()
    print("Verifying integrity...")
    success = verify(wallets, conn)
    conn.close()

    print()
    if success:
        print("[DONE] Migration successful.  The bot can now use besterbot.db.")
        print(f"       Your data backup is at: {BACKUP_DIR}/")
    else:
        print("[WARN] Integrity check failed — review the output above.")
        print("       Your original wallets.json is unchanged.")
        sys.exit(1)


if __name__ == "__main__":
    main()
