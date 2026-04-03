import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI, CURRENCY_NAME,
)
from bot.strings import Work as S

_KEY = "last_work"
_COOLDOWN = 600  # 10 minutes


@command("work", description=S.COMMAND_DESCRIPTION, usage="f.work", category="Casino")
async def work_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            await message.reply(S.COOLDOWN.format(m=m, s=s))
            return

    emoji, desc = random.choice(S.JOBS)
    earned = random.randint(2000, 5000)
    new_bal = add_balance(message.author.id, earned)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title=S.TITLE.format(emoji=emoji),
        description=S.DESCRIPTION.format(desc=desc, earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x2ECC71,
    ), message.author)
    embed.set_footer(text=S.FOOTER.format(new_bal=new_bal, CURRENCY_EMOJI=CURRENCY_EMOJI))
    await message.reply(embed=embed)
