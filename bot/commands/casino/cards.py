"""Shared card & deck utilities for blackjack and poker."""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass

SUITS = ["\u2660", "\u2665", "\u2666", "\u2663"]  # ♠♥♦♣
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


@dataclass
class Card:
    rank: str
    suit: str

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    @property
    def bj_value(self) -> int:
        if self.rank in ("J", "Q", "K"):
            return 10
        if self.rank == "A":
            return 11
        return int(self.rank)

    @property
    def poker_rank(self) -> int:
        return RANKS.index(self.rank)


class Deck:
    def __init__(self, n: int = 1) -> None:
        self.cards = [Card(r, s) for _ in range(n) for s in SUITS for r in RANKS]
        random.shuffle(self.cards)

    def deal(self, n: int = 1) -> list[Card]:
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt


# ── Blackjack helpers ─────────────────────────

def bj_total(hand: list[Card]) -> int:
    total = sum(c.bj_value for c in hand)
    aces = sum(1 for c in hand if c.rank == "A")
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def hand_str(cards: list[Card]) -> str:
    return " ".join(f"`{c}`" for c in cards)


# ── Poker evaluation ─────────────────────────

POKER_PAYOUTS: dict[int, tuple[int, str]] = {
    9: (500, "Royal Flush"),    # 500x — legendary hand deserves a legendary payout
    8: (50,  "Straight Flush"),
    7: (25,  "Four of a Kind"),
    6: (9,   "Full House"),
    5: (6,   "Flush"),
    4: (4,   "Straight"),
    3: (3,   "Three of a Kind"),
    2: (2,   "Two Pair"),
    1: (1,   "Jacks or Better"),
    0: (1,   "Any Pair"),       # Low pair now returns the bet — no more losing on a pair
    -1: (0,  "High Card"),
}


def evaluate_poker(cards: list[Card]) -> tuple[int, str]:
    """Return (rank_key, hand_name). Higher rank_key = better hand."""
    ranks = sorted([c.poker_rank for c in cards], reverse=True)
    suits = [c.suit for c in cards]

    is_flush = len(set(suits)) == 1

    unique = sorted(set(ranks), reverse=True)
    is_straight = (
        len(unique) == 5
        and (unique[0] - unique[4] == 4)
    )
    # Ace-low straight (A-2-3-4-5)
    if not is_straight and set(ranks) == {12, 3, 2, 1, 0}:
        is_straight = True

    counts = Counter(ranks)
    freq = sorted(counts.values(), reverse=True)

    if is_flush and is_straight:
        return (9, "Royal Flush") if ranks[0] == 12 else (8, "Straight Flush")
    if freq == [4, 1]:
        return (7, "Four of a Kind")
    if freq == [3, 2]:
        return (6, "Full House")
    if is_flush:
        return (5, "Flush")
    if is_straight:
        return (4, "Straight")
    if freq == [3, 1, 1]:
        return (3, "Three of a Kind")
    if freq == [2, 2, 1]:
        return (2, "Two Pair")
    if freq == [2, 1, 1, 1]:
        pair_rank = [r for r, c in counts.items() if c == 2][0]
        if pair_rank >= 9:  # J, Q, K, A
            return (1, "Jacks or Better")
        return (0, "Low Pair")
    return (-1, "High Card")
