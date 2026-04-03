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
from bot.strings import Tradeup as S

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
            await interaction.response.send_message(S.NOT_YOUR_TRADEUP, ephemeral=True)
            return False
        return True

    @discord.ui.button(label=S.CONFIRM_LABEL, style=discord.ButtonStyle.success, emoji="⬆️")
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
                content=S.MISSING_ITEMS,
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
            title=S.SUCCESS_TITLE,
            description=S.SUCCESS_DESC.format(
                from_emoji=RARITIES[self.rarity]['emoji'],
                from_label=RARITIES[self.rarity]['label'],
                to_emoji=info['emoji'],
                to_label=info['label'],
            ),
            color=info["color"],
        )
        embed.add_field(name=S.FIELD_ERHALTEN,  value=f"**{item_full_name(result)}**", inline=False)
        embed.add_field(name=S.FIELD_FLOAT,     value=f"`{result['float']:.6f}`",      inline=True)
        embed.add_field(name=S.FIELD_PATTERN,   value=f"`{result['pattern']}`",        inline=True)
        embed.add_field(name=S.FIELD_STATTRAK,  value="✅" if result["stattrak"] else "❌", inline=True)
        embed.add_field(
            name=S.FIELD_SELL,
            value=f"**{result['sell_price']:,}** {CURRENCY_EMOJI}",
            inline=True,
        )
        if result.get("image_url"):
            embed.set_image(url=result["image_url"])
        tag_embed(embed, self.member)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=S.CANCEL_LABEL, style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        self._disable_all()
        await interaction.response.edit_message(content=S.CANCEL_CONTENT, embed=None, view=self)

    def _disable_all(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        self._disable_all()


@command("tradeup", description=S.DESCRIPTION,
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
            title=S.OVERVIEW_TITLE,
            description=S.OVERVIEW_DESC.format(lines="\n".join(lines)),
            color=0x5865F2,
        )
        embed.set_footer(text=S.OVERVIEW_FOOTER)
        tag_embed(embed, message.author)
        await message.reply(embed=embed)
        return

    # ── Rarity given: confirm trade up ──────────────────────────────────────
    rarity = _RARITY_ALIASES.get(args[0].lower())
    if rarity is None:
        await message.reply(S.INVALID_RARITY)
        return

    candidates = [it for it in inv if it["rarity"] == rarity]
    if len(candidates) < TRADE_UP_COUNT:
        await message.reply(
            S.NOT_ENOUGH_ITEMS.format(
                count=TRADE_UP_COUNT,
                emoji=RARITIES[rarity]['emoji'],
                label=RARITIES[rarity]['label'],
                have=len(candidates),
            )
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
        title=S.CONFIRM_TITLE,
        description=S.CONFIRM_DESC.format(
            from_emoji=RARITIES[rarity]['emoji'],
            from_label=RARITIES[rarity]['label'],
            total_in=total_in,
            CURRENCY_EMOJI=CURRENCY_EMOJI,
            to_emoji=RARITIES[next_r]['emoji'],
            to_label=RARITIES[next_r]['label'],
        ),
        color=RARITIES[rarity]["color"],
    )
    embed.add_field(name=S.FIELD_ITEMS_IN, value="\n".join(lines), inline=False)
    tag_embed(embed, message.author)

    view = TradeUpConfirmView(message.author.id, message.author, rarity, cheapest)
    await message.reply(embed=embed, view=view)
