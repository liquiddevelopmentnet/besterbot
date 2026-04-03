import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI, CURRENCY_NAME,
)
from bot.strings import Finanzspritze as S

_KEY = "last_finanzspritze"
_COOLDOWN = 3600  # 1 hour
_AMOUNT = 10_000


@command("finanzspritze", description=S.COMMAND_DESCRIPTION, usage="f.finanzspritze", category="Casino")
async def finanzspritze_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            await message.reply(S.COOLDOWN.format(m=m, s=s))
            return

    new_bal = add_balance(message.author.id, _AMOUNT)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title=S.TITLE,
        description=S.DESCRIPTION.format(response=random.choice(S.RESPONSES), amount=_AMOUNT, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0xF1C40F,
    ), message.author)
    embed.set_footer(text=S.FOOTER.format(new_bal=new_bal, CURRENCY_EMOJI=CURRENCY_EMOJI))
    await message.reply(embed=embed)
