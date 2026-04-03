"""Item selling — f.sell <#|all> [rarity]"""
import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_inventory, remove_item, add_balance, tag_embed,
    CURRENCY_EMOJI,
)
from bot.commands.casino.items import item_full_name, RARITIES, RARITY_ORDER
from bot.strings import Sell as S

_RARITY_ALIASES: dict[str, str] = {
    "lightblue": "lightblue", "lb": "lightblue", "blau": "lightblue",
    "blue":      "blue",      "bl": "blue",
    "purple":    "purple",    "lila": "purple",  "pu": "purple",
    "pink":      "pink",      "pi": "pink",
    "gold":      "gold",      "ge": "gold",
}


class SellAllConfirmView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member, to_sell: list):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.member  = member
        self.to_sell = to_sell
        self._done   = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(S.NOT_YOUR_DEAL, ephemeral=True)
            return False
        return True

    @discord.ui.button(label=S.CONFIRM_LABEL, style=discord.ButtonStyle.danger, emoji="💰")
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        total = 0
        for item in self.to_sell:
            if remove_item(self.user_id, item["id"]) is not None:
                total += item["sell_price"]
        add_balance(self.user_id, total)
        for child in self.children:
            child.disabled = True
        embed = discord.Embed(
            title=S.SOLD_BULK_TITLE,
            description=S.SOLD_BULK_DESC.format(count=len(self.to_sell), total=total, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0x2ECC71,
        )
        tag_embed(embed, self.member)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=S.CANCEL_LABEL, style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            content=S.CANCEL_CONTENT, embed=None, view=self
        )

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


@command("sell", description=S.DESCRIPTION,
         usage="f.sell <#[,#,...]|all> [rarity]", category="Casino")
async def sell_command(message: Message, args: list[str]):
    if not args:
        await message.reply(S.USAGE)
        return

    inv = get_inventory(message.author.id)

    # ── sell all ────────────────────────────────────────────────────────────
    if args[0].lower() == "all":
        rarity_filter = None
        if len(args) >= 2:
            rarity_filter = _RARITY_ALIASES.get(args[1].lower())
            if rarity_filter is None:
                await message.reply(S.UNKNOWN_RARITY.format(rarity=args[1]))
                return

        to_sell = [it for it in inv if rarity_filter is None or it["rarity"] == rarity_filter]

        if not to_sell:
            label = S.NO_ITEMS_LABEL.format(rarity=rarity_filter) if rarity_filter else ""
            await message.reply(S.NO_ITEMS.format(label=label))
            return

        total_value = sum(it["sell_price"] for it in to_sell)
        lines = []
        for r in RARITY_ORDER:
            count = sum(1 for it in to_sell if it["rarity"] == r)
            if count:
                lines.append(f"{RARITIES[r]['emoji']} {RARITIES[r]['label']}: **{count}x**")

        embed = discord.Embed(
            title=S.CONFIRM_TITLE,
            description=S.CONFIRM_DESC.format(count=len(to_sell), total=total_value, CURRENCY_EMOJI=CURRENCY_EMOJI, lines="\n".join(lines)),
            color=0xE74C3C,
        )
        tag_embed(embed, message.author)
        view = SellAllConfirmView(message.author.id, message.author, to_sell)
        await message.reply(embed=embed, view=view)
        return

    # ── sell by index (single or multi: "3", "3 5 2", "3,5,2", "3,5 2") ──────
    # Combine all args and split on commas + spaces to support every format
    tokens = " ".join(args).replace(",", " ").split()

    if not all(t.isdigit() for t in tokens):
        await message.reply(S.INVALID_NUMBERS)
        return

    if not inv:
        await message.reply(S.EMPTY_INV)
        return

    # Resolve indices (1-based, deduplicated, preserve order)
    seen: set[int] = set()
    to_sell: list[dict] = []
    bad: list[str] = []

    for t in tokens:
        idx = int(t) - 1
        if idx < 0 or idx >= len(inv):
            bad.append(t)
        elif idx not in seen:
            seen.add(idx)
            to_sell.append(inv[idx])

    if bad:
        await message.reply(S.INVALID_IDX.format(nums=', '.join(bad), count=len(inv)))
        return

    # Sell all selected items
    total = 0
    sold: list[dict] = []
    for item in to_sell:
        if remove_item(message.author.id, item["id"]) is not None:
            total += item["sell_price"]
            sold.append(item)

    if not sold:
        await message.reply(S.SELL_FAILED)
        return

    add_balance(message.author.id, total)

    if len(sold) == 1:
        item = sold[0]
        info = RARITIES[item["rarity"]]
        embed = discord.Embed(
            title=S.SOLD_TITLE_SINGLE,
            description=S.SOLD_DESC_SINGLE.format(emoji=info['emoji'], name=item_full_name(item), price=item['sell_price'], CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0x2ECC71,
        )
    else:
        lines = [
            f"{RARITIES[it['rarity']]['emoji']} **{item_full_name(it)}** — "
            f"**{it['sell_price']:,}** {CURRENCY_EMOJI}"
            for it in sold
        ]
        embed = discord.Embed(
            title=S.SOLD_TITLE_MULTI,
            description="\n".join(lines),
            color=0x2ECC71,
        )
        embed.add_field(name=S.SOLD_FIELD_GESAMT, value=f"**{total:,}** {CURRENCY_EMOJI}", inline=False)

    tag_embed(embed, message.author)
    await message.reply(embed=embed)
