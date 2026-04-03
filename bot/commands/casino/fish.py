import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI,
)
from bot.strings import Fish as S

_KEY = "last_fish"
_COOLDOWN = 600  # 10 minutes


@command("fish", description=S.COMMAND_DESCRIPTION, usage="f.fish", category="Casino")
async def fish_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            time_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
            await message.reply(S.COOLDOWN.format(time_str=time_str))
            return

    low, high, emoji, name = random.choice(S.CATCHES)
    earned = random.randint(low, high)
    new_bal = add_balance(message.author.id, earned)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title=S.TITLE.format(emoji=emoji),
        description=S.DESCRIPTION.format(name=name, earned=earned, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x3498DB,
    ), message.author)
    embed.set_footer(text=S.FOOTER.format(new_bal=new_bal, CURRENCY_EMOJI=CURRENCY_EMOJI))
    await message.reply(embed=embed)
