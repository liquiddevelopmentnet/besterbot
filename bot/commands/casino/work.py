import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI, CURRENCY_NAME,
)

_KEY = "last_work"
_COOLDOWN = 300  # 5 minutes

_JOBS = [
    ("🍔", "hat die fritten in die Tütte bei MCs gepackt"),
    ("🚗", "hat ein paar Obdachlose rumgefahren"),
    ("💻", "fixed someone's printer"),
    ("🛒", "stacked shelves at Lidl"),
    ("📦", "sorted packages at Amazon"),
    ("🔧", "fixed a leaky pipe"),
    ("🎸", "busked at the Hauptbahnhof"),
    ("🚚", "made DHL deliveries"),
    ("🧹", "cleaned an office building"),
    ("📱", "did customer support calls"),
]


@command("work", description="Work a shift for steady income", usage="f.work", category="Casino")
async def work_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            await message.reply(f"😴 You're still tired. Back to work in **{m}m {s}s**.")
            return

    emoji, desc = random.choice(_JOBS)
    earned = random.randint(500, 1500)
    new_bal = add_balance(message.author.id, earned)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title=f"{emoji} Work Complete",
        description=f"You {desc} and earned **{earned:,}** {CURRENCY_EMOJI}.",
        color=0x2ECC71,
    ), message.author)
    embed.set_footer(text=f"Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 5min")
    await message.reply(embed=embed)
