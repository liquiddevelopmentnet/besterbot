import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)
from bot.strings import Double as S


def _play(bet: int, user_id: int, member: discord.Member) -> discord.Embed:
    win = random.random() < 0.53  # 53% win → ~106% RTP
    if win:
        winnings = bet * 2
        add_balance(user_id, winnings)
        embed = discord.Embed(
            title=S.TITLE,
            description=S.WIN_DESC.format(winnings=winnings, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0x2ECC71,
        )
    else:
        embed = discord.Embed(
            title=S.TITLE,
            description=S.LOSE_DESC.format(bet=bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0xE74C3C,
        )
    embed.set_footer(text=S.FOOTER.format(bet=bet))
    return tag_embed(embed, member)


class DoubleView(discord.ui.View):
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

    @discord.ui.button(label=S.PLAY_AGAIN_LABEL, style=discord.ButtonStyle.primary, emoji="\U0001f501")
    async def play_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Deduct bet first — if insufficient, just disable and bail
        try:
            remove_balance(self.user_id, self.bet)
        except ValueError:
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(
                S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME), ephemeral=True
            )
            return

        # Disable buttons on this (old) message
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

        # Send a fresh message with new active buttons
        embed    = _play(self.bet, self.user_id, self.member)
        new_view = DoubleView(self.user_id, self.member, self.bet)
        await interaction.followup.send(embed=embed, view=new_view)

    @discord.ui.button(label=S.QUIT_LABEL, style=discord.ButtonStyle.secondary, emoji="\u2716\ufe0f")
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@command("double", description=S.DESCRIPTION, usage="f.double <bet>", category="Casino")
async def double_command(message: Message, args: list[str]):
    if not args:
        await message.reply("Usage: `f.double <bet>`  (e.g. `f.double 500`, `f.double all`, `f.double 50%`)")
        return

    bet = resolve_bet(args[0], message.author.id)
    if bet is None:
        await message.reply("Usage: `f.double <bet>`  (e.g. `f.double 500`, `f.double all`, `f.double 50%`)")
        return
    if bet < MIN_BET:
        await message.reply(S.MIN_BET_MSG.format(MIN_BET=MIN_BET, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(S.BROKE_MSG.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    embed = _play(bet, message.author.id, message.author)
    view  = DoubleView(message.author.id, message.author, bet)
    await message.reply(embed=embed, view=view)
