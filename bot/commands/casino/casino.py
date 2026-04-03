import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import tag_embed, CURRENCY_EMOJI, CURRENCY_NAME
from bot.strings import Casino as S

# ── Game catalogue ────────────────────────────────────────────────────────────

_GAMES = S.GAMES
_GAME_BY_ID = {g["id"]: g for g in _GAMES}

# ── Embed builders ────────────────────────────────────────────────────────────

def _build_overview_embed(member: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title=S.OVERVIEW_TITLE.format(CURRENCY_NAME=CURRENCY_NAME),
        description=S.OVERVIEW_DESC.format(CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0xF1C40F,
    )
    for game in _GAMES:
        embed.add_field(name=game["ov_name"], value=game["ov_value"], inline=False)
    embed.set_footer(text=S.OVERVIEW_FOOTER)
    return tag_embed(embed, member)


def _build_detail_embed(game_id: str, member: discord.Member) -> discord.Embed:
    g = _GAME_BY_ID[game_id]
    # Some detail_title/desc entries have {CURRENCY_NAME}/{CURRENCY_EMOJI} placeholders
    detail_title = g["detail_title"].format(CURRENCY_NAME=CURRENCY_NAME) if "{CURRENCY_NAME}" in g["detail_title"] else g["detail_title"]
    embed = discord.Embed(
        title=detail_title,
        description=g["detail_desc"],
        color=0xF1C40F,
    )
    for name, value, inline in g["detail_fields"]:
        # Some field values have {CURRENCY_EMOJI} placeholders
        value = value.format(CURRENCY_EMOJI=CURRENCY_EMOJI) if "{CURRENCY_EMOJI}" in value else value
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_footer(text=S.DETAIL_FOOTER)
    return tag_embed(embed, member)

# ── View ──────────────────────────────────────────────────────────────────────

class CasinoView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=300)
        self.member      = member
        self._detail_mode = False
        self._build_buttons()

    def _build_buttons(self, *, show_back: bool = False):
        self.clear_items()

        for game in _GAMES:
            btn = discord.ui.Button(
                label=game["label"],
                emoji=game["emoji"],
                style=discord.ButtonStyle.primary,
                row=game["row"],
            )
            btn.callback = self._make_game_cb(game["id"])
            self.add_item(btn)

        if show_back:
            back = discord.ui.Button(
                label=S.BACK_LABEL,
                emoji="◀️",
                style=discord.ButtonStyle.secondary,
                row=2,
            )
            back.callback = self._do_back
            self.add_item(back)

    def _make_game_cb(self, game_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.member.id:
                await interaction.response.send_message(
                    S.NOT_YOUR_MENU, ephemeral=True
                )
                return
            self._build_buttons(show_back=True)
            embed = _build_detail_embed(game_id, self.member)
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _do_back(self, interaction: discord.Interaction):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                S.NOT_YOUR_MENU, ephemeral=True
            )
            return
        self._build_buttons(show_back=False)
        embed = _build_overview_embed(self.member)
        await interaction.response.edit_message(embed=embed, view=self)

# ── Command ───────────────────────────────────────────────────────────────────

@command("casino", description=S.DESCRIPTION.format(CURRENCY_NAME=CURRENCY_NAME), usage="f.casino", category="Casino")
async def casino_command(message: Message, args: list[str]):
    view  = CasinoView(message.author)
    embed = _build_overview_embed(message.author)
    await message.channel.send(embed=embed, view=view)
