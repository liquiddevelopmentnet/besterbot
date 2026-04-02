"""Persistent currency system — SQLite-backed wallet store.

Public API is identical to the previous JSON-backed version so that no
command file needs to change.  Internal I/O now goes through bot.db instead
of reading/writing wallets.json on every call.
"""

import threading

import discord

from bot.db import get_db

CURRENCY_NAME    = "Maka Flaschen"
CURRENCY_EMOJI   = "🍷"
STARTING_BALANCE = 5000
MIN_BET          = 10

# Single write-lock — same pattern as before.  Keeps compound operations
# (transfer, trade_items, …) fully atomic even though SQLite itself is
# thread-safe in WAL mode.
_lock = threading.Lock()


# ── Helpers ───────────────────────────────────────────────────────────────────

def tag_embed(embed: discord.Embed, member: discord.Member) -> discord.Embed:
    """Stamp an embed with the triggering user's name and avatar."""
    embed.set_author(
        name=member.display_name,
        icon_url=str(member.display_avatar.url),
    )
    return embed


def _ensure(uid: str) -> None:
    """Insert a new user row with the starting balance if one does not exist."""
    get_db().execute(
        "INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, ?)",
        (uid, STARTING_BALANCE),
    )


def _item_row_to_dict(row: tuple) -> dict:
    """Convert a DB row (from items SELECT *) to the legacy item dict format."""
    return {
        "id":         row[0],
        # row[1] is user_id — omitted from the public dict
        "weapon":     row[2],
        "skin":       row[3],
        "rarity":     row[4],
        "float":      row[5],
        "wear":       row[6],
        "wear_abbr":  row[7],
        "pattern":    row[8],
        "stattrak":   bool(row[9]),
        "sell_price": row[10],
        "image_url":  row[11],
    }


# ── Balance ───────────────────────────────────────────────────────────────────

def get_balance(user_id: int) -> int:
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        row = get_db().execute(
            "SELECT balance FROM users WHERE user_id = ?", (uid,)
        ).fetchone()
        return row[0]


def add_balance(user_id: int, amount: int) -> int:
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        get_db().execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, uid),
        )
        row = get_db().execute(
            "SELECT balance FROM users WHERE user_id = ?", (uid,)
        ).fetchone()
        return row[0]


def remove_balance(user_id: int, amount: int) -> int:
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        row = get_db().execute(
            "SELECT balance FROM users WHERE user_id = ?", (uid,)
        ).fetchone()
        if row[0] < amount:
            raise ValueError("Insufficient balance")
        get_db().execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
            (amount, uid),
        )
        return row[0] - amount


def force_remove_balance(user_id: int, amount: int) -> int:
    """Remove balance without a floor check — balance can go negative."""
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        get_db().execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
            (amount, uid),
        )
        row = get_db().execute(
            "SELECT balance FROM users WHERE user_id = ?", (uid,)
        ).fetchone()
        return row[0]


def set_balance(user_id: int, amount: int) -> int:
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        get_db().execute(
            "UPDATE users SET balance = ? WHERE user_id = ?",
            (amount, uid),
        )
        return amount


def transfer(from_id: int, to_id: int, amount: int) -> tuple[int, int]:
    with _lock:
        db  = get_db()
        fid = str(from_id)
        tid = str(to_id)
        _ensure(fid)
        _ensure(tid)
        row = db.execute(
            "SELECT balance FROM users WHERE user_id = ?", (fid,)
        ).fetchone()
        if row[0] < amount:
            raise ValueError("Insufficient balance")
        db.execute("BEGIN")
        try:
            db.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                (amount, fid),
            )
            db.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, tid),
            )
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        f_bal = db.execute(
            "SELECT balance FROM users WHERE user_id = ?", (fid,)
        ).fetchone()[0]
        t_bal = db.execute(
            "SELECT balance FROM users WHERE user_id = ?", (tid,)
        ).fetchone()[0]
        return f_bal, t_bal


def delete_user(user_id: int) -> bool:
    """Remove a user and all their data.  Returns True if they existed."""
    with _lock:
        uid = str(user_id)
        cur = get_db().execute(
            "DELETE FROM users WHERE user_id = ?", (uid,)
        )
        return cur.rowcount > 0


def everyone_broke() -> bool:
    """True if every tracked player has a balance of 0 or below."""
    row = get_db().execute("SELECT COUNT(*) FROM users").fetchone()
    if row[0] == 0:
        return False
    broke = get_db().execute(
        "SELECT COUNT(*) FROM users WHERE balance > 0"
    ).fetchone()
    return broke[0] == 0


def reset_all_balances(amount: int) -> None:
    """Set every tracked player's balance to `amount`."""
    with _lock:
        get_db().execute("UPDATE users SET balance = ?", (amount,))


def get_leaderboard(limit: int = 10) -> list[tuple[str, int]]:
    rows = get_db().execute(
        "SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [(row[0], row[1]) for row in rows]


def get_leaderboard_with_worth(limit: int = 10) -> list[tuple[str, int, int]]:
    """Return (user_id, balance, inv_worth) sorted by total wealth descending."""
    rows = get_db().execute(
        """SELECT u.user_id,
                  u.balance,
                  COALESCE(SUM(i.sell_price), 0) AS inv_worth
           FROM users u
           LEFT JOIN items i ON i.user_id = u.user_id
           GROUP BY u.user_id
           ORDER BY (u.balance + COALESCE(SUM(i.sell_price), 0)) DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    return [(row[0], row[1], row[2]) for row in rows]


# ── Cooldowns ─────────────────────────────────────────────────────────────────

def get_cooldown(user_id: int, key: str) -> float | str | None:
    """Return the stored cooldown value for a key, or None.

    Numeric timestamps are returned as float; last_daily is returned as str.
    """
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        row = get_db().execute(
            "SELECT value FROM cooldowns WHERE user_id = ? AND key = ?",
            (uid, key),
        ).fetchone()
        if row is None:
            return None
        raw = row[0]
        # last_daily is stored as "YYYY-MM-DD" — keep it a string
        if key == "last_daily":
            return raw
        try:
            return float(raw)
        except ValueError:
            return raw


def set_cooldown(user_id: int, key: str, timestamp: float | str) -> None:
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        get_db().execute(
            """INSERT INTO cooldowns (user_id, key, value) VALUES (?, ?, ?)
               ON CONFLICT(user_id, key) DO UPDATE SET value = excluded.value""",
            (uid, key, str(timestamp)),
        )


# ── Inventory ─────────────────────────────────────────────────────────────────

def get_inventory(user_id: int) -> list:
    """Return a list of item dicts for the user."""
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        rows = get_db().execute(
            "SELECT * FROM items WHERE user_id = ? ORDER BY rowid",
            (uid,),
        ).fetchall()
        return [_item_row_to_dict(r) for r in rows]


def add_item(user_id: int, item: dict) -> None:
    """Insert an item dict into the user's inventory."""
    with _lock:
        uid = str(user_id)
        _ensure(uid)
        get_db().execute(
            """INSERT INTO items
               (id, user_id, weapon, skin, rarity, float, wear, wear_abbr,
                pattern, stattrak, sell_price, image_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                item["id"],
                uid,
                item["weapon"],
                item["skin"],
                item["rarity"],
                item["float"],
                item["wear"],
                item["wear_abbr"],
                item["pattern"],
                int(item["stattrak"]),
                item["sell_price"],
                item.get("image_url"),
            ),
        )


def remove_item(user_id: int, item_id: str) -> dict | None:
    """Remove an item by its short id.  Returns the removed item or None."""
    with _lock:
        uid = str(user_id)
        row = get_db().execute(
            "SELECT * FROM items WHERE id = ? AND user_id = ?",
            (item_id, uid),
        ).fetchone()
        if row is None:
            return None
        get_db().execute("DELETE FROM items WHERE id = ?", (item_id,))
        return _item_row_to_dict(row)


def trade_items(
    from_id: int,
    to_id: int,
    from_item_ids: list[str],
    to_item_ids: list[str],
) -> bool:
    """Atomically swap items between two users.
    Returns False if any requested item is not found.
    """
    with _lock:
        db  = get_db()
        fid = str(from_id)
        tid = str(to_id)
        _ensure(fid)
        _ensure(tid)

        # Verify all items exist and belong to the correct owners
        f_rows = db.execute(
            f"SELECT * FROM items WHERE user_id = ? AND id IN ({','.join('?' * len(from_item_ids))})",
            (fid, *from_item_ids),
        ).fetchall()
        t_rows = db.execute(
            f"SELECT * FROM items WHERE user_id = ? AND id IN ({','.join('?' * len(to_item_ids))})",
            (tid, *to_item_ids),
        ).fetchall()

        if len(f_rows) != len(from_item_ids) or len(t_rows) != len(to_item_ids):
            return False

        db.execute("BEGIN")
        try:
            # Re-assign from_id's items to to_id
            if from_item_ids:
                db.execute(
                    f"UPDATE items SET user_id = ? WHERE id IN ({','.join('?' * len(from_item_ids))})",
                    (tid, *from_item_ids),
                )
            # Re-assign to_id's items to from_id
            if to_item_ids:
                db.execute(
                    f"UPDATE items SET user_id = ? WHERE id IN ({','.join('?' * len(to_item_ids))})",
                    (fid, *to_item_ids),
                )
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise

        return True


def get_all_inventories() -> dict[str, list]:
    """Return {uid: [items…]} for every user that has at least one item."""
    rows = get_db().execute("SELECT * FROM items ORDER BY user_id, rowid").fetchall()
    result: dict[str, list] = {}
    for row in rows:
        uid = row[1]
        result.setdefault(uid, []).append(_item_row_to_dict(row))
    return result


# ── Bet helper ────────────────────────────────────────────────────────────────

def resolve_bet(raw: str, user_id: int) -> int | None:
    """Parse a bet string into an integer amount based on the user's balance.

    Accepted formats:
      all / max / allin / a  → full balance
      half                   → 50 % of balance
      min                    → MIN_BET
      50% / 25% / 75% …      → that percentage of balance
      1234                   → exact number

    Returns None if the string is not recognised.
    """
    bal = get_balance(user_id)
    s   = raw.strip().lower()

    if s in ("all", "max", "allin", "a"):
        return max(bal, 0)
    if s in ("half",):
        return max(bal // 2, 0)
    if s in ("min",):
        return MIN_BET
    if s.endswith("%"):
        try:
            pct = float(s[:-1])
            if 0 < pct <= 100:
                return max(int(bal * pct / 100), 0)
        except ValueError:
            pass
    if s.isdigit():
        return int(s)
    return None
