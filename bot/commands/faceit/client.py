"""Shared Faceit API helpers used across faceit commands."""

import os

import requests
from faceit import Faceit, EnvKey

data = Faceit.data(EnvKey("FACEIT_KEY"))

LEVEL_COLORS = {
    1: 0xEEEEEE, 2: 0x1CE400, 3: 0x1CE400, 4: 0x1CE400,
    5: 0xF4E009, 6: 0xF4E009, 7: 0xF4E009,
    8: 0xFF6309, 9: 0xFF6309, 10: 0xFF0F0F,
}

LEVEL_BARS = {
    1: "█░░░░░░░░░", 2: "██░░░░░░░░", 3: "███░░░░░░░",
    4: "████░░░░░░", 5: "█████░░░░░", 6: "██████░░░░",
    7: "███████░░░", 8: "████████░░", 9: "█████████░",
    10: "██████████",
}


def get_ongoing_match(player_id: str) -> dict | None:
    headers = {"Authorization": f"Bearer {os.getenv('FACEIT_KEY')}"}
    try:
        r = requests.get(
            f"https://open.faceit.com/data/v4/players/{player_id}/history",
            headers=headers,
            params={"game": "cs2", "type": "ongoing", "limit": 1},
            timeout=5,
        )
        items = r.json().get("items", [])
        if not items:
            return None

        match_id = items[0]["match_id"]
        match_r = requests.get(
            f"https://open.faceit.com/data/v4/matches/{match_id}",
            headers=headers,
            timeout=5,
        )
        return match_r.json()
    except Exception as e:
        print(f"[get_ongoing_match] {e}")
        return None
