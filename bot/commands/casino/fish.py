import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI,
)

_KEY = "last_fish"
_COOLDOWN = 300  # 5 minutes

_CATCHES = [
    (300,  600,  "🐟", "a small sardine"),
    (400,  800,  "🐠", "a tropical fish"),
    (500,  900,  "🦐", "a bag of shrimp"),
    (600, 1000,  "🦀", "a crab"),
    (800, 1200,  "🐡", "a pufferfish"),
    (900, 1200,  "🐙", "an octopus"),
    (600,  900,  "🥾", "an old boot (someone paid for the antique)"),
    (1000, 1200, "🦞", "a massive lobster"),
]


@command("fish", description="Go fishing for some income", usage="f.fish", category="Casino")
async def fish_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            time_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
            await message.reply(f"🎣 The fish need time to come back. Try again in **{time_str}**.")
            return

    low, high, emoji, name = random.choice(_CATCHES)
    earned = random.randint(low, high)
    new_bal = add_balance(message.author.id, earned)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title=f"{emoji} Caught Something!",
        description=f"You reeled in **{name}** and sold it for **{earned:,}** {CURRENCY_EMOJI}.",
        color=0x3498DB,
    ), message.author)
    embed.set_footer(text=f"Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 5min")
    await message.reply(embed=embed)
