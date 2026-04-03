import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import get_leaderboard_with_worth, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI
from bot.strings import Leaderboard as S

MEDALS = {0: "\U0001f947", 1: "\U0001f948", 2: "\U0001f949"}


async def _build_embed(guild: discord.Guild, requester: discord.Member) -> discord.Embed:
    board = get_leaderboard_with_worth(10)
    lines = []
    for i, (uid, bal, inv_worth) in enumerate(board):
        member = guild.get_member(int(uid))
        if member is None:
            try:
                member = await guild.fetch_member(int(uid))
            except discord.NotFound:
                pass
        name  = member.display_name if member else f"User {uid}"
        total = bal + inv_worth
        line  = f"{MEDALS.get(i, f'`{i+1}.`')} **{name}** — {bal:,} {CURRENCY_EMOJI}"
        if inv_worth > 0:
            line += f"  *(+{inv_worth:,} inv — {total:,} total)*"
        lines.append(line)
    embed = discord.Embed(
        title=S.TITLE.format(CURRENCY_EMOJI=CURRENCY_EMOJI, CURRENCY_NAME=CURRENCY_NAME),
        description="\n".join(lines) or S.EMPTY,
        color=0xF1C40F,
    )
    embed.set_footer(text=S.FOOTER)
    return tag_embed(embed, requester)


class LeaderboardView(discord.ui.View):
    def __init__(self, requester: discord.Member):
        super().__init__(timeout=180)
        self.requester = requester

    @discord.ui.button(label=S.REFRESH_LABEL, style=discord.ButtonStyle.secondary, emoji="\U0001f504")
    async def refresh(self, interaction: discord.Interaction, _: discord.ui.Button):
        embed = await _build_embed(interaction.guild, self.requester)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@command("leaderboard", description=S.DESCRIPTION, usage="f.leaderboard", category="Casino")
@command("lb",          description=S.DESCRIPTION, usage="f.lb",          category="Casino")
async def leaderboard_command(message: Message, args: list[str]):
    embed = await _build_embed(message.guild, message.author)
    view  = LeaderboardView(message.author)
    await message.channel.send(embed=embed, view=view)
