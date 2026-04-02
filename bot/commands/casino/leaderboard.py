import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import get_leaderboard, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI

MEDALS = {0: "\U0001f947", 1: "\U0001f948", 2: "\U0001f949"}


async def _build_embed(guild: discord.Guild, requester: discord.Member) -> discord.Embed:
    board = get_leaderboard(10)
    lines = []
    for i, (uid, bal) in enumerate(board):
        member = guild.get_member(int(uid))
        if member is None:
            try:
                member = await guild.fetch_member(int(uid))
            except discord.NotFound:
                pass
        name = member.display_name if member else f"User {uid}"
        lines.append(f"{MEDALS.get(i, f'`{i+1}.`')} **{name}** — {bal:,} {CURRENCY_EMOJI}")
    embed = discord.Embed(
        title=f"{CURRENCY_EMOJI} {CURRENCY_NAME} Leaderboard",
        description="\n".join(lines) or "No players yet.",
        color=0xF1C40F,
    )
    return tag_embed(embed, requester)


class LeaderboardView(discord.ui.View):
    def __init__(self, requester: discord.Member):
        super().__init__(timeout=180)
        self.requester = requester

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary, emoji="\U0001f504")
    async def refresh(self, interaction: discord.Interaction, _: discord.ui.Button):
        embed = await _build_embed(interaction.guild, self.requester)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@command("leaderboard", description="Top balances", usage="f.leaderboard", category="Casino")
@command("lb",          description="Top balances", usage="f.lb",          category="Casino")
async def leaderboard_command(message: Message, args: list[str]):
    embed = await _build_embed(message.guild, message.author)
    view  = LeaderboardView(message.author)
    await message.channel.send(embed=embed, view=view)
