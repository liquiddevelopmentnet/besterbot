"""Inventory viewer — f.inventory [@user] [sort] / f.inv [@user] [sort]"""
import math

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import get_inventory, remove_item, add_balance, log_earning, tag_embed, CURRENCY_EMOJI
from bot.commands.casino.items import item_full_name, RARITIES, RARITY_ORDER
from bot.strings import Inventory as S

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
    title = S.TITLE_OWN if own else S.TITLE_OTHER.format(name=target.display_name)
    embed = discord.Embed(title=title, color=0x2C2F33)

    if not items:
        if own:
            embed.description = S.EMPTY_OWN
        else:
            embed.description = S.EMPTY_OTHER.format(name=target.display_name)
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
    embed.add_field(name=S.FIELD_WORTH, value=f"**{total_value:,}** {CURRENCY_EMOJI}", inline=True)
    embed.add_field(name=S.FIELD_ITEMS, value=rarity_str or "—",                       inline=True)
    embed.set_footer(
        text=S.FOOTER.format(page=page + 1, total=total_pages, count=len(items), sort=sort_label)
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
        raw_items: list,
        *,
        own: bool = True,
        sort_mode: str = "default",
    ):
        super().__init__(timeout=120)
        self.viewer_id   = viewer_id
        self.target      = target
        self.raw_items   = raw_items
        self.own         = own
        self.sort_mode   = sort_mode
        self.items       = _sort_items(raw_items, sort_mode)
        self.page        = 0
        self.total_pages = max(1, math.ceil(len(self.items) / ITEMS_PER_PAGE))
        self._rebuild()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.viewer_id:
            await interaction.response.send_message(S.NOT_YOURS, ephemeral=True)
            return False
        return True

    def _current_embed(self) -> discord.Embed:
        return _inv_embed(
            self.items, self.page, self.total_pages,
            self.target, self.sort_mode, own=self.own,
        )

    def _page_items(self) -> list:
        start = self.page * ITEMS_PER_PAGE
        return self.items[start : start + ITEMS_PER_PAGE]

    def _rebuild(self) -> None:
        self.clear_items()

        # ── Row 0: sort buttons ───────────────────────────────────────────────
        for mode, (label, _) in [
            ("value",  (S.SORT_VALUE_LABEL,  None)),
            ("rarity", (S.SORT_RARITY_LABEL, None)),
            ("float",  (S.SORT_FLOAT_LABEL,  None)),
        ]:
            btn = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.primary if self.sort_mode == mode else discord.ButtonStyle.secondary,
                row=0,
            )
            captured_mode = mode
            async def _sort_cb(interaction: discord.Interaction, _btn=None, _mode=captured_mode):
                self.sort_mode   = "default" if self.sort_mode == _mode else _mode
                self.items       = _sort_items(self.raw_items, self.sort_mode)
                self.page        = 0
                self.total_pages = max(1, math.ceil(len(self.items) / ITEMS_PER_PAGE))
                self._rebuild()
                await interaction.response.edit_message(embed=self._current_embed(), view=self)
            btn.callback = _sort_cb
            self.add_item(btn)

        # ── Row 1: page Select (only when more than 1 page) ──────────────────
        if self.total_pages > 1:
            # Discord Select options capped at 25
            max_opts = min(self.total_pages, 25)
            options = [
                discord.SelectOption(
                    label=f"Seite {p + 1} / {self.total_pages}",
                    value=str(p),
                    default=(p == self.page),
                )
                for p in range(max_opts)
            ]
            page_select = discord.ui.Select(
                placeholder=S.PAGE_SELECT_PLACEHOLDER,
                options=options,
                row=1,
            )
            async def _page_cb(interaction: discord.Interaction):
                self.page = int(page_select.values[0])
                self._rebuild()
                await interaction.response.edit_message(embed=self._current_embed(), view=self)
            page_select.callback = _page_cb
            self.add_item(page_select)

        # ── Row 2: sell multi-select (own inventory, non-empty page) ─────────
        if self.own and self.items:
            page_items = self._page_items()
            sell_options = []
            for item in page_items:
                info  = RARITIES[item["rarity"]]
                label = item_full_name(item)[:100]
                desc  = f"{item['sell_price']:,} {CURRENCY_EMOJI}"[:100]
                sell_options.append(
                    discord.SelectOption(
                        label=label,
                        description=desc,
                        value=item["id"],
                        emoji=info["emoji"],
                    )
                )
            sell_select = discord.ui.Select(
                placeholder=S.SELL_SELECT_PLACEHOLDER,
                options=sell_options,
                min_values=1,
                max_values=len(sell_options),
                row=2,
            )
            async def _sell_cb(interaction: discord.Interaction):
                sold_ids    = set(sell_select.values)
                sold_items  = [it for it in self.items if it["id"] in sold_ids]
                total_price = sum(it["sell_price"] for it in sold_items)
                for it in sold_items:
                    remove_item(self.viewer_id, it["id"])
                    add_balance(self.viewer_id, it["sell_price"])
                    log_earning(self.viewer_id, it["sell_price"])
                # Refresh view with updated inventory
                self.raw_items   = get_inventory(self.viewer_id)
                self.items       = _sort_items(self.raw_items, self.sort_mode)
                self.total_pages = max(1, math.ceil(len(self.items) / ITEMS_PER_PAGE))
                self.page        = min(self.page, max(0, self.total_pages - 1))
                self._rebuild()
                await interaction.response.edit_message(
                    content=S.SELL_RESULT.format(
                        count=len(sold_items), total=total_price, CURRENCY_EMOJI=CURRENCY_EMOJI
                    ),
                    embed=self._current_embed(),
                    view=self,
                )
            sell_select.callback = _sell_cb
            self.add_item(sell_select)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


@command("inventory", description=S.DESCRIPTION,
         usage="f.inventory [@user]", category="Casino")
@command("inv",       description=S.DESCRIPTION,
         usage="f.inv [@user]",       category="Casino")
async def inventory_command(message: Message, args: list[str]):
    if message.mentions:
        target = message.mentions[0]
        own    = (target.id == message.author.id)
    else:
        target = message.author
        own    = True

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
