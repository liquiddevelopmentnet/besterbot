import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI,
)

_KEY = "last_beg"
_COOLDOWN = 120  # 2 minutes

_RESPONSES = [
    "A kind stranger took pity on you.",
    "Someone threw coins out of a car window.",
    "You found a crumpled bill on the ground.",
    "A tourist thought you were a street performer.",
    "Your sob story actually worked.",
    "An old lady gave you her grocery change.",
]


@command("beg", description="Beg for spare change", usage="f.beg", category="Casino")
async def beg_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            await message.reply(f"🙏 People are tired of you. Wait **{m}m {s}s** before begging again.")
            return

    earned = random.randint(50, 500)
    new_bal = add_balance(message.author.id, earned)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title="🙏 Begging Complete",
        description=f"{random.choice(_RESPONSES)}\n+**{earned:,}** {CURRENCY_EMOJI}",
        color=0x95A5A6,
    ), message.author)
    embed.set_footer(text=f"Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 2min")
    await message.reply(embed=embed)
