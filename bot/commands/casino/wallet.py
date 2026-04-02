"""Persistent currency system — JSON-backed wallet store."""

import json
import threading
from pathlib import Path

import discord

CURRENCY_NAME = "Maka Flaschen"
CURRENCY_EMOJI = "🍷"  # 🥤
STARTING_BALANCE = 5000
MIN_BET = 10

_WALLET_PATH = Path(__file__).resolve().parents[3] / "data" / "wallets.json"
_lock = threading.Lock()


def tag_embed(embed: discord.Embed, member: discord.Member) -> discord.Embed:
    """Stamp an embed with the triggering user's name and avatar."""
    embed.set_author(
        name=member.display_name,
        icon_url=str(member.display_avatar.url),
    )
    return embed


def _load() -> dict:
    if not _WALLET_PATH.exists():
        return {}
    with open(_WALLET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    _WALLET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_WALLET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _ensure(data: dict, uid: str) -> None:
    if uid not in data:
        data[uid] = {"balance": STARTING_BALANCE}


def get_balance(user_id: int) -> int:
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        _save(data)
        return data[uid]["balance"]


def add_balance(user_id: int, amount: int) -> int:
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        data[uid]["balance"] += amount
        _save(data)
        return data[uid]["balance"]


def remove_balance(user_id: int, amount: int) -> int:
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        if data[uid]["balance"] < amount:
            raise ValueError("Insufficient balance")
        data[uid]["balance"] -= amount
        _save(data)
        return data[uid]["balance"]


def transfer(from_id: int, to_id: int, amount: int) -> tuple[int, int]:
    with _lock:
        data = _load()
        fid, tid = str(from_id), str(to_id)
        _ensure(data, fid)
        _ensure(data, tid)
        if data[fid]["balance"] < amount:
            raise ValueError("Insufficient balance")
        data[fid]["balance"] -= amount
        data[tid]["balance"] += amount
        _save(data)
        return data[fid]["balance"], data[tid]["balance"]


def get_cooldown(user_id: int, key: str) -> float | None:
    """Return the stored timestamp for a cooldown key, or None."""
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        return data[uid].get(key)


def set_cooldown(user_id: int, key: str, timestamp: float) -> None:
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        data[uid][key] = timestamp
        _save(data)


def force_remove_balance(user_id: int, amount: int) -> int:
    """Remove balance without a floor check — balance can go negative."""
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        data[uid]["balance"] -= amount
        _save(data)
        return data[uid]["balance"]


def set_balance(user_id: int, amount: int) -> int:
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        data[uid]["balance"] = amount
        _save(data)
        return amount


def delete_user(user_id: int) -> bool:
    """Remove a user from the wallet entirely. Returns True if they existed."""
    with _lock:
        data = _load()
        uid = str(user_id)
        if uid not in data:
            return False
        del data[uid]
        _save(data)
        return True


def everyone_broke() -> bool:
    """True if every tracked player has a balance of 0 or below."""
    data = _load()
    if not data:
        return False
    return all(info["balance"] <= 0 for info in data.values())


def reset_all_balances(amount: int) -> None:
    """Set every tracked player's balance to `amount`."""
    with _lock:
        data = _load()
        for uid in data:
            data[uid]["balance"] = amount
        _save(data)


def get_leaderboard(limit: int = 10) -> list[tuple[str, int]]:
    data = _load()
    ranked = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)
    return [(uid, info["balance"]) for uid, info in ranked[:limit]]


# ── Inventory helpers ──────────────────────────────────────────────────────────

def get_inventory(user_id: int) -> list:
    """Return a copy of the user's item inventory (list of item dicts)."""
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        return list(data[uid].get("inventory", []))


def add_item(user_id: int, item: dict) -> None:
    """Append an item dict to the user's inventory."""
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        data[uid].setdefault("inventory", []).append(item)
        _save(data)


def remove_item(user_id: int, item_id: str) -> dict | None:
    """Remove an item by its short id. Returns the removed item or None."""
    with _lock:
        data = _load()
        uid = str(user_id)
        _ensure(data, uid)
        inv = data[uid].get("inventory", [])
        for i, item in enumerate(inv):
            if item["id"] == item_id:
                removed = inv.pop(i)
                data[uid]["inventory"] = inv
                _save(data)
                return removed
        return None


def trade_items(
    from_id: int,
    to_id: int,
    from_item_ids: list[str],
    to_item_ids: list[str],
) -> bool:
    """Atomically swap items between two users.
    Returns False if any requested item is not found."""
    with _lock:
        data = _load()
        fid, tid = str(from_id), str(to_id)
        _ensure(data, fid)
        _ensure(data, tid)
        f_inv = data[fid].get("inventory", [])
        t_inv = data[tid].get("inventory", [])
        from_set = set(from_item_ids)
        to_set = set(to_item_ids)
        f_moving = [it for it in f_inv if it["id"] in from_set]
        t_moving = [it for it in t_inv if it["id"] in to_set]
        if len(f_moving) != len(from_item_ids) or len(t_moving) != len(to_item_ids):
            return False
        data[fid]["inventory"] = [it for it in f_inv if it["id"] not in from_set]
        data[tid]["inventory"] = [it for it in t_inv if it["id"] not in to_set]
        data[fid]["inventory"].extend(t_moving)
        data[tid]["inventory"].extend(f_moving)
        _save(data)
        return True


def resolve_bet(raw: str, user_id: int) -> int | None:
    """Parse a bet string into an integer amount based on the user's balance.

    Accepted formats:
      all / max / allin      → full balance
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


def get_all_inventories() -> dict[str, list]:
    """Return {uid: [items...]} for every user that has at least one item."""
    data = _load()
    return {
        uid: list(info.get("inventory", []))
        for uid, info in data.items()
        if info.get("inventory")
    }
