"""Inventory viewer — f.inventory [@user] [sort] / f.inv [@user] [sort]"""
import math

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import get_inventory, tag_embed, CURRENCY_EMOJI
from bot.commands.casino.items import item_full_name, RARITIES, RARITY_ORDER

ITEMS_PER_PAGE = 5

SORT_MODES = {
    "default":  ("Standard",        lambda it: 0),
    "value":    ("Wert ↓",          lambda it: -it["sell_price"]),
    "rarity":   ("Seltenheit ↓",    lambda it: -RARITY_ORDER.index(it["rarity"])),
    "float":    ("Float ↑",         lambda it: it["float"]),
}


def _sort_items(items: list, mode: str) -> list:
    key = SORT_MODES.get(mode, SORT_MODES["default"])[1]
    return sorted(items, key=key)


def _inv_embed(
    items: list,
    page: int,
    total_pages: int,
    target: discord.Member,
    sort_mode: str,
    *,
    own: bool = True,
) -> discord.Embed:
    title = "🎒 Dein Inventar" if own else f"🎒 {target.display_name}'s Inventar"
    embed = discord.Embed(title=title, color=0x2C2F33)

    if not items:
        if own:
            embed.description = (
                "Dein Inventar ist leer!\n"
                "Öffne eine Case mit `f.case` für **800** Maka."
            )
        else:
            embed.description = f"**{target.display_name}** hat noch keine Items."
        return tag_embed(embed, target)

    start      = page * ITEMS_PER_PAGE
    page_items = items[start : start + ITEMS_PER_PAGE]
    lines      = []

    for idx, item in enumerate(page_items, start=start + 1):
        info = RARITIES[item["rarity"]]
        name = item_full_name(item)
        st   = "ST " if item["stattrak"] else ""
        lines.append(
            f"**`#{idx}`** {info['emoji']} **{name}**\n"
            f"  Float: `{item['float']:.6f}` · Pattern: `{item['pattern']}` · "
            f"{st}Wert: **{item['sell_price']:,}** {CURRENCY_EMOJI} · ID: `{item['id']}`"
        )

    total_value = sum(it["sell_price"] for it in items)
    by_rarity   = {r: sum(1 for it in items if it["rarity"] == r) for r in RARITY_ORDER}
    rarity_str  = "  ".join(
        f"{RARITIES[r]['emoji']} {by_rarity[r]}"
        for r in RARITY_ORDER
        if by_rarity[r] > 0
    )

    sort_label = SORT_MODES.get(sort_mode, SORT_MODES["default"])[0]

    embed.description = "\n\n".join(lines)
    embed.add_field(name="Inventarwert", value=f"**{total_value:,}** {CURRENCY_EMOJI}", inline=True)
    embed.add_field(name="Items",        value=rarity_str or "—",                       inline=True)

    footer_suffix = "  ·  f.sell <#> zum Verkaufen" if own else ""
    embed.set_footer(
        text=(
            f"Seite {page + 1}/{total_pages}  ·  {len(items)} Items"
            f"  ·  Sortierung: {sort_label}{footer_suffix}"
        )
    )

    thumb_item = max(page_items, key=lambda it: RARITY_ORDER.index(it["rarity"]))
    if thumb_item.get("image_url"):
        embed.set_thumbnail(url=thumb_item["image_url"])

    return tag_embed(embed, target)


class InventoryView(discord.ui.View):
    def __init__(
        self,
        viewer_id: int,
        target: discord.Member,
        raw_items: list,       # unsorted original list
        *,
        own: bool = True,
        sort_mode: str = "default",
    ):
        super().__init__(timeout=120)
        self.viewer_id  = viewer_id
        self.target     = target
        self.raw_items  = raw_items
        self.own        = own
        self.sort_mode  = sort_mode
        self.items      = _sort_items(raw_items, sort_mode)
        self.page       = 0
        self.total_pages = max(1, math.ceil(len(self.items) / ITEMS_PER_PAGE))
        self._sync()

    def _sync(self) -> None:
        self.prev_btn.disabled    = self.page == 0
        self.next_btn.disabled    = self.page >= self.total_pages - 1
        # highlight active sort button
        self.sort_value_btn.style  = (
            discord.ButtonStyle.primary if self.sort_mode == "value"  else discord.ButtonStyle.secondary
        )
        self.sort_rarity_btn.style = (
            discord.ButtonStyle.primary if self.sort_mode == "rarity" else discord.ButtonStyle.secondary
        )
        self.sort_float_btn.style  = (
            discord.ButtonStyle.primary if self.sort_mode == "float"  else discord.ButtonStyle.secondary
        )

    def _current_embed(self) -> discord.Embed:
        return _inv_embed(
            self.items, self.page, self.total_pages,
            self.target, self.sort_mode, own=self.own,
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.viewer_id:
            await interaction.response.send_message(
                "Nur der Aufrufer kann blättern!", ephemeral=True
            )
            return False
        return True

    # ── pagination ────────────────────────────────────────────────────────────
    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary, row=0)
    async def prev_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.page -= 1
        self._sync()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary, row=0)
    async def next_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.page += 1
        self._sync()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    # ── sort buttons ──────────────────────────────────────────────────────────
    @discord.ui.button(label="💰 Wert", style=discord.ButtonStyle.secondary, row=1)
    async def sort_value_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.sort_mode  = "default" if self.sort_mode == "value" else "value"
        self.items      = _sort_items(self.raw_items, self.sort_mode)
        self.page       = 0
        self.total_pages = max(1, math.ceil(len(self.items) / ITEMS_PER_PAGE))
        self._sync()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    @discord.ui.button(label="⭐ Seltenheit", style=discord.ButtonStyle.secondary, row=1)
    async def sort_rarity_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.sort_mode  = "default" if self.sort_mode == "rarity" else "rarity"
        self.items      = _sort_items(self.raw_items, self.sort_mode)
        self.page       = 0
        self.total_pages = max(1, math.ceil(len(self.items) / ITEMS_PER_PAGE))
        self._sync()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    @discord.ui.button(label="🔢 Float", style=discord.ButtonStyle.secondary, row=1)
    async def sort_float_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        self.sort_mode  = "default" if self.sort_mode == "float" else "float"
        self.items      = _sort_items(self.raw_items, self.sort_mode)
        self.page       = 0
        self.total_pages = max(1, math.ceil(len(self.items) / ITEMS_PER_PAGE))
        self._sync()
        await interaction.response.edit_message(embed=self._current_embed(), view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


@command("inventory", description="Zeige Inventar (eigenes oder von @user)",
         usage="f.inventory [@user]", category="Casino")
@command("inv",       description="Zeige Inventar (eigenes oder von @user)",
         usage="f.inv [@user]",       category="Casino")
async def inventory_command(message: Message, args: list[str]):
    if message.mentions:
        target = message.mentions[0]
        own    = (target.id == message.author.id)
    else:
        target = message.author
        own    = True

    # Optional sort arg: f.inventory value / f.inventory rarity / f.inventory float
    sort_mode = "default"
    for a in args:
        if a.lower() in SORT_MODES:
            sort_mode = a.lower()
            break

    raw_items   = get_inventory(target.id)
    items       = _sort_items(raw_items, sort_mode)
    total_pages = max(1, math.ceil(len(items) / ITEMS_PER_PAGE))
    embed       = _inv_embed(items, 0, total_pages, target, sort_mode, own=own)
    view        = InventoryView(message.author.id, target, raw_items, own=own, sort_mode=sort_mode)
    await message.reply(embed=embed, view=view)
