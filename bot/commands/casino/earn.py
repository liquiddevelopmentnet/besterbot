import random
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_cooldown, set_cooldown, add_balance, force_remove_balance,
    tag_embed, CURRENCY_EMOJI, CURRENCY_NAME,
)

_CET = ZoneInfo("Europe/Berlin")
_DAILY_AMOUNT = 10_000

# ── Earning data (mirrors the individual command files) ───────────────────────

_BEG_RESPONSES = [
    "A kind stranger took pity on you.",
    "Someone threw coins out of a car window.",
    "You found a crumpled bill on the ground.",
    "A tourist thought you were a street performer.",
    "An old lady gave you her grocery change.",
]

_JOBS = [
    ("🍔", "flipped burgers at McDonalds"),
    ("🚗", "drove Uber for a few hours"),
    ("💻", "fixed someone's printer"),
    ("🛒", "stacked shelves at Lidl"),
    ("📦", "sorted packages at Amazon"),
    ("🎸", "busked at the Hauptbahnhof"),
    ("🚚", "made DHL deliveries"),
    ("🧹", "cleaned an office building"),
]

_CATCHES = [
    (300,  600,  "🐟", "a small sardine"),
    (400,  800,  "🐠", "a tropical fish"),
    (500,  900,  "🦐", "a bag of shrimp"),
    (600, 1000,  "🦀", "a crab"),
    (800, 1200,  "🐡", "a pufferfish"),
    (600,  900,  "🥾", "an old boot (someone paid for the antique)"),
    (1000, 1200, "🦞", "a massive lobster"),
]

_SUCCESS_CRIMES = [
    "robbed a vending machine",
    "pickpocketed a tourist",
    "sold knockoff Gucci bags",
    "ran a shell game on tourists",
]
_FAIL_CRIMES = [
    "got caught shoplifting and fined",
    "tripped the alarm and had to pay damages",
    "your accomplice snitched on you",
]

_SUCCESS_SCAMS = [
    "ran a fake crypto ICO and cashed out",
    "sold an 'AI startup' to a gullible investor",
    "pulled off a Nigerian prince email scheme",
    "listed a non-existent apartment on Airbnb",
]
_FAIL_SCAMS = [
    "the mark was an undercover cop",
    "your phishing site got traced back to you",
    "you accidentally scammed a lawyer",
]

# ── Command metadata ──────────────────────────────────────────────────────────

# (cmd, key, cd_secs, gain_str, risk_str, desc, has_button)
_COMMANDS = [
    ("f.beg",   "last_beg",   120, "50 – 500",         "None",                    "Beg strangers for spare change",       True),
    ("f.fish",  "last_fish",  300, "300 – 1,200",       "None",                    "Cast a line and sell your catch",      True),
    ("f.work",  "last_work",  300, "500 – 1,500",       "None",                    "Pick up a random shift job",           True),
    ("f.steal", "last_steal", 300, "15–30% of target",  "45%: lose 20–40% of own", "Pickpocket another player",            False),
    ("f.crime", "last_crime", 600, "1,500 – 4,000",     "30%: lose 500–1,500",     "Pull off a street-level crime",        True),
    ("f.scam",  "last_scam",  600, "2,000 – 5,000",     "40%: lose 1,000–2,000",   "Run a high-risk con",                  True),
    ("f.daily", "last_daily", 0,   "10,000",            "None",                    "Collect your daily government handout",True),
]

_BUTTON_META = [
    ("beg",   "🙏", "Beg",   "last_beg",   120),
    ("fish",  "🎣", "Fish",  "last_fish",  300),
    ("work",  "💼", "Work",  "last_work",  300),
    ("crime", "🦹", "Crime", "last_crime", 600),
    ("scam",  "🤑", "Scam",  "last_scam",  600),
    ("daily", "🍾", "Daily", "last_daily", 0),
]

# ── Cooldown helpers ──────────────────────────────────────────────────────────

def _status(user_id: int, key: str, cd_secs: int) -> tuple[bool, int | None]:
    last = get_cooldown(user_id, key)
    if cd_secs == 0:                                         # daily: date-based
        today = datetime.now(tz=_CET).strftime("%Y-%m-%d")
        if last != today:
            return True, None
        midnight = (
            datetime.now(tz=_CET)
            .replace(hour=0, minute=0, second=0, microsecond=0)
            + timedelta(days=1)
        )
        return False, int(midnight.timestamp())
    if last is None:
        return True, None
    remaining = cd_secs - (time.time() - last)
    if remaining <= 0:
        return True, None
    return False, int(time.time() + remaining)

# ── Earning logic — returns (title, description, color, new_bal) ──────────────

def _run_beg(user_id: int) -> tuple[str, str, int, int]:
    earned = random.randint(50, 500)
    new_bal = add_balance(user_id, earned)
    set_cooldown(user_id, "last_beg", time.time())
    return (
        "🙏 Begging Complete",
        f"{random.choice(_BEG_RESPONSES)}\n+**{earned:,}** {CURRENCY_EMOJI}",
        0x95A5A6,
        new_bal,
    )


def _run_fish(user_id: int) -> tuple[str, str, int, int]:
    low, high, emoji, name = random.choice(_CATCHES)
    earned = random.randint(low, high)
    new_bal = add_balance(user_id, earned)
    set_cooldown(user_id, "last_fish", time.time())
    return (
        f"{emoji} Caught Something!",
        f"You reeled in **{name}** and sold it for **{earned:,}** {CURRENCY_EMOJI}.",
        0x3498DB,
        new_bal,
    )


def _run_work(user_id: int) -> tuple[str, str, int, int]:
    emoji, desc = random.choice(_JOBS)
    earned = random.randint(500, 1500)
    new_bal = add_balance(user_id, earned)
    set_cooldown(user_id, "last_work", time.time())
    return (
        f"{emoji} Work Complete",
        f"You {desc} and earned **{earned:,}** {CURRENCY_EMOJI}.",
        0x2ECC71,
        new_bal,
    )


def _run_crime(user_id: int) -> tuple[str, str, int, int]:
    set_cooldown(user_id, "last_crime", time.time())
    if random.random() < 0.70:
        earned = random.randint(1500, 4000)
        new_bal = add_balance(user_id, earned)
        return (
            "🦹 Crime Pays",
            f"You {random.choice(_SUCCESS_CRIMES)} and got away with **{earned:,}** {CURRENCY_EMOJI}.",
            0x2ECC71,
            new_bal,
        )
    else:
        lost = random.randint(500, 1500)
        new_bal = force_remove_balance(user_id, lost)
        return (
            "🚨 Busted!",
            f"You {random.choice(_FAIL_CRIMES)}. Fined **{lost:,}** {CURRENCY_EMOJI}.",
            0xE74C3C,
            new_bal,
        )


def _run_scam(user_id: int) -> tuple[str, str, int, int]:
    set_cooldown(user_id, "last_scam", time.time())
    if random.random() < 0.60:
        earned = random.randint(2000, 5000)
        new_bal = add_balance(user_id, earned)
        return (
            "🤑 Scam Successful",
            f"You {random.choice(_SUCCESS_SCAMS)}.\n+**{earned:,}** {CURRENCY_EMOJI}",
            0x2ECC71,
            new_bal,
        )
    else:
        lost = random.randint(1000, 2000)
        new_bal = force_remove_balance(user_id, lost)
        return (
            "🚔 Scam Backfired",
            f"You {random.choice(_FAIL_SCAMS)}.\n-**{lost:,}** {CURRENCY_EMOJI}",
            0xE74C3C,
            new_bal,
        )


def _run_daily(user_id: int) -> tuple[str, str, int, int]:
    today = datetime.now(tz=_CET).strftime("%Y-%m-%d")
    new_bal = add_balance(user_id, _DAILY_AMOUNT)
    set_cooldown(user_id, "last_daily", today)
    return (
        f"{CURRENCY_EMOJI} Daily Reward Claimed!",
        f"+**{_DAILY_AMOUNT:,}** {CURRENCY_NAME}",
        0x2ECC71,
        new_bal,
    )


_RUNNERS = {
    "beg":   _run_beg,
    "fish":  _run_fish,
    "work":  _run_work,
    "crime": _run_crime,
    "scam":  _run_scam,
    "daily": _run_daily,
}

# ── Embed builder ─────────────────────────────────────────────────────────────

def _build_embed(
    user_id: int,
    member: discord.Member,
    last_result: tuple[str, str, int, int] | None = None,
) -> discord.Embed:
    color = last_result[2] if last_result else 0xF1C40F
    embed = tag_embed(discord.Embed(
        title=f"{CURRENCY_EMOJI} Ways to Earn {CURRENCY_NAME}",
        color=color,
    ), member)

    if last_result:
        title, description, _, new_bal = last_result
        embed.add_field(
            name=f"▸ {title}",
            value=f"{description}\n**Balance: {new_bal:,}** {CURRENCY_EMOJI}",
            inline=False,
        )

    for cmd, key, cd_secs, gain, risk, desc, _ in _COMMANDS:
        available, ready_at = _status(user_id, key, cd_secs)
        status_line = "🟢 **Available now**" if available else f"🔴 Ready <t:{ready_at}:R>"
        risk_line   = f"⚠️ {risk}" if risk != "None" else "✅ No risk"
        embed.add_field(
            name=f"`{cmd}`  —  {desc}",
            value=f"💰 **{gain}** {CURRENCY_EMOJI}\n{risk_line}\n{status_line}",
            inline=True,
        )

    embed.set_footer(text="Higher risk = higher reward. Steal requires f.steal @user.")
    return embed

# ── View ──────────────────────────────────────────────────────────────────────

class EarnView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.member  = member
        self._refresh_buttons()

    def _refresh_buttons(self):
        self.clear_items()
        for btn_id, emoji, label, key, cd_secs in _BUTTON_META:
            available, _ = _status(self.user_id, key, cd_secs)
            btn = discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.success if available else discord.ButtonStyle.secondary,
                disabled=not available,
            )
            btn.callback = self._make_callback(btn_id, key, cd_secs)
            self.add_item(btn)

    def _make_callback(self, btn_id: str, key: str, cd_secs: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your earn menu!", ephemeral=True)
                return

            available, ready_at = _status(self.user_id, key, cd_secs)
            if not available:
                await interaction.response.send_message(
                    f"Still on cooldown — ready <t:{ready_at}:R>.", ephemeral=True
                )
                return

            result = _RUNNERS[btn_id](self.user_id)
            self._refresh_buttons()
            updated_embed = _build_embed(self.user_id, self.member, last_result=result)
            await interaction.response.edit_message(embed=updated_embed, view=self)

        return callback

# ── Command ───────────────────────────────────────────────────────────────────

@command("earn", description="Overview of all earning commands", usage="f.earn", category="Casino")
async def earn_command(message: Message, args: list[str]):
    embed = _build_embed(message.author.id, message.author)
    view  = EarnView(message.author.id, message.author)
    await message.channel.send(embed=embed, view=view)
