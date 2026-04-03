import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI,
)
from bot.strings import Beg as S

_KEY = "last_beg"
_COOLDOWN = 240  # 4 minutes


@command("beg", description=S.COMMAND_DESCRIPTION, usage="f.beg", category="Casino")
async def beg_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            await message.reply(S.COOLDOWN.format(m=m, s=s))
            return

    earned = random.randint(500, 2500)
    new_bal = add_balance(message.author.id, earned)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title=S.TITLE,
        description=S.DESCRIPTION.format(response=random.choice(S.RESPONSES), earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x95A5A6,
    ), message.author)
    embed.set_footer(text=S.FOOTER.format(new_bal=new_bal, CURRENCY_EMOJI=CURRENCY_EMOJI))
    await message.reply(embed=embed)
