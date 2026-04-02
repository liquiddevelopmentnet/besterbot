"""CS2-style item definitions and utilities shared across case commands."""
import json
import random
import uuid
from pathlib import Path

# ── External data files ───────────────────────────────────────────────────────
_DATA = Path(__file__).resolve().parents[3] / "data"

with open(_DATA / "skin_list.json",   encoding="utf-8") as _f:
    _SKIN_LIST: dict[str, list] = json.load(_f)   # {"lightblue": [[w, s], ...], ...}

with open(_DATA / "skin_images.json", encoding="utf-8") as _f:
    _SKIN_IMAGES: dict[str, str] = json.load(_f)  # {"Weapon|Skin": "url", ...}

# ── Gloves never have StatTrak in CS2 ─────────────────────────────────────────
_GLOVE_WEAPONS: frozenset[str] = frozenset({
    "Sport Gloves",
    "Driver Gloves",
    "Hand Wraps",
    "Moto Gloves",
    "Specialist Gloves",
    "Hydra Gloves",
    "Bloodhound Gloves",
})

# ── Rarity definitions ────────────────────────────────────────────────────────
RARITIES: dict[str, dict] = {
    "lightblue": {
        "name":       "Mil-Spec",
        "emoji":      "🔷",
        "color":      0x4FC3F7,
        "label":      "Mil-Spec Grade",
        "weight":     6500,   # 65 %
        "sell_range": (30, 150),
    },
    "blue": {
        "name":       "Restricted",
        "emoji":      "🟦",
        "color":      0x4169E1,
        "label":      "Restricted",
        "weight":     2500,   # 25 %
        "sell_range": (150, 700),
    },
    "purple": {
        "name":       "Classified",
        "emoji":      "🟪",
        "color":      0x8A2BE2,
        "label":      "Classified",
        "weight":     600,    #  6 %
        "sell_range": (700, 3000),
    },
    "pink": {
        "name":       "Covert",
        "emoji":      "🌸",
        "color":      0xFF69B4,
        "label":      "Covert",
        "weight":     300,    #  3 %
        "sell_range": (3000, 15000),
    },
    "gold": {
        "name":       "Rare Special",
        "emoji":      "⭐",
        "color":      0xFFD700,
        "label":      "★ Rare Special",
        "weight":     100,    #  1 %
        "sell_range": (15000, 80000),
    },
}

RARITY_ORDER: list[str] = ["lightblue", "blue", "purple", "pink", "gold"]

WEAR_RANGES: list[tuple] = [
    (0.00, 0.07, "Factory New",    "FN"),
    (0.07, 0.15, "Minimal Wear",   "MW"),
    (0.15, 0.38, "Field-Tested",   "FT"),
    (0.38, 0.45, "Well-Worn",      "WW"),
    (0.45, 1.00, "Battle-Scarred", "BS"),
]

# Convert loaded lists to tuples for consistency
SKINS: dict[str, list[tuple]] = {
    tier: [tuple(pair) for pair in pairs]
    for tier, pairs in _SKIN_LIST.items()
}


# ── Core helpers ──────────────────────────────────────────────────────────────

def roll_rarity() -> str:
    total = sum(r["weight"] for r in RARITIES.values())
    roll  = random.randint(1, total)
    cumulative = 0
    for key in RARITY_ORDER:
        cumulative += RARITIES[key]["weight"]
        if roll <= cumulative:
            return key
    return "lightblue"


def float_to_wear(f: float) -> tuple[str, str]:
    for lo, hi, name, abbr in WEAR_RANGES:
        if lo <= f < hi:
            return name, abbr
    return "Battle-Scarred", "BS"


def calc_sell_price(rarity: str, float_val: float, stattrak: bool) -> int:
    """Deterministic sell price: low float → higher price, StatTrak → +50 %."""
    lo, hi = RARITIES[rarity]["sell_range"]
    price  = int(hi - (hi - lo) * float_val)
    if stattrak:
        price = int(price * 1.5)
    return max(price, 10)


def create_item(rarity: str | None = None) -> dict:
    """Generate a complete random item dict."""
    if rarity is None:
        rarity = roll_rarity()
    weapon, skin = random.choice(SKINS[rarity])
    f = round(random.uniform(0.0, 1.0), 6)
    wear_name, wear_abbr = float_to_wear(f)
    # Gloves never have StatTrak in CS2
    st = (random.random() < 0.2) if weapon not in _GLOVE_WEAPONS else False
    return {
        "id":         str(uuid.uuid4())[:8],
        "weapon":     weapon,
        "skin":       skin,
        "rarity":     rarity,
        "float":      f,
        "wear":       wear_name,
        "wear_abbr":  wear_abbr,
        "pattern":    random.randint(1, 999),
        "stattrak":   st,
        "sell_price": calc_sell_price(rarity, f, st),
        "image_url":  _SKIN_IMAGES.get(f"{weapon}|{skin}", ""),
    }


def item_full_name(item: dict) -> str:
    st = "StatTrak™ " if item["stattrak"] else ""
    return f"{st}{item['weapon']} | {item['skin']} ({item['wear_abbr']})"
