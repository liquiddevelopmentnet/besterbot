"""Server-wide skin ranking — f.skinranking / f.skins
Shows the most valuable / rarest items across all players."""
import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import get_all_inventories, tag_embed, CURRENCY_EMOJI
from bot.commands.casino.items import item_full_name, RARITIES, RARITY_ORDER
from bot.strings import Skinranking as S

TOP_N = 15

# Rarity sort key: gold=4, pink=3, purple=2, blue=1, lightblue=0
_RARITY_RANK = {r: i for i, r in enumerate(RARITY_ORDER)}

MEDALS = {0: "🥇", 1: "🥈", 2: "🥉"}


def _collect_all_items(guild: discord.Guild) -> list[dict]:
    """Flatten all server members' inventories into one sorted list."""
    all_invs = get_all_inventories()
    flat: list[dict] = []
    for uid, items in all_invs.items():
        member = guild.get_member(int(uid))
        owner  = member.display_name if member else f"User {uid}"
        for it in items:
            flat.append({**it, "_owner": owner})
    return flat


def _build_embed(
    flat: list[dict],
    sort_by: str,           # "value" | "rarity"
    member: discord.Member,
) -> discord.Embed:
    if sort_by == "rarity":
        sorted_items = sorted(
            flat,
            key=lambda it: (_RARITY_RANK[it["rarity"]], it["sell_price"]),
            reverse=True,
        )
        title  = S.TITLE_RARITY
        footer = S.FOOTER_RARITY
    else:
        sorted_items = sorted(flat, key=lambda it: it["sell_price"], reverse=True)
        title  = S.TITLE_VALUE
        footer = S.FOOTER_VALUE

    top = sorted_items[:TOP_N]

    if not top:
        embed = discord.Embed(
            title       = title,
            description = S.EMPTY_DESC,
            color       = 0xF1C40F,
        )
        return tag_embed(embed, member)

    lines = []
    for i, it in enumerate(top):
        medal = MEDALS.get(i, f"`{i+1}.`")
        info  = RARITIES[it["rarity"]]
        name  = item_full_name(it)
        st    = "ST™ " if it["stattrak"] else ""
        lines.append(
            f"{medal} {info['emoji']} **{name}**\n"
            f"  👤 **{it['_owner']}** · {st}Float: `{it['float']:.4f}` · "
            f"**{it['sell_price']:,}** {CURRENCY_EMOJI}"
        )

    # Stats footer info
    total_items  = len(flat)
    total_value  = sum(it["sell_price"] for it in flat)
    gold_count   = sum(1 for it in flat if it["rarity"] == "gold")
    pink_count   = sum(1 for it in flat if it["rarity"] == "pink")

    embed = discord.Embed(
        title       = title,
        description = "\n\n".join(lines),
        color       = 0xFFD700 if sort_by == "rarity" else 0x2ECC71,
    )
    embed.add_field(
        name  = S.STATS_NAME,
        value = S.STATS_VALUE.format(total=total_items, total_value=total_value, CURRENCY_EMOJI=CURRENCY_EMOJI, gold=gold_count, pink=pink_count),
        inline = False,
    )
    embed.set_footer(text=footer)

    # Thumbnail: top item's image
    if top[0].get("image_url"):
        embed.set_thumbnail(url=top[0]["image_url"])

    return tag_embed(embed, member)


class SkinRankingView(discord.ui.View):
    def __init__(self, flat: list[dict], member: discord.Member):
        super().__init__(timeout=120)
        self.flat   = flat
        self.member = member
        self.mode   = "value"
        self._sync()

    def _sync(self) -> None:
        self.value_btn.disabled  = (self.mode == "value")
        self.rarity_btn.disabled = (self.mode == "rarity")

    @discord.ui.button(label=S.VALUE_BTN_LABEL, style=discord.ButtonStyle.success, emoji="💰")
    async def value_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.mode = "value"
        self._sync()
        await interaction.response.edit_message(
            embed=_build_embed(self.flat, "value", self.member), view=self
        )

    @discord.ui.button(label=S.RARITY_BTN_LABEL, style=discord.ButtonStyle.primary, emoji="⭐")
    async def rarity_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.mode = "rarity"
        self._sync()
        await interaction.response.edit_message(
            embed=_build_embed(self.flat, "rarity", self.member), view=self
        )

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


@command("skinranking", description=S.DESCRIPTION,
         usage="f.skinranking [value|rarity]", category="Casino")
@command("skins",       description=S.DESCRIPTION,
         usage="f.skins [value|rarity]",       category="Casino")
async def skinranking_command(message: Message, args: list[str]):
    sort_by = "value"
    if args and args[0].lower() in ("rarity", "seltenheit", "rare"):
        sort_by = "rarity"

    flat  = _collect_all_items(message.guild)
    embed = _build_embed(flat, sort_by, message.author)
    view  = SkinRankingView(flat, message.author)
    await message.reply(embed=embed, view=view)
