import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, get_balance, log_earning, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)
from bot.strings import Bet as S


class BetView(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member, bet: int):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.bet = bet
        self.resolved = False
        self.message: discord.Message | None = None

    @discord.ui.button(label=S.ACCEPT_LABEL, style=discord.ButtonStyle.success, emoji="\u2705")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(S.NOT_FOR_YOU, ephemeral=True)
            return

        # Deduct from target
        try:
            remove_balance(self.target.id, self.bet)
        except ValueError:
            await interaction.response.send_message(
                S.NOT_ENOUGH_CURRENCY.format(CURRENCY_NAME=CURRENCY_NAME), ephemeral=True
            )
            return

        self.resolved = True

        # Coin flip
        winner = random.choice([self.challenger, self.target])
        loser = self.target if winner == self.challenger else self.challenger
        pot = self.bet * 2
        add_balance(winner.id, pot)
        log_earning(winner.id, pot)

        embed = tag_embed(discord.Embed(
            title=S.RESULT_TITLE,
            color=0xFFD700,
        ), interaction.user)
        embed.add_field(
            name=S.COIN_FLIP_NAME,
            value=S.COIN_FLIP_VALUE.format(
                winner=winner.display_name, pot=pot, CURRENCY_EMOJI=CURRENCY_EMOJI,
                loser=loser.display_name, bet=self.bet,
            ),
            inline=False,
        )

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label=S.DECLINE_LABEL, style=discord.ButtonStyle.danger, emoji="\u274c")
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(S.NOT_FOR_YOU, ephemeral=True)
            return

        self.resolved = True
        add_balance(self.challenger.id, self.bet)

        embed = tag_embed(discord.Embed(
            title=S.DECLINED_TITLE,
            description=S.DECLINED_DESC.format(name=self.target.display_name),
            color=0x95A5A6,
        ), interaction.user)

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        if not self.resolved:
            add_balance(self.challenger.id, self.bet)
            embed = discord.Embed(
                title=S.EXPIRED_TITLE,
                description=S.EXPIRED_DESC.format(name=self.target.display_name),
                color=0x95A5A6,
            )
            for item in self.children:
                item.disabled = True
            if self.message:
                try:
                    await self.message.edit(embed=embed, view=self)
                except discord.NotFound:
                    pass


@command("bet", description=S.DESCRIPTION, usage="f.bet @user <amount>", category="Casino")
async def bet_command(message: Message, args: list[str]):
    if len(args) < 2 or not message.mentions:
        await message.reply("Usage: `f.bet @user <amount>`")
        return

    target = message.mentions[0]
    if target.id == message.author.id:
        await message.reply(S.CANT_BET_SELF)
        return
    if target.bot:
        await message.reply(S.CANT_BET_BOT)
        return

    raw_amount = args[-1]
    bet = resolve_bet(raw_amount, message.author.id)
    if bet is None or bet <= 0:
        await message.reply(S.INVALID_AMOUNT)
        return
    if bet < MIN_BET:
        await message.reply(S.MIN_BET_MSG.format(MIN_BET=MIN_BET, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    # Check target has enough
    if get_balance(target.id) < bet:
        await message.reply(S.TARGET_BROKE.format(name=target.display_name, CURRENCY_NAME=CURRENCY_NAME))
        return

    # Deduct from challenger
    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(S.SENDER_BROKE.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    view = BetView(message.author, target, bet)

    embed = tag_embed(discord.Embed(
        title=S.CHALLENGE_TITLE,
        description=S.CHALLENGE_DESC.format(
            challenger=message.author.display_name,
            target=target.display_name,
            bet=bet,
            CURRENCY_EMOJI=CURRENCY_EMOJI,
            mention=target.mention,
        ),
        color=0xF1C40F,
    ), message.author)

    msg = await message.channel.send(embed=embed, view=view)
    view.message = msg
