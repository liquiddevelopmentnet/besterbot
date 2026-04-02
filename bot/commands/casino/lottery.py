import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)

SYMBOLS = ["\U0001f352", "\U0001f34b", "\U0001f514", "\U0001f48e",
           "\u2b50", "\U0001f4b0", "\U0001f7e3"]


def _scratch(bet: int, user_id: int, member: discord.Member) -> discord.Embed:
    reels  = [random.choice(SYMBOLS) for _ in range(3)]
    unique = len(set(reels))

    if unique == 1:
        multiplier = 10
        result     = "\U0001f389 **JACKPOT!** All three match!"
        color      = 0xFFD700
    elif unique == 2:
        multiplier = 3
        result     = "\U0001f31f **Two match!** Nice pull."
        color      = 0x2ECC71
    else:
        multiplier = 0
        result     = "\U0001f480 **No match.** Better luck next time."
        color      = 0xE74C3C

    winnings = bet * multiplier
    if winnings > 0:
        add_balance(user_id, winnings)
        result += f"\n+**{winnings:,}** {CURRENCY_EMOJI}"

    embed = discord.Embed(title="\U0001f3b0 Lottery Scratch-Off", color=color)
    embed.add_field(name="Your Ticket",
                    value=f"[ {reels[0]} | {reels[1]} | {reels[2]} ]", inline=False)
    embed.add_field(name="Result", value=result, inline=False)
    embed.set_footer(text=f"Bet: {bet:,} | 3 match = 10x \u2022 2 match = 3x")
    return tag_embed(embed, member)


class LotteryView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member, bet: int):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.member  = member
        self.bet     = bet

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Another Ticket",
                       style=discord.ButtonStyle.primary, emoji="\U0001f3b0")
    async def another(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            remove_balance(self.user_id, self.bet)
        except ValueError:
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(
                f"Not enough {CURRENCY_NAME} for another ticket!", ephemeral=True
            )
            return
        embed = _scratch(self.bet, self.user_id, self.member)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.secondary, emoji="\u2716\ufe0f")
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@command("lottery", description="Scratch-off lottery ticket",
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
        await message.reply(f"Minimum bet is {MIN_BET} {CURRENCY_EMOJI}")
        return

    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(f"You don't have enough {CURRENCY_NAME}!")
        return

    embed = _scratch(bet, message.author.id, message.author)
    view  = LotteryView(message.author.id, message.author, bet)
    await message.reply(embed=embed, view=view)
