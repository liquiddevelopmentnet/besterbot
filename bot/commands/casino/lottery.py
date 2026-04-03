import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)
from bot.strings import Lottery as S

SYMBOLS = ["\U0001f352", "\U0001f34b", "\U0001f514", "\U0001f48e",
           "\u2b50", "\U0001f4b0", "\U0001f7e3"]


def _scratch(bet: int, user_id: int, member: discord.Member) -> discord.Embed:
    reels  = [random.choice(SYMBOLS) for _ in range(3)]
    unique = len(set(reels))

    if unique == 1:
        multiplier = 10
        result     = S.JACKPOT
        color      = 0xFFD700
    elif unique == 2:
        multiplier = 3
        result     = S.TWO_MATCH
        color      = 0x2ECC71
    else:
        multiplier = 0
        result     = S.NO_MATCH
        color      = 0xE74C3C

    winnings = bet * multiplier
    if winnings > 0:
        add_balance(user_id, winnings)
        result += S.WIN_SUFFIX.format(winnings=winnings, CURRENCY_EMOJI=CURRENCY_EMOJI)

    embed = discord.Embed(title=S.TITLE, color=color)
    embed.add_field(name=S.YOUR_TICKET,
                    value=f"[ {reels[0]} | {reels[1]} | {reels[2]} ]", inline=False)
    embed.add_field(name=S.RESULT, value=result, inline=False)
    embed.set_footer(text=S.FOOTER.format(bet=bet))
    return tag_embed(embed, member)


class LotteryView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member, bet: int):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.member  = member
        self.bet     = bet

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(S.NOT_YOUR_GAME, ephemeral=True)
            return False
        return True

    @discord.ui.button(label=S.ANOTHER_TICKET_LABEL,
                       style=discord.ButtonStyle.primary, emoji="\U0001f3b0")
    async def another(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            remove_balance(self.user_id, self.bet)
        except ValueError:
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(
                S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME), ephemeral=True
            )
            return
        embed = _scratch(self.bet, self.user_id, self.member)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=S.QUIT_LABEL, style=discord.ButtonStyle.secondary, emoji="\u2716\ufe0f")
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@command("lottery", description=S.DESCRIPTION,
         usage="f.lottery <bet>", category="Casino")
async def lottery_command(message: Message, args: list[str]):
    if not args:
        await message.reply("Usage: `f.lottery <bet>`  (e.g. `f.lottery 500`, `f.lottery all`, `f.lottery 50%`)")
        return

    bet = resolve_bet(args[0], message.author.id)
    if bet is None:
        await message.reply("Usage: `f.lottery <bet>`  (e.g. `f.lottery 500`, `f.lottery all`, `f.lottery 50%`)")
        return
    if bet < MIN_BET:
        await message.reply(S.MIN_BET_MSG.format(MIN_BET=MIN_BET, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(S.BROKE_MSG.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    embed = _scratch(bet, message.author.id, message.author)
    view  = LotteryView(message.author.id, message.author, bet)
    await message.reply(embed=embed, view=view)
