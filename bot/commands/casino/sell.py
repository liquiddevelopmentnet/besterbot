"""Item selling — f.sell <#|all> [rarity]"""
import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_inventory, remove_item, add_balance, tag_embed,
    CURRENCY_EMOJI,
)
from bot.commands.casino.items import item_full_name, RARITIES, RARITY_ORDER

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
            await interaction.response.send_message("Nicht dein Deal!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Bestätigen", style=discord.ButtonStyle.danger, emoji="💰")
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
            title="💰 Verkauft",
            description=(
                f"**{len(self.to_sell)}** Items für "
                f"**{total:,}** {CURRENCY_EMOJI} verkauft."
            ),
            color=0x2ECC71,
        )
        tag_embed(embed, self.member)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            content="Verkauf abgebrochen.", embed=None, view=self
        )

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


@command("sell", description="Verkaufe Items: f.sell 3  |  f.sell 3,5,2  |  f.sell all",
         usage="f.sell <#[,#,...]|all> [rarity]", category="Casino")
async def sell_command(message: Message, args: list[str]):
    if not args:
        await message.reply(
            "**Verwendung:**\n"
            "`f.sell 3` — Verkaufe Item #3\n"
            "`f.sell 3,5,2` — Verkaufe Items #3, #5 und #2 auf einmal\n"
            "`f.sell all` — Verkaufe alle Items\n"
            "`f.sell all lightblue` — Verkaufe alle Items einer Seltenheit"
        )
        return

    inv = get_inventory(message.author.id)

    # ── sell all ────────────────────────────────────────────────────────────
    if args[0].lower() == "all":
        rarity_filter = None
        if len(args) >= 2:
            rarity_filter = _RARITY_ALIASES.get(args[1].lower())
            if rarity_filter is None:
                await message.reply(
                    f"Unbekannte Seltenheit `{args[1]}`. "
                    f"Mögliche Werte: `lightblue`, `blue`, `purple`, `pink`, `gold`"
                )
                return

        to_sell = [it for it in inv if rarity_filter is None or it["rarity"] == rarity_filter]

        if not to_sell:
            label = f" mit Seltenheit **{rarity_filter}**" if rarity_filter else ""
            await message.reply(f"Du hast keine Items{label} im Inventar.")
            return

        total_value = sum(it["sell_price"] for it in to_sell)
        lines = []
        for r in RARITY_ORDER:
            count = sum(1 for it in to_sell if it["rarity"] == r)
            if count:
                lines.append(f"{RARITIES[r]['emoji']} {RARITIES[r]['label']}: **{count}x**")

        embed = discord.Embed(
            title="💰 Alles verkaufen?",
            description=(
                f"Du willst **{len(to_sell)} Items** für "
                f"**{total_value:,}** {CURRENCY_EMOJI} verkaufen:\n\n"
                + "\n".join(lines)
            ),
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
        await message.reply(
            "Gib Inventarnummern an, z. B. `f.sell 3` oder `f.sell 3,5,2`."
        )
        return

    if not inv:
        await message.reply("Dein Inventar ist leer.")
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
        await message.reply(
            f"Ungültige Nummer(n): `{', '.join(bad)}`. Du hast **{len(inv)}** Items (#1–#{len(inv)})."
        )
        return

    # Sell all selected items
    total = 0
    sold: list[dict] = []
    for item in to_sell:
        if remove_item(message.author.id, item["id"]) is not None:
            total += item["sell_price"]
            sold.append(item)

    if not sold:
        await message.reply("Konnte keine Items verkaufen — versuch es nochmal.")
        return

    add_balance(message.author.id, total)

    if len(sold) == 1:
        item = sold[0]
        info = RARITIES[item["rarity"]]
        embed = discord.Embed(
            title="💰 Item verkauft",
            description=(
                f"{info['emoji']} **{item_full_name(item)}**\n"
                f"Verkauft für **{item['sell_price']:,}** {CURRENCY_EMOJI}"
            ),
            color=0x2ECC71,
        )
    else:
        lines = [
            f"{RARITIES[it['rarity']]['emoji']} **{item_full_name(it)}** — "
            f"**{it['sell_price']:,}** {CURRENCY_EMOJI}"
            for it in sold
        ]
        embed = discord.Embed(
            title="💰 Items verkauft",
            description="\n".join(lines),
            color=0x2ECC71,
        )
        embed.add_field(name="Gesamt", value=f"**{total:,}** {CURRENCY_EMOJI}", inline=False)

    tag_embed(embed, message.author)
    await message.reply(embed=embed)
