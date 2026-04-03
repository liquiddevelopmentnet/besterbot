"""f.daily — 30 000 Maka Flaschen once per calendar day (resets at midnight CET)."""

from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_NAME, CURRENCY_EMOJI,
)
from bot.strings import Daily as S

_CET = ZoneInfo("Europe/Berlin")   # handles both CET (UTC+1) and CEST (UTC+2)
_DAILY_KEY = "last_daily"
_DAILY_AMOUNT = 30_000


def _today_cet() -> str:
    return datetime.now(tz=_CET).strftime("%Y-%m-%d")


def _seconds_until_midnight_cet() -> int:
    now = datetime.now(tz=_CET)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # next midnight
    from datetime import timedelta
    midnight = midnight + timedelta(days=1)
    return int((midnight - now).total_seconds())


@command("daily", description=S.DESCRIPTION, usage="f.daily", category="Casino")
async def daily_command(message: Message, args: list[str]):
    today = _today_cet()
    last = get_cooldown(message.author.id, _DAILY_KEY)

    if last == today:
        secs = _seconds_until_midnight_cet()
        h, rem = divmod(secs, 3600)
        m, s = divmod(rem, 60)
        embed = discord.Embed(
            title=S.ALREADY_CLAIMED_TITLE.format(CURRENCY_EMOJI=CURRENCY_EMOJI),
            description=S.ALREADY_CLAIMED_DESC.format(h=h, m=m, s=s),
            color=0xE74C3C,
        )
        tag_embed(embed, message.author)
        await message.reply(embed=embed)
        return

    new_bal = add_balance(message.author.id, _DAILY_AMOUNT)
    set_cooldown(message.author.id, _DAILY_KEY, today)

    embed = discord.Embed(
        title=S.REWARD_TITLE.format(CURRENCY_EMOJI=CURRENCY_EMOJI),
        description=S.REWARD_DESC.format(amount=_DAILY_AMOUNT, CURRENCY_NAME=CURRENCY_NAME, new_bal=new_bal, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x2ECC71,
    )
    embed.set_footer(text=S.REWARD_FOOTER)
    tag_embed(embed, message.author)
    await message.reply(embed=embed)
