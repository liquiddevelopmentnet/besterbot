import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, get_balance, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)


class BetView(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member, bet: int):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.bet = bet
        self.resolved = False
        self.message: discord.Message | None = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="\u2705")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("This challenge isn't for you!", ephemeral=True)
            return

        # Deduct from target
        try:
            remove_balance(self.target.id, self.bet)
        except ValueError:
            await interaction.response.send_message(
                f"You don't have enough {CURRENCY_NAME}!", ephemeral=True
            )
            return

        self.resolved = True

        # Coin flip
        winner = random.choice([self.challenger, self.target])
        loser = self.target if winner == self.challenger else self.challenger
        pot = self.bet * 2
        add_balance(winner.id, pot)

        embed = tag_embed(discord.Embed(
            title="\U0001f3b2 50:50 Bet \u2014 Result",
            color=0xFFD700,
        ), interaction.user)
        embed.add_field(
            name="\U0001fa99 Coin Flip",
            value=(
                f"**{winner.display_name}** wins **{pot:,}** {CURRENCY_EMOJI}!\n"
                f"**{loser.display_name}** loses their **{self.bet:,}** {CURRENCY_EMOJI}."
            ),
            inline=False,
        )

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, emoji="\u274c")
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("This challenge isn't for you!", ephemeral=True)
            return

        self.resolved = True
        add_balance(self.challenger.id, self.bet)

        embed = tag_embed(discord.Embed(
            title="\U0001f3b2 50:50 Bet \u2014 Declined",
            description=f"**{self.target.display_name}** declined. Bet refunded.",
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
                title="\U0001f3b2 50:50 Bet \u2014 Expired",
                description=f"**{self.target.display_name}** didn't respond. Bet refunded.",
                color=0x95A5A6,
            )
            for item in self.children:
                item.disabled = True
            if self.message:
                try:
                    await self.message.edit(embed=embed, view=self)
                except discord.NotFound:
                    pass


@command("bet", description="50:50 bet against another player", usage="f.bet @user <amount>", category="Casino")
async def bet_command(message: Message, args: list[str]):
    if len(args) < 2 or not message.mentions:
        await message.reply("Usage: `f.bet @user <amount>`")
        return

    target = message.mentions[0]
    if target.id == message.author.id:
        await message.reply("You can't bet against yourself.")
        return
    if target.bot:
        await message.reply("You can't bet against a bot.")
        return

    raw_amount = args[-1]
    bet = resolve_bet(raw_amount, message.author.id)
    if bet is None or bet <= 0:
        await message.reply("Amount must be a positive number (e.g. `500`, `all`, `50%`).")
        return
    if bet < MIN_BET:
        await message.reply(f"Minimum bet is {MIN_BET} {CURRENCY_EMOJI}")
        return

    # Check target has enough
    if get_balance(target.id) < bet:
        await message.reply(f"**{target.display_name}** doesn't have enough {CURRENCY_NAME}!")
        return

    # Deduct from challenger
    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(f"You don't have enough {CURRENCY_NAME}!")
        return

    view = BetView(message.author, target, bet)

    embed = tag_embed(discord.Embed(
        title="\U0001f3b2 50:50 Bet Challenge!",
        description=(
            f"**{message.author.display_name}** challenges **{target.display_name}** "
            f"for **{bet:,}** {CURRENCY_EMOJI}!\n\n"
            f"{target.mention}, do you accept?"
        ),
        color=0xF1C40F,
    ), message.author)

    msg = await message.channel.send(embed=embed, view=view)
    view.message = msg
