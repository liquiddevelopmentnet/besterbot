import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, log_earning, tag_embed,
    CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET, resolve_bet,
)
from bot.strings import Crash as S

# Preset target multipliers offered as buttons
_PRESETS = [1.5, 2.0, 3.0, 5.0, 10.0, 25.0]


def _crash_point() -> float:
    """
    Generate a random crash point.
    Distribution: P(crash >= x) = 1.05 / x  → 105% RTP for any target.
    Capped at 100x.
    """
    r = random.random()
    return round(min(1.05 / r, 100.0), 2)


def _pending_embed(member: discord.Member, bet: int) -> discord.Embed:
    lines = []
    for p in _PRESETS:
        chance = min(int(1.05 / p * 100), 99)
        lines.append(f"**{p}x** — {chance}% chance · pays **{int(bet * p):,}**")
    embed = discord.Embed(
        title=S.PENDING_TITLE,
        description=S.PENDING_DESC.format(lines="\n".join(lines)),
        color=0xF39C12,
    )
    embed.add_field(name=S.PENDING_BET, value=f"{bet:,} {CURRENCY_EMOJI}", inline=True)
    embed.set_footer(text=S.PENDING_FOOTER)
    return tag_embed(embed, member)


def _result_embed(
    member: discord.Member,
    bet: int,
    target: float,
    crash: float,
) -> discord.Embed:
    won    = crash >= target
    payout = int(bet * target)

    if won:
        profit = payout - bet
        embed  = discord.Embed(
            title=S.SAFE_TITLE,
            description=S.SAFE_DESC.format(crash=crash, target=target, payout=payout, CURRENCY_EMOJI=CURRENCY_EMOJI, profit=profit),
            color=0x2ECC71,
        )
    else:
        embed = discord.Embed(
            title=S.CRASHED_TITLE,
            description=S.CRASHED_DESC.format(crash=crash, target=target, bet=bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0xE74C3C,
        )

    embed.add_field(name=S.FIELD_BET,     value=f"{bet:,} {CURRENCY_EMOJI}", inline=True)
    embed.add_field(name=S.FIELD_TARGET,  value=f"{target}x",                inline=True)
    embed.add_field(name=S.FIELD_CRASHED, value=f"{crash}x",                 inline=True)
    return tag_embed(embed, member)


class CrashView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member, bet: int):
        super().__init__(timeout=60)
        self.user_id  = user_id
        self.member   = member
        self.bet      = bet
        self._message: discord.Message | None = None

        for i, preset in enumerate(_PRESETS):
            btn = discord.ui.Button(
                label=f"{preset}x",
                style=discord.ButtonStyle.primary,
                row=0 if i < 3 else 1,
                custom_id=f"crash_{preset}_{user_id}",
            )
            btn.callback = self._make_cb(preset)
            self.add_item(btn)

    def _make_cb(self, target: float):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(S.NOT_YOUR_GAME, ephemeral=True)
                return

            crash = _crash_point()
            won   = crash >= target

            if won:
                payout = int(self.bet * target)
                add_balance(self.user_id, payout)
                log_earning(self.user_id, payout)

            for item in self.children:
                item.disabled = True

            embed = _result_embed(self.member, self.bet, target, crash)
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()

        return callback

    async def on_timeout(self):
        # Player never picked — refund
        add_balance(self.user_id, self.bet)
        for item in self.children:
            item.disabled = True
        if self._message:
            try:
                await self._message.edit(view=self)
            except Exception:
                pass


@command("crash", description=S.DESCRIPTION, usage="f.crash <bet>", category="Casino")
async def crash_command(message: Message, args: list[str]):
    if not args:
        await message.reply("Usage: `f.crash <bet>`  (e.g. `f.crash 500`, `f.crash all`, `f.crash 50%`)")
        return

    bet = resolve_bet(args[0], message.author.id)
    if bet is None:
        await message.reply("Usage: `f.crash <bet>`  (e.g. `f.crash 500`, `f.crash all`, `f.crash 50%`)")
        return
    if bet < MIN_BET:
        await message.reply(S.MIN_BET_MSG.format(MIN_BET=MIN_BET, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    embed = _pending_embed(message.author, bet)
    view  = CrashView(message.author.id, message.author, bet)
    msg   = await message.reply(embed=embed, view=view)
    view._message = msg
