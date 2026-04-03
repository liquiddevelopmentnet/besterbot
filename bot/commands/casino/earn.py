import random
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_cooldown, set_cooldown, add_balance, force_remove_balance,
    log_earning, tag_embed, CURRENCY_EMOJI, CURRENCY_NAME,
)
from bot.strings import Earn as S

_CET = ZoneInfo("Europe/Berlin")
_DAILY_AMOUNT = 30_000

# ── Command metadata ──────────────────────────────────────────────────────────

# Static keys/cooldowns/has_button paired with display strings from S.COMMANDS_META
# S.COMMANDS_META: (cmd, gain_str, risk_str, desc)
_CMD_KEYS = [
    # (cmd,            key,                  cd_secs, has_button)
    ("f.beg",           "last_beg",           240,   True),
    ("f.fish",          "last_fish",          600,   True),
    ("f.work",          "last_work",          600,   True),
    ("f.steal",         "last_steal",         600,   False),
    ("f.crime",         "last_crime",         1200,  True),
    ("f.scam",          "last_scam",          1200,  True),
    ("f.daily",         "last_daily",         0,     True),
    ("f.finanzspritze", "last_finanzspritze", 3600,  True),
]

# (cmd, key, cd_secs, gain_str, risk_str, desc, has_button)
_COMMANDS = [
    (cmd, key, cd_secs, gain, risk, desc, has_btn)
    for (cmd, key, cd_secs, has_btn), (_, gain, risk, desc)
    in zip(_CMD_KEYS, S.COMMANDS_META)
]

_BUTTON_META = [
    ("beg",           "🙏", "Beg",          "last_beg",           240),
    ("fish",          "🎣", "Fish",         "last_fish",          600),
    ("work",          "💼", "Work",         "last_work",          600),
    ("crime",         "🦹", "Crime",        "last_crime",         1200),
    ("scam",          "🤑", "Scam",         "last_scam",          1200),
    ("daily",         "🍾", "Daily",        "last_daily",         0),
    ("finanzspritze", "💶", "Finanzspritze","last_finanzspritze",  3600),
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
    earned = random.randint(500, 2500)
    new_bal = add_balance(user_id, earned)
    log_earning(user_id, earned)
    set_cooldown(user_id, "last_beg", time.time())
    return (
        S.BEG_TITLE,
        S.BEG_DESC.format(response=random.choice(S.BEG_RESPONSES), earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
        0x95A5A6,
        new_bal,
    )


def _run_fish(user_id: int) -> tuple[str, str, int, int]:
    low, high, emoji, name = random.choice(S.CATCHES)
    earned = random.randint(low, high)
    new_bal = add_balance(user_id, earned)
    log_earning(user_id, earned)
    set_cooldown(user_id, "last_fish", time.time())
    return (
        S.FISH_TITLE.format(emoji=emoji),
        S.FISH_DESC.format(name=name, earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
        0x3498DB,
        new_bal,
    )


def _run_work(user_id: int) -> tuple[str, str, int, int]:
    emoji, desc = random.choice(S.JOBS)
    earned = random.randint(2000, 5000)
    new_bal = add_balance(user_id, earned)
    log_earning(user_id, earned)
    set_cooldown(user_id, "last_work", time.time())
    return (
        S.WORK_TITLE.format(emoji=emoji),
        S.WORK_DESC.format(desc=desc, earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
        0x2ECC71,
        new_bal,
    )


def _run_crime(user_id: int) -> tuple[str, str, int, int]:
    set_cooldown(user_id, "last_crime", time.time())
    if random.random() < 0.70:
        earned = random.randint(8000, 13000)
        new_bal = add_balance(user_id, earned)
        log_earning(user_id, earned)
        return (
            S.CRIME_SUCCESS_TITLE,
            S.CRIME_SUCCESS_DESC.format(crime=random.choice(S.SUCCESS_CRIMES), earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
            0x2ECC71,
            new_bal,
        )
    else:
        lost = random.randint(1000, 2000)
        new_bal = force_remove_balance(user_id, lost)
        return (
            S.CRIME_FAIL_TITLE,
            S.CRIME_FAIL_DESC.format(crime=random.choice(S.FAIL_CRIMES), lost=lost, CURRENCY_EMOJI=CURRENCY_EMOJI),
            0xE74C3C,
            new_bal,
        )


def _run_scam(user_id: int) -> tuple[str, str, int, int]:
    set_cooldown(user_id, "last_scam", time.time())
    if random.random() < 0.60:
        earned = random.randint(10000, 16000)
        new_bal = add_balance(user_id, earned)
        log_earning(user_id, earned)
        return (
            S.SCAM_SUCCESS_TITLE,
            S.SCAM_SUCCESS_DESC.format(scam=random.choice(S.SUCCESS_SCAMS), earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
            0x2ECC71,
            new_bal,
        )
    else:
        lost = random.randint(1000, 2500)
        new_bal = force_remove_balance(user_id, lost)
        return (
            S.SCAM_FAIL_TITLE,
            S.SCAM_FAIL_DESC.format(scam=random.choice(S.FAIL_SCAMS), lost=lost, CURRENCY_EMOJI=CURRENCY_EMOJI),
            0xE74C3C,
            new_bal,
        )


def _run_daily(user_id: int) -> tuple[str, str, int, int]:
    today = datetime.now(tz=_CET).strftime("%Y-%m-%d")
    new_bal = add_balance(user_id, _DAILY_AMOUNT)
    log_earning(user_id, _DAILY_AMOUNT)
    set_cooldown(user_id, "last_daily", today)
    return (
        S.DAILY_TITLE.format(CURRENCY_EMOJI=CURRENCY_EMOJI),
        S.DAILY_DESC.format(amount=_DAILY_AMOUNT, CURRENCY_NAME=CURRENCY_NAME),
        0x2ECC71,
        new_bal,
    )


_FINANZSPRITZE_AMOUNT = 10_000


def _run_finanzspritze(user_id: int) -> tuple[str, str, int, int]:
    new_bal = add_balance(user_id, _FINANZSPRITZE_AMOUNT)
    log_earning(user_id, _FINANZSPRITZE_AMOUNT)
    set_cooldown(user_id, "last_finanzspritze", time.time())
    return (
        S.FINANZ_TITLE,
        S.FINANZ_DESC.format(line=random.choice(S.FINANZSPRITZE_LINES), amount=_FINANZSPRITZE_AMOUNT, CURRENCY_EMOJI=CURRENCY_EMOJI),
        0xF1C40F,
        new_bal,
    )


_RUNNERS = {
    "beg":           _run_beg,
    "fish":          _run_fish,
    "work":          _run_work,
    "crime":         _run_crime,
    "scam":          _run_scam,
    "daily":         _run_daily,
    "finanzspritze": _run_finanzspritze,
}

# ── Embed builder ─────────────────────────────────────────────────────────────

def _build_embed(
    user_id: int,
    member: discord.Member,
    last_result: tuple[str, str, int, int] | None = None,
) -> discord.Embed:
    color = last_result[2] if last_result else 0xF1C40F
    embed = tag_embed(discord.Embed(
        title=S.EMBED_TITLE.format(CURRENCY_EMOJI=CURRENCY_EMOJI, CURRENCY_NAME=CURRENCY_NAME),
        color=color,
    ), member)

    if last_result:
        title, description, _, new_bal = last_result
        embed.add_field(
            name=f"▸ {title}",
            value=S.RESULT_FIELD_VALUE.format(description=description, new_bal=new_bal, CURRENCY_EMOJI=CURRENCY_EMOJI),
            inline=False,
        )

    for cmd, key, cd_secs, gain, risk, desc, _ in _COMMANDS:
        available, ready_at = _status(user_id, key, cd_secs)
        status_line = S.AVAILABLE_STATUS if available else S.COOLDOWN_STATUS.format(ready_at=ready_at)
        risk_line   = S.RISK_YES.format(risk=risk) if risk != "None" else S.RISK_NO
        embed.add_field(
            name=f"`{cmd}`  —  {desc}",
            value=S.FIELD_VALUE_TEMPLATE.format(gain=gain, CURRENCY_EMOJI=CURRENCY_EMOJI, risk_line=risk_line, status_line=status_line),
            inline=True,
        )

    embed.set_footer(text=S.FOOTER)
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
                await interaction.response.send_message(S.NOT_YOUR_MENU, ephemeral=True)
                return

            available, ready_at = _status(self.user_id, key, cd_secs)
            if not available:
                await interaction.response.send_message(
                    S.STILL_COOLDOWN.format(ready_at=ready_at), ephemeral=True
                )
                return

            result = _RUNNERS[btn_id](self.user_id)
            self._refresh_buttons()
            updated_embed = _build_embed(self.user_id, self.member, last_result=result)
            await interaction.response.edit_message(embed=updated_embed, view=self)

        return callback

# ── Command ───────────────────────────────────────────────────────────────────

@command("earn", description=S.DESCRIPTION, usage="f.earn", category="Casino")
async def earn_command(message: Message, args: list[str]):
    embed = _build_embed(message.author.id, message.author)
    view  = EarnView(message.author.id, message.author)
    await message.channel.send(embed=embed, view=view)
