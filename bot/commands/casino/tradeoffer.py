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
from bot.strings import Tradeoffer as S

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
        title=S.EMBED_TITLE,
        color=0xF39C12,
    )

    def _fmt(items: list) -> str:
        if not items:
            return S.NOTHING
        return "\n".join(
            f"{RARITIES[it['rarity']]['emoji']} **{item_full_name(it)}** — "
            f"Float: `{it['float']:.6f}` · Pattern: `{it['pattern']}` · "
            f"Wert: **{it['sell_price']:,}** {CURRENCY_EMOJI}"
            for it in items
        )

    embed.add_field(name=S.FROM_OFFERS.format(name=from_name), value=_fmt(offered_items), inline=False)
    if counter_items:
        embed.add_field(name=S.COUNTER_OFFER, value=_fmt(counter_items), inline=False)

    if status:
        embed.add_field(name=S.STATUS, value=status, inline=False)

    embed.set_footer(text=S.FOOTER.format(trade_id=trade_id))
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
                S.NOT_FOR_YOU, ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label=S.ACCEPT_LABEL, style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        trade = _pending.get(self.trade_id)
        if trade is None:
            await interaction.response.edit_message(
                content=S.EXPIRED, embed=None, view=None
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
                content=S.TRADE_FAILED, embed=None, view=self
            )
            return

        embed = _items_embed(
            self.trade_id,
            self.from_member,
            self.from_member.display_name,
            trade["from_items"],
            trade["to_items"],
            status=S.ACCEPTED_STATUS.format(name=self.to_member.display_name),
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=S.COUNTER_LABEL, style=discord.ButtonStyle.primary, emoji="🔄")
    async def counter(self, interaction: discord.Interaction, _: discord.ui.Button):
        """Open a modal so the receiver can specify counter-item numbers."""
        if self._done:
            return
        trade = _pending.get(self.trade_id)
        if trade is None:
            await interaction.response.send_message(S.TRADE_GONE, ephemeral=True)
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

    @discord.ui.button(label=S.DECLINE_LABEL, style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        self._disable_all()
        _pending.pop(self.trade_id, None)
        # Can't use from_items after deletion; just show status
        await interaction.response.edit_message(
            content=S.DECLINED_CONTENT.format(name=self.to_member.display_name),
            embed=None,
            view=self,
        )

    def _disable_all(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        _pending.pop(self.trade_id, None)
        self._disable_all()


class CounterModal(discord.ui.Modal, title=S.COUNTER_MODAL_TITLE):
    item_input = discord.ui.TextInput(
        label=S.COUNTER_INPUT_LABEL,
        placeholder=S.COUNTER_PLACEHOLDER,
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
            await interaction.response.send_message(S.TRADE_GONE, ephemeral=True)
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
                S.COUNTER_INVALID_NUMS.format(nums=', '.join(errors), count=len(inv)),
                ephemeral=True,
            )
            return

        if not chosen:
            await interaction.response.send_message(
                S.COUNTER_NONE_SELECTED, ephemeral=True
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
            status=S.COUNTER_SENT_STATUS.format(
                to_name=self.to_member.display_name,
                from_mention=self.from_member.mention,
                trade_id=self.trade_id,
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
            await interaction.response.send_message(S.NOT_YOUR_TRADE_COUNTER, ephemeral=True)
            return False
        return True

    @discord.ui.button(label=S.ACCEPT_COUNTER_LABEL, style=discord.ButtonStyle.success, emoji="✅")
    async def accept(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        trade = _pending.get(self.trade_id)
        if trade is None:
            await interaction.response.edit_message(content=S.TRADE_EXPIRED_COUNTER, embed=None, view=None)
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
                content=S.COUNTER_FAILED, embed=None, view=self
            )
            return

        embed = _items_embed(
            self.trade_id,
            self.from_member,
            self.from_member.display_name,
            trade["from_items"],
            trade["to_items"],
            status=S.TRADE_DONE_STATUS.format(from_name=self.from_member.display_name, to_name=self.to_member.display_name),
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=S.DECLINE_LABEL, style=discord.ButtonStyle.danger, emoji="❌")
    async def decline(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._done = True
        self._disable_all()
        _pending.pop(self.trade_id, None)
        await interaction.response.edit_message(
            content=S.COUNTER_DECLINED_CONTENT, embed=None, view=self
        )

    def _disable_all(self) -> None:
        for child in self.children:
            child.disabled = True

    async def on_timeout(self) -> None:
        _pending.pop(self.trade_id, None)
        self._disable_all()


@command("tradeoffer", description=S.DESCRIPTION_TRADEOFFER,
         usage="f.tradeoffer @user <#> [#...]", category="Casino")
async def tradeoffer_command(message: Message, args: list[str]):
    _prune_expired()

    if not message.mentions:
        await message.reply(S.USAGE)
        return

    target = message.mentions[0]

    if target.id == message.author.id:
        await message.reply(S.CANT_TRADE_SELF)
        return
    if target.bot:
        await message.reply(S.CANT_TRADE_BOT)
        return

    # Parse item numbers (everything after the mention)
    num_tokens = [a for a in args if a.isdigit()]
    if not num_tokens:
        await message.reply(S.NO_ITEMS_GIVEN)
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
        await message.reply(S.INVALID_NUMBERS.format(nums=', '.join(errors), count=len(inv)))
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
    embed.description = S.OFFER_DESC.format(mention=target.mention, name=message.author.display_name)

    view = TradeResponseView(
        trade_id,
        message.author.id,
        target.id,
        message.author,
        target,
    )
    await message.reply(content=target.mention, embed=embed, view=view)


@command("accepttrade", description=S.DESCRIPTION_ACCEPTTRADE,
         usage="f.accepttrade <trade_id>", category="Casino")
async def accepttrade_command(message: Message, args: list[str]):
    _prune_expired()
    if not args:
        await message.reply(S.ACCEPT_USAGE)
        return

    trade_id = args[0]
    trade    = _pending.get(trade_id)

    if trade is None:
        await message.reply(S.NOT_FOUND)
        return

    if message.author.id != trade["from_id"]:
        await message.reply(S.NOT_YOUR_TRADE)
        return

    if not trade["to_item_ids"]:
        await message.reply(S.NO_COUNTER_YET)
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
        status=S.CONFIRM_COUNTER_STATUS,
    )
    view = AcceptCounterView(
        trade_id,
        trade["from_id"],
        trade["to_id"],
        from_member,
        to_member,
    )
    await message.reply(embed=embed, view=view)


@command("declinetrade", description=S.DESCRIPTION_DECLINETRADE,
         usage="f.declinetrade <trade_id>", category="Casino")
async def declinetrade_command(message: Message, args: list[str]):
    if not args:
        await message.reply(S.DECLINE_USAGE)
        return

    trade_id = args[0]
    trade    = _pending.get(trade_id)

    if trade is None:
        await message.reply(S.NOT_FOUND)
        return
    if message.author.id != trade["from_id"]:
        await message.reply(S.NOT_YOUR_TRADE)
        return

    del _pending[trade_id]
    await message.reply(S.DECLINED_AND_REMOVED.format(trade_id=trade_id))
