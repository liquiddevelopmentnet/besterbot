import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, force_remove_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI, CURRENCY_NAME,
)

_KEY = "last_crime"
_COOLDOWN = 1200  # 20 minutes
_SUCCESS_CHANCE = 0.70

_SUCCESS_CRIMES = [
    "robbed a vending machine",
    "pickpocketed a tourist",
    "sold knockoff Gucci bags",
    "hacked a parking meter",
    "ran a shell game on tourists",
    "fenced stolen electronics",
    "forged a concert ticket run",
]

_FAIL_CRIMES = [
    "got caught shoplifting and fined",
    "tripped the alarm and had to pay damages",
    "got mugged while trying to mug someone else",
    "the police showed up mid-heist",
    "your accomplice snitched on you",
]


@command("crime", description="Commit a risky crime for big rewards", usage="f.crime", category="Casino")
async def crime_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            time_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
            await message.reply(f"🚔 Still laying low. Try again in **{time_str}**.")
            return

    set_cooldown(message.author.id, _KEY, time.time())

    if random.random() < _SUCCESS_CHANCE:
        earned = random.randint(8000, 13000)
        new_bal = add_balance(message.author.id, earned)
        embed = tag_embed(discord.Embed(
            title="🦹 Crime Pays",
            description=f"You {random.choice(_SUCCESS_CRIMES)} and got away with **{earned:,}** {CURRENCY_EMOJI}.",
            color=0x2ECC71,
        ), message.author)
    else:
        lost = random.randint(1000, 2000)
        new_bal = force_remove_balance(message.author.id, lost)
        embed = tag_embed(discord.Embed(
            title="🚨 Busted!",
            description=f"You {random.choice(_FAIL_CRIMES)}. Fined **{lost:,}** {CURRENCY_EMOJI}.",
            color=0xE74C3C,
        ), message.author)
        if new_bal < 0:
            embed.add_field(name="💸 In Debt", value=f"**{abs(new_bal):,}** {CURRENCY_EMOJI} in the hole.", inline=False)

    embed.set_footer(text=f"Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 20min")
    await message.reply(embed=embed)
