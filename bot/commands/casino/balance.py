import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_balance, get_leaderboard, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI,
)

MEDALS = {0: "\U0001f947", 1: "\U0001f948", 2: "\U0001f949"}


def _lb_embed(guild: discord.Guild, requester: discord.Member) -> discord.Embed:
    board = get_leaderboard(10)
    lines = []
    for i, (uid, bal) in enumerate(board):
        member = guild.get_member(int(uid))
        name   = member.display_name if member else f"User {uid}"
        lines.append(f"{MEDALS.get(i, f'`{i+1}.`')} **{name}** — {bal:,} {CURRENCY_EMOJI}")
    embed = discord.Embed(
        title=f"{CURRENCY_EMOJI} {CURRENCY_NAME} Leaderboard",
        description="\n".join(lines) or "No players yet.",
        color=0xF1C40F,
    )
    return tag_embed(embed, requester)


class BalanceView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=120)
        self.member = member

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                "This isn't your wallet!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Earn Menu", style=discord.ButtonStyle.success, emoji="\U0001f4b0")
    async def earn_menu(self, interaction: discord.Interaction, _: discord.ui.Button):
        from bot.commands.casino.earn import _build_embed, EarnView
        embed = _build_embed(self.member.id, self.member)
        view  = EarnView(self.member.id, self.member)
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="Leaderboard", style=discord.ButtonStyle.secondary, emoji="\U0001f3c6")
    async def leaderboard(self, interaction: discord.Interaction, _: discord.ui.Button):
        embed = _lb_embed(interaction.guild, self.member)
        await interaction.response.send_message(embed=embed)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@command("balance", description="Check your balance", usage="f.balance", category="Casino")
@command("bal",     description="Check your balance", usage="f.bal",     category="Casino")
async def balance_command(message: Message, args: list[str]):
    bal   = get_balance(message.author.id)
    embed = discord.Embed(
        title=f"{CURRENCY_EMOJI} Wallet",
        description=f"**{bal:,}** {CURRENCY_NAME}",
        color=0xF1C40F,
    )
    tag_embed(embed, message.author)
    view = BalanceView(message.author)
    await message.reply(embed=embed, view=view)
