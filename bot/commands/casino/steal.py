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
    get_cooldown, set_cooldown, log_earning, tag_embed,
    CURRENCY_NAME, CURRENCY_EMOJI,
)
from bot.strings import Steal as S

_STEAL_KEY = "last_steal"
_COOLDOWN_SECS  = 5 * 60  # 5 minutes
_SUCCESS_CHANCE = 0.55
_MAX_STEAL      = 5_000   # max Maka you can gain on a successful steal
_MAX_PENALTY    = 3_000   # max Maka you can lose when caught


@command("steal", description=S.DESCRIPTION, usage="f.steal @user", category="Casino")
async def steal_command(message: Message, args: list[str]):
    if not message.mentions:
        await message.reply("Usage: `f.steal @user`")
        return

    target = message.mentions[0]

    if target.id == message.author.id:
        await message.reply(S.CANT_STEAL_SELF)
        return
    if target.bot:
        await message.reply(S.CANT_STEAL_BOT)
        return

    # Cooldown check
    last = get_cooldown(message.author.id, _STEAL_KEY)
    if last is not None:
        remaining = _COOLDOWN_SECS - (time.time() - last)
        if remaining > 0:
            h, rem = divmod(int(remaining), 3600)
            m, s = divmod(rem, 60)
            await message.reply(S.COOLDOWN.format(h=h, m=m, s=s))
            return

    target_bal = get_balance(target.id)
    author_bal = get_balance(message.author.id)

    # Need something worth stealing
    if target_bal < 100:
        await message.reply(S.TARGET_BROKE.format(name=target.display_name, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    set_cooldown(message.author.id, _STEAL_KEY, time.time())

    if random.random() < _SUCCESS_CHANCE:
        # ── Success ────────────────────────────────────────────
        pct = random.uniform(0.15, 0.30)
        stolen = max(100, int(target_bal * pct))
        stolen = min(stolen, target_bal, _MAX_STEAL)

        force_remove_balance(target.id, stolen)
        new_author = add_balance(message.author.id, stolen)
        log_earning(message.author.id, stolen)

        embed = discord.Embed(
            title=S.SUCCESS_TITLE,
            description=S.SUCCESS_DESC.format(stolen=stolen, CURRENCY_EMOJI=CURRENCY_EMOJI, name=target.display_name),
            color=0x2ECC71,
        )
        embed.add_field(name=S.YOUR_BALANCE, value=f"{new_author:,} {CURRENCY_EMOJI}", inline=True)
        embed.add_field(
            name=S.TARGET_BALANCE.format(name=target.display_name),
            value=f"{get_balance(target.id):,} {CURRENCY_EMOJI}",
            inline=True,
        )
    else:
        # ── Caught ─────────────────────────────────────────────
        pct = random.uniform(0.20, 0.40)
        penalty = max(100, int(author_bal * pct)) if author_bal > 0 else random.randint(200, 600)
        penalty = min(penalty, _MAX_PENALTY)
        new_author = force_remove_balance(message.author.id, penalty)

        embed = discord.Embed(
            title=S.CAUGHT_TITLE,
            description=S.CAUGHT_DESC.format(name=target.display_name, penalty=penalty, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0xE74C3C,
        )
        embed.add_field(name=S.YOUR_BALANCE, value=f"{new_author:,} {CURRENCY_EMOJI}", inline=True)
        if new_author < 0:
            embed.add_field(
                name=S.DEBT_NAME,
                value=S.DEBT_VALUE.format(amount=abs(new_author), CURRENCY_EMOJI=CURRENCY_EMOJI),
                inline=True,
            )

    embed.set_footer(text=S.FOOTER)
    tag_embed(embed, message.author)
    await message.reply(embed=embed)
