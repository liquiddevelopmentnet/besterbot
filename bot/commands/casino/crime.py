import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, force_remove_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI, CURRENCY_NAME,
)
from bot.strings import Crime as S

_KEY = "last_crime"
_COOLDOWN = 1200  # 20 minutes
_SUCCESS_CHANCE = 0.70


@command("crime", description=S.DESCRIPTION, usage="f.crime", category="Casino")
async def crime_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            time_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
            await message.reply(S.COOLDOWN.format(time_str=time_str))
            return

    set_cooldown(message.author.id, _KEY, time.time())

    if random.random() < _SUCCESS_CHANCE:
        earned = random.randint(8000, 13000)
        new_bal = add_balance(message.author.id, earned)
        embed = tag_embed(discord.Embed(
            title=S.SUCCESS_TITLE,
            description=S.SUCCESS_DESC.format(crime=random.choice(S.SUCCESS_CRIMES), earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0x2ECC71,
        ), message.author)
    else:
        lost = random.randint(1000, 2000)
        new_bal = force_remove_balance(message.author.id, lost)
        embed = tag_embed(discord.Embed(
            title=S.FAIL_TITLE,
            description=S.FAIL_DESC.format(crime=random.choice(S.FAIL_CRIMES), lost=lost, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0xE74C3C,
        ), message.author)
        if new_bal < 0:
            embed.add_field(name=S.DEBT_NAME, value=S.DEBT_VALUE.format(amount=abs(new_bal), CURRENCY_EMOJI=CURRENCY_EMOJI), inline=False)

    embed.set_footer(text=S.FOOTER.format(new_bal=new_bal, CURRENCY_EMOJI=CURRENCY_EMOJI))
    await message.reply(embed=embed)
