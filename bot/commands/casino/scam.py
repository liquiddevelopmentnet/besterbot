import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, force_remove_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI,
)

_KEY = "last_scam"
_COOLDOWN = 1200  # 20 minutes
_SUCCESS_CHANCE = 0.60

_SUCCESS_SCAMS = [
    "hat die geheimen Aktien von Netanyahu gerugpulled",
    "sold an 'AI startup' to a gullible investor",
    "pulled off a Nigerian prince email scheme",
    "convinced someone their PC had a virus and charged for 'repairs'",
    "listed a non-existent apartment on Airbnb",
    "sold 'premium' tap water as Swiss mineral water",
]

_FAIL_SCAMS = [
    "the mark was an undercover cop",
    "your phishing site got reported and traced back to you",
    "you accidentally scammed a lawyer",
    "Interpol froze your accounts",
    "the victim recognised you from a wanted poster",
]


@command("scam", description="Run a high-risk scam for massive profit", usage="f.scam", category="Casino")
async def scam_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            time_str = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
            await message.reply(f"🕵️ Keep a low profile for **{time_str}** more.")
            return

    set_cooldown(message.author.id, _KEY, time.time())

    if random.random() < _SUCCESS_CHANCE:
        earned = random.randint(10000, 16000)
        new_bal = add_balance(message.author.id, earned)
        embed = tag_embed(discord.Embed(
            title="🤑 Scam Successful",
            description=f"You {random.choice(_SUCCESS_SCAMS)}.\n+**{earned:,}** {CURRENCY_EMOJI}",
            color=0x2ECC71,
        ), message.author)
    else:
        lost = random.randint(1000, 2500)
        new_bal = force_remove_balance(message.author.id, lost)
        embed = tag_embed(discord.Embed(
            title="🚔 Scam Backfired",
            description=f"You {random.choice(_FAIL_SCAMS)}.\n-**{lost:,}** {CURRENCY_EMOJI}",
            color=0xE74C3C,
        ), message.author)
        if new_bal < 0:
            embed.add_field(name="💸 In Debt", value=f"**{abs(new_bal):,}** {CURRENCY_EMOJI} in the hole.", inline=False)

    embed.set_footer(text=f"Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 20min")
    await message.reply(embed=embed)
