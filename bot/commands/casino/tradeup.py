"""CS2-style Trade Up Contract — f.tradeup [rarity]
10 items of the same grade → 1 item of the next grade up.
Auto-selects the 10 cheapest items of the chosen rarity."""
import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_inventory, remove_item, add_item, tag_embed, CURRENCY_EMOJI,
)
from bot.commands.casino.items import (
    create_item, item_full_name, RARITIES, RARITY_ORDER,
)

TRADE_UP_COUNT = 10

_RARITY_ALIASES: dict[str, str] = {
    "lightblue": "lightblue", "lb": "lightblue", "blau":  "lightblue",
    "blue":      "blue",      "bl": "blue",
    "purple":    "purple",    "lila": "purple",   "pu":    "purple",
    "pink":      "pink",      "pi":  "pink",
}
# Gold can't be traded up


def _next_rarity(rarity: str) -> str | None:
    idx = RARITY_ORDER.index(rarity)
    if idx >= len(RARITY_ORDER) - 1:
        return None
    return RARITY_ORDER[idx + 1]


class TradeUpConfirmView(discord.ui.View):
    def __init__(
        self,
        user_id: int,
        member: discord.Member,
        rarity: str,
        items: list,
    ):
        super().__init__(timeout=60)
        self.user_id   = user_id
        self.member    = member
        self.rarity    = rarity
        self.items     = items  # exactly 10 items to consume
        self._done     = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Nicht dein Trade Up!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Trade Up!", style=discord.ButtonStyle.success, emoji="⬆️")
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        self._disable_all()

        # Re-fetch inventory to ensure items still exist
        current_inv = get_inventory(self.user_id)
        current_ids = {it["id"] for it in current_inv}
        missing = [it for it in self.items if it["id"] not in current_ids]
        if missing:
            await interaction.response.edit_message(
                content="❌ Einige Items wurden zwischenzeitlich entfernt. Trade Up abgebrochen.",
                embed=None,
                view=self,
            )
            return

        # Remove the 10 items
        for it in self.items:
            remove_item(self.user_id, it["id"])

        # Generate result item of next rarity
        next_rarity = _next_rarity(self.rarity)
        result = create_item(next_rarity)
        add_item(self.user_id, result)

        info = RARITIES[result["rarity"]]
        embed = discord.Embed(
            title="⬆️ Trade Up erfolgreich!",
            description=(
                f"10× {RARITIES[self.rarity]['emoji']} {RARITIES[self.rarity]['label']} "
                f"→ {info['emoji']} **{info['label']}**"
            ),
            color=info["color"],
        )
        embed.add_field(name="Erhalten",   value=f"**{item_full_name(result)}**", inline=False)
        embed.add_field(name="Float",      value=f"`{result['float']:.6f}`",      inline=True)
        embed.add_field(name="Pattern",    value=f"`{result['pattern']}`",        inline=True)
        embed.add_field(name="StatTrak™",  value="✅" if result["stattrak"] else "❌", inline=True)
        embed.add_field(
            name="Verkaufswert",
            value=f"**{result['sell_price']:,}** {CURRENCY_EMOJI}",
            inline=True,
        )
        if result.get("image_url"):
            embed.set_image(url=result["image_url"])
        tag_embed(embed, self.member)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        self._disable_all()
        await interaction.response.edit_message(content="Trade Up abgebrochen.", embed=None, view=self)

    def _disable_all(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        self._disable_all()


@command("tradeup", description="Tausche 10 Items einer Seltenheit für 1 Item der nächsten Stufe",
         usage="f.tradeup [lightblue|blue|purple|pink]", category="Casino")
async def tradeup_command(message: Message, args: list[str]):
    inv = get_inventory(message.author.id)

    # ── No rarity given: show overview ──────────────────────────────────────
    if not args:
        lines = []
        for rarity in RARITY_ORDER[:-1]:  # gold can't be traded up
            count = sum(1 for it in inv if it["rarity"] == rarity)
            next_r = _next_rarity(rarity)
            status = f"✅ {count}/10" if count >= TRADE_UP_COUNT else f"❌ {count}/10"
            lines.append(
                f"{RARITIES[rarity]['emoji']} **{RARITIES[rarity]['label']}** {status} "
                f"→ {RARITIES[next_r]['emoji']} {RARITIES[next_r]['label']}"
            )
        embed = discord.Embed(
            title="⬆️ Trade Up Contract",
            description=(
                "Tausche **10 Items** gleicher Seltenheit gegen **1 Item** der nächsten Stufe.\n"
                "Die 10 günstigsten Items werden automatisch ausgewählt.\n\n"
                + "\n".join(lines)
            ),
            color=0x5865F2,
        )
        embed.set_footer(text="f.tradeup <lightblue|blue|purple|pink>")
        tag_embed(embed, message.author)
        await message.reply(embed=embed)
        return

    # ── Rarity given: confirm trade up ──────────────────────────────────────
    rarity = _RARITY_ALIASES.get(args[0].lower())
    if rarity is None:
        await message.reply(
            "Ungültige Seltenheit. Mögliche Werte: `lightblue`, `blue`, `purple`, `pink`\n"
            "(Gold kann nicht geupgradet werden)"
        )
        return

    candidates = [it for it in inv if it["rarity"] == rarity]
    if len(candidates) < TRADE_UP_COUNT:
        await message.reply(
            f"Du brauchst mindestens **{TRADE_UP_COUNT}** "
            f"{RARITIES[rarity]['emoji']} {RARITIES[rarity]['label']} Items. "
            f"Aktuell hast du **{len(candidates)}**."
        )
        return

    # Select 10 cheapest
    cheapest = sorted(candidates, key=lambda it: it["sell_price"])[:TRADE_UP_COUNT]
    next_r   = _next_rarity(rarity)
    total_in = sum(it["sell_price"] for it in cheapest)

    lines = [
        f"`#{i+1}` {item_full_name(it)} — **{it['sell_price']:,}** {CURRENCY_EMOJI}"
        for i, it in enumerate(cheapest)
    ]
    embed = discord.Embed(
        title="⬆️ Trade Up Contract",
        description=(
            f"Diese **10** {RARITIES[rarity]['emoji']} {RARITIES[rarity]['label']} Items "
            f"(Gesamtwert: **{total_in:,}** {CURRENCY_EMOJI}) werden getauscht gegen\n"
            f"**1** {RARITIES[next_r]['emoji']} {RARITIES[next_r]['label']} Item:"
        ),
        color=RARITIES[rarity]["color"],
    )
    embed.add_field(name="Einzutauschende Items", value="\n".join(lines), inline=False)
    tag_embed(embed, message.author)

    view = TradeUpConfirmView(message.author.id, message.author, rarity, cheapest)
    await message.reply(embed=embed, view=view)
