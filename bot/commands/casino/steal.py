"""f.steal — attempt to steal from another player.

Success (55 %): steal 15–30 % of target's balance (min 100 MF).
Failure (45 %): lose 20–40 % of your own balance — can go negative.
"""

import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, force_remove_balance, get_balance,
    get_cooldown, set_cooldown, tag_embed,
    CURRENCY_NAME, CURRENCY_EMOJI,
)

_STEAL_KEY = "last_steal"
_COOLDOWN_SECS = 5 * 60 # 5 minutes
_SUCCESS_CHANCE = 0.55


@command("steal", description="Attempt to steal from another player", usage="f.steal @user", category="Casino")
async def steal_command(message: Message, args: list[str]):
    if not message.mentions:
        await message.reply("Usage: `f.steal @user`")
        return

    target = message.mentions[0]

    if target.id == message.author.id:
        await message.reply("You can't steal from yourself.")
        return
    if target.bot:
        await message.reply("Bots don't carry cash.")
        return

    # Cooldown check
    last = get_cooldown(message.author.id, _STEAL_KEY)
    if last is not None:
        remaining = _COOLDOWN_SECS - (time.time() - last)
        if remaining > 0:
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            await message.reply(
                f"\U0001f6ab You're still laying low. Try again in **{h}h {m}m {s}s**."
            )
            return

    target_bal = get_balance(target.id)
    author_bal = get_balance(message.author.id)

    # Need something worth stealing
    if target_bal < 100:
        await message.reply(
            f"**{target.display_name}** is too broke to steal from (< 100 {CURRENCY_EMOJI})."
        )
        return

    set_cooldown(message.author.id, _STEAL_KEY, time.time())

    if random.random() < _SUCCESS_CHANCE:
        # ── Success ────────────────────────────────────────────
        pct = random.uniform(0.15, 0.30)
        stolen = max(100, int(target_bal * pct))
        stolen = min(stolen, target_bal)   # can't steal more than they have

        force_remove_balance(target.id, stolen)
        new_author = add_balance(message.author.id, stolen)

        embed = discord.Embed(
            title="\U0001f977 Heist Successful!",
            description=(
                f"You pickpocketed **{stolen:,}** {CURRENCY_EMOJI} "
                f"from **{target.display_name}**!"
            ),
            color=0x2ECC71,
        )
        embed.add_field(name="Your Balance", value=f"{new_author:,} {CURRENCY_EMOJI}", inline=True)
        embed.add_field(
            name=f"{target.display_name}'s Balance",
            value=f"{get_balance(target.id):,} {CURRENCY_EMOJI}",
            inline=True,
        )
    else:
        # ── Caught ─────────────────────────────────────────────
        pct = random.uniform(0.20, 0.40)
        penalty = max(100, int(author_bal * pct)) if author_bal > 0 else random.randint(200, 600)
        new_author = force_remove_balance(message.author.id, penalty)

        embed = discord.Embed(
            title="\U0001f6a8 Caught Red-Handed!",
            description=(
                f"**{target.display_name}** caught you stealing and called the cops.\n"
                f"You were fined **{penalty:,}** {CURRENCY_EMOJI}."
            ),
            color=0xE74C3C,
        )
        embed.add_field(name="Your Balance", value=f"{new_author:,} {CURRENCY_EMOJI}", inline=True)
        if new_author < 0:
            embed.add_field(
                name="\U0001f4b8 In Debt",
                value=f"You're **{abs(new_author):,}** {CURRENCY_EMOJI} in the hole.",
                inline=True,
            )

    embed.set_footer(text="2-hour cooldown before your next attempt.")
    tag_embed(embed, message.author)
    await message.reply(embed=embed)
