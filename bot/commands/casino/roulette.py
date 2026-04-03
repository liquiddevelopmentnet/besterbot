import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, log_earning, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)
from bot.strings import Roulette as S

RED     = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK   = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
NUMBERS = list(range(0, 37))


def _color_of(n: int) -> str:
    if n == 0:
        return "green"
    return "red" if n in RED else "black"


def _color_emoji(c: str) -> str:
    return {"red": "\U0001f534", "black": "\u26ab", "green": "\U0001f7e2"}[c]


def _spin(bet: int, choice: str | int,
          user_id: int, member: discord.Member) -> discord.Embed:
    result       = random.choice(NUMBERS)
    result_color = _color_of(result)
    result_emoji = _color_emoji(result_color)

    bet_type = "color" if isinstance(choice, str) else "number"
    winnings = 0
    if bet_type == "color" and choice == result_color:
        # Green: 1/37 chance → 40x = 108% RTP | Red/Black: 18/37 → 2.2x = 107% RTP
        multiplier = 40 if choice == "green" else 2.2
        winnings = int(bet * multiplier)
    elif bet_type == "number" and choice == result:
        winnings = bet * 40  # 1/37 chance → 40x = 108% RTP

    if winnings > 0:
        add_balance(user_id, winnings)
        log_earning(user_id, winnings)
        desc  = S.WIN_DESC.format(winnings=winnings, CURRENCY_EMOJI=CURRENCY_EMOJI)
        color = 0x2ECC71
    else:
        desc  = S.LOSE_DESC.format(bet=bet, CURRENCY_EMOJI=CURRENCY_EMOJI)
        color = 0xE74C3C

    embed = discord.Embed(title=S.TITLE, color=color)
    embed.add_field(
        name=S.LANDS_ON,
        value=f"{result_emoji} **{result}** ({result_color})",
        inline=False,
    )
    embed.add_field(name=S.YOUR_BET,
                    value=f"`{choice}` for {bet:,} {CURRENCY_EMOJI}", inline=True)
    embed.add_field(name=S.RESULT, value=desc, inline=True)
    return tag_embed(embed, member)


class RouletteView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member,
                 bet: int, choice: str | int):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.member  = member
        self.bet     = bet
        self.choice  = choice

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(S.NOT_YOUR_GAME, ephemeral=True)
            return False
        return True

    async def _bet_and_spin(self, interaction: discord.Interaction, choice: str | int):
        try:
            remove_balance(self.user_id, self.bet)
        except ValueError:
            await interaction.response.send_message(
                S.NOT_ENOUGH_SPIN.format(CURRENCY_NAME=CURRENCY_NAME), ephemeral=True
            )
            return
        self.choice = choice
        embed = _spin(self.bet, choice, self.user_id, self.member)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=S.RED_LABEL,   style=discord.ButtonStyle.danger,    emoji="\U0001f534")
    async def bet_red(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._bet_and_spin(interaction, "red")

    @discord.ui.button(label=S.BLACK_LABEL, style=discord.ButtonStyle.secondary, emoji="\u26ab")
    async def bet_black(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._bet_and_spin(interaction, "black")

    @discord.ui.button(label=S.GREEN_LABEL, style=discord.ButtonStyle.success,   emoji="\U0001f7e2")
    async def bet_green(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._bet_and_spin(interaction, "green")

    @discord.ui.button(label=S.SAME_LABEL,  style=discord.ButtonStyle.primary,   emoji="\U0001f501")
    async def same_again(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._bet_and_spin(interaction, self.choice)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@command("roulette", description=S.DESCRIPTION,
         usage="f.roulette <bet> <red/black/green/number>", category="Casino")
async def roulette_command(message: Message, args: list[str]):
    if len(args) < 2:
        await message.reply(S.USAGE)
        return

    bet = resolve_bet(args[0], message.author.id)
    if bet is None:
        await message.reply(S.USAGE)
        return
    choice = args[1].lower()

    if bet < MIN_BET:
        await message.reply(S.MIN_BET_MSG.format(MIN_BET=MIN_BET, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    if choice in ("red", "black", "green"):
        pass
    elif choice.isdigit() and 0 <= int(choice) <= 36:
        choice = int(choice)
    else:
        await message.reply(S.INVALID_CHOICE)
        return

    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    embed = _spin(bet, choice, message.author.id, message.author)
    view  = RouletteView(message.author.id, message.author, bet, choice)
    await message.reply(embed=embed, view=view)
