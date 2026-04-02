"""CS2-style trade offers between players — f.tradeoffer @user <item_numbers...>
Pending offers are stored in memory and expire after 5 minutes."""
import time
import uuid

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_inventory, trade_items, tag_embed, CURRENCY_EMOJI,
)
from bot.commands.casino.items import item_full_name, RARITIES

# ── In-memory pending trades (expire after OFFER_TTL seconds) ─────────────────
OFFER_TTL = 300  # 5 minutes
_pending: dict[str, dict] = {}


def _prune_expired() -> None:
    now = time.time()
    expired = [k for k, v in _pending.items() if now - v["created_at"] > OFFER_TTL]
    for k in expired:
        del _pending[k]


def _items_embed(
    trade_id: str,
    from_member: discord.Member | None,
    from_name: str,
    offered_items: list,
    counter_items: list,
    *,
    status: str | None = None,
) -> discord.Embed:
    embed = discord.Embed(
        title="🔁 Trade Angebot",
        color=0xF39C12,
    )

    def _fmt(items: list) -> str:
        if not items:
            return "*(nichts)*"
        return "\n".join(
            f"{RARITIES[it['rarity']]['emoji']} **{item_full_name(it)}** — "
            f"Float: `{it['float']:.6f}` · Pattern: `{it['pattern']}` · "
            f"Wert: **{it['sell_price']:,}** {CURRENCY_EMOJI}"
            for it in items
        )

    embed.add_field(name=f"📤 {from_name} bietet:", value=_fmt(offered_items), inline=False)
    if counter_items:
        embed.add_field(name="📥 Gegenangebot:", value=_fmt(counter_items), inline=False)

    if status:
        embed.add_field(name="Status", value=status, inline=False)

    embed.set_footer(text=f"Trade-ID: {trade_id}  ·  Läuft in 5 Min ab")
    if from_member:
        tag_embed(embed, from_member)
    return embed


class TradeResponseView(discord.ui.View):
    """Shown to the trade TARGET so they can accept, add counter-items, or decline."""

    def __init__(
        self,
        trade_id: str,
        from_id: int,
        to_id: int,
        from_member: discord.Member,
        to_member: discord.Member,
    ):
        super().__init__(timeout=OFFER_TTL)
        self.trade_id   = trade_id
        self.from_id    = from_id
        self.to_id      = to_id
        self.from_member = from_member
        self.to_member   = to_member
        self._done       = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.to_id:
            await interaction.response.send_message(
                "Dieses Angebot ist nicht für dich!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Annehmen", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        trade = _pending.get(self.trade_id)
        if trade is None:
            await interaction.response.edit_message(
                content="❌ Trade abgelaufen oder nicht mehr vorhanden.", embed=None, view=None
            )
            return
        self._done = True
        self._disable_all()

        ok = trade_items(
            self.from_id, self.to_id,
            trade["from_item_ids"],
            trade["to_item_ids"],
        )
        del _pending[self.trade_id]

        if not ok:
            await interaction.response.edit_message(
                content="❌ Trade fehlgeschlagen — Items nicht mehr vorhanden.", embed=None, view=self
            )
            return

        embed = _items_embed(
            self.trade_id,
            self.from_member,
            self.from_member.display_name,
            trade["from_items"],
            trade["to_items"],
            status=f"✅ Trade angenommen von **{self.to_member.display_name}**!",
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Gegenangebot", style=discord.ButtonStyle.primary, emoji="🔄")
    async def counter(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open a modal so the receiver can specify counter-item numbers."""
        if self._done:
            return
        trade = _pending.get(self.trade_id)
        if trade is None:
            await interaction.response.send_message("Trade nicht mehr vorhanden.", ephemeral=True)
            return
        await interaction.response.send_modal(
            CounterModal(
                trade_id=self.trade_id,
                from_id=self.from_id,
                to_id=self.to_id,
                from_member=self.from_member,
                to_member=self.to_member,
                parent_view=self,
            )
        )

    @discord.ui.button(label="Ablehnen", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        self._disable_all()
        _pending.pop(self.trade_id, None)
        embed = _items_embed(
            self.trade_id,
            self.from_member,
            self.from_member.display_name,
            _pending.get(self.trade_id, {}).get("from_items", []),
            [],
            status=f"❌ Trade abgelehnt von **{self.to_member.display_name}**.",
        )
        # Can't use from_items after deletion; just show status
        await interaction.response.edit_message(
            content=f"❌ **{self.to_member.display_name}** hat das Trade-Angebot abgelehnt.",
            embed=None,
            view=self,
        )

    def _disable_all(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        _pending.pop(self.trade_id, None)
        self._disable_all()


class CounterModal(discord.ui.Modal, title="Gegenangebot — Item-Nummern"):
    item_input = discord.ui.TextInput(
        label="Deine Item-Nummern (komma- oder leerzeichengetrennt)",
        placeholder="z. B.: 1 4 7  oder  2,5",
        required=True,
        max_length=100,
    )

    def __init__(
        self,
        trade_id: str,
        from_id: int,
        to_id: int,
        from_member: discord.Member,
        to_member: discord.Member,
        parent_view: TradeResponseView,
    ):
        super().__init__()
        self.trade_id    = trade_id
        self.from_id     = from_id
        self.to_id       = to_id
        self.from_member = from_member
        self.to_member   = to_member
        self.parent_view = parent_view

    async def on_submit(self, interaction: discord.Interaction):
        trade = _pending.get(self.trade_id)
        if trade is None:
            await interaction.response.send_message("Trade nicht mehr vorhanden.", ephemeral=True)
            return

        raw    = self.item_input.value.replace(",", " ").split()
        inv    = get_inventory(self.to_id)
        chosen = []
        errors = []

        for tok in raw:
            if tok.isdigit():
                idx = int(tok) - 1
                if 0 <= idx < len(inv):
                    item = inv[idx]
                    if item not in chosen:
                        chosen.append(item)
                else:
                    errors.append(tok)
            else:
                errors.append(tok)

        if errors:
            await interaction.response.send_message(
                f"Ungültige Nummern: `{', '.join(errors)}`. Du hast **{len(inv)}** Items.",
                ephemeral=True,
            )
            return

        if not chosen:
            await interaction.response.send_message(
                "Keine Items ausgewählt.", ephemeral=True
            )
            return

        # Update the pending trade with counter-items
        trade["to_item_ids"] = [it["id"] for it in chosen]
        trade["to_items"]    = chosen
        self.parent_view._done = True
        self.parent_view._disable_all()

        embed = _items_embed(
            self.trade_id,
            self.from_member,
            self.from_member.display_name,
            trade["from_items"],
            chosen,
            status=(
                f"🔄 **{self.to_member.display_name}** hat ein Gegenangebot geschickt!\n"
                f"**{self.from_member.mention}**, akzeptiere mit `f.accepttrade {self.trade_id}`"
                f" oder lehne ab mit `f.declinetrade {self.trade_id}`."
            ),
        )
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class AcceptCounterView(discord.ui.View):
    """Shown to the original SENDER after a counter-offer was made."""

    def __init__(
        self,
        trade_id: str,
        from_id: int,
        to_id: int,
        from_member: discord.Member,
        to_member: discord.Member,
    ):
        super().__init__(timeout=OFFER_TTL)
        self.trade_id    = trade_id
        self.from_id     = from_id
        self.to_id       = to_id
        self.from_member = from_member
        self.to_member   = to_member
        self._done       = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.from_id:
            await interaction.response.send_message("Nicht dein Trade!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Gegenangebot annehmen", style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        trade = _pending.get(self.trade_id)
        if trade is None:
            await interaction.response.edit_message(content="Trade abgelaufen.", embed=None, view=None)
            return
        self._done = True
        self._disable_all()

        ok = trade_items(
            self.from_id, self.to_id,
            trade["from_item_ids"],
            trade["to_item_ids"],
        )
        del _pending[self.trade_id]

        if not ok:
            await interaction.response.edit_message(
                content="❌ Trade fehlgeschlagen — Items nicht mehr vorhanden.", embed=None, view=self
            )
            return

        embed = _items_embed(
            self.trade_id,
            self.from_member,
            self.from_member.display_name,
            trade["from_items"],
            trade["to_items"],
            status=f"✅ Trade abgeschlossen zwischen **{self.from_member.display_name}** und **{self.to_member.display_name}**!",
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Ablehnen", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        self._disable_all()
        _pending.pop(self.trade_id, None)
        await interaction.response.edit_message(
            content=f"❌ Gegenangebot abgelehnt.", embed=None, view=self
        )

    def _disable_all(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        _pending.pop(self.trade_id, None)
        self._disable_all()


@command("tradeoffer", description="Sende ein Trade-Angebot: f.tradeoffer @user <item_nummern...>",
         usage="f.tradeoffer @user <#> [#...]", category="Casino")
async def tradeoffer_command(message: Message, args: list[str]):
    _prune_expired()

    if not message.mentions:
        await message.reply(
            "**Verwendung:** `f.tradeoffer @user <item_nummern>`\n"
            "Beispiel: `f.tradeoffer @Finn 1 3` — bietet Items #1 und #3 an.\n"
            "Sieh dein Inventar mit `f.inventory`."
        )
        return

    target = message.mentions[0]

    if target.id == message.author.id:
        await message.reply("Du kannst dir selbst kein Angebot schicken.")
        return
    if target.bot:
        await message.reply("Du kannst keinem Bot ein Angebot schicken.")
        return

    # Parse item numbers (everything after the mention)
    num_tokens = [a for a in args if a.isdigit()]
    if not num_tokens:
        await message.reply(
            "Gib mindestens eine Inventarnummer an.\n"
            "Beispiel: `f.tradeoffer @user 1 3`\n"
            "Sieh dein Inventar mit `f.inventory`."
        )
        return

    inv    = get_inventory(message.author.id)
    chosen = []
    errors = []

    for tok in num_tokens:
        idx = int(tok) - 1
        if 0 <= idx < len(inv):
            item = inv[idx]
            if item not in chosen:
                chosen.append(item)
        else:
            errors.append(tok)

    if errors:
        await message.reply(
            f"Ungültige Nummern: `{', '.join(errors)}`. Du hast **{len(inv)}** Items."
        )
        return

    trade_id = str(uuid.uuid4())[:8]
    _pending[trade_id] = {
        "created_at":    time.time(),
        "from_id":       message.author.id,
        "to_id":         target.id,
        "from_item_ids": [it["id"] for it in chosen],
        "from_items":    chosen,
        "to_item_ids":   [],
        "to_items":      [],
    }

    embed = _items_embed(
        trade_id,
        message.author,
        message.author.display_name,
        chosen,
        [],
    )
    embed.description = f"{target.mention}, du hast ein Trade-Angebot von **{message.author.display_name}** erhalten!"

    view = TradeResponseView(
        trade_id,
        message.author.id,
        target.id,
        message.author,
        target,
    )
    await message.reply(content=target.mention, embed=embed, view=view)


@command("accepttrade", description="Gegenangebot akzeptieren",
         usage="f.accepttrade <trade_id>", category="Casino")
async def accepttrade_command(message: Message, args: list[str]):
    _prune_expired()
    if not args:
        await message.reply("Verwendung: `f.accepttrade <trade_id>`")
        return

    trade_id = args[0]
    trade    = _pending.get(trade_id)

    if trade is None:
        await message.reply("Trade nicht gefunden oder bereits abgelaufen.")
        return

    if message.author.id != trade["from_id"]:
        await message.reply("Das ist nicht dein Trade.")
        return

    if not trade["to_item_ids"]:
        await message.reply("Der andere Spieler hat noch kein Gegenangebot gemacht.")
        return

    try:
        from_member = await message.guild.fetch_member(trade["from_id"])
        to_member   = await message.guild.fetch_member(trade["to_id"])
    except Exception:
        from_member = message.author
        to_member   = message.author

    embed = _items_embed(
        trade_id,
        from_member,
        from_member.display_name,
        trade["from_items"],
        trade["to_items"],
        status="Bestätige das Gegenangebot:",
    )
    view = AcceptCounterView(
        trade_id,
        trade["from_id"],
        trade["to_id"],
        from_member,
        to_member,
    )
    await message.reply(embed=embed, view=view)


@command("declinetrade", description="Gegenangebot ablehnen",
         usage="f.declinetrade <trade_id>", category="Casino")
async def declinetrade_command(message: Message, args: list[str]):
    if not args:
        await message.reply("Verwendung: `f.declinetrade <trade_id>`")
        return

    trade_id = args[0]
    trade    = _pending.get(trade_id)

    if trade is None:
        await message.reply("Trade nicht gefunden oder bereits abgelaufen.")
        return
    if message.author.id != trade["from_id"]:
        await message.reply("Das ist nicht dein Trade.")
        return

    del _pending[trade_id]
    await message.reply(f"Trade `{trade_id}` abgelehnt und entfernt.")
