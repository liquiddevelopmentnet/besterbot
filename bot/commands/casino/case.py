"""CS2-style case opening — f.case (costs 800 Maka)."""
import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, get_balance, add_item, tag_embed,
    CURRENCY_NAME, CURRENCY_EMOJI,
)
from bot.commands.casino.items import create_item, item_full_name, RARITIES
from bot.strings import Case as S

CASE_COST = 800
CASE_NAME  = "BesterBot Capsule"

# user_id → item dict of the currently undecided case
_pending_cases: dict[int, dict] = {}


def _build_embed(
    item: dict,
    member: discord.Member,
    *,
    kept: bool | None = None,
    sold_for: int | None = None,
    auto_sold_prev: dict | None = None,
) -> discord.Embed:
    info     = RARITIES[item["rarity"]]
    name     = item_full_name(item)
    headline = S.OPEN_LINES[item["rarity"]]

    desc = f"{info['emoji']} **{info['label']}** — {headline}"
    if auto_sold_prev:
        prev_name = item_full_name(auto_sold_prev)
        desc = (
            S.PREV_SOLD_PREFIX.format(prev_name=prev_name, price=auto_sold_prev['sell_price'], CURRENCY_EMOJI=CURRENCY_EMOJI)
            + desc
        )

    embed = discord.Embed(title=f"🎁 {CASE_NAME}", description=desc, color=info["color"])
    embed.add_field(name=S.FIELD_ITEM,       value=f"**{name}**",                                inline=False)
    embed.add_field(name=S.FIELD_FLOAT,      value=f"`{item['float']:.6f}`",                      inline=True)
    embed.add_field(name=S.FIELD_PATTERN,    value=f"`{item['pattern']}`",                        inline=True)
    embed.add_field(name=S.FIELD_STATTRAK,   value="✅" if item["stattrak"] else "❌",             inline=True)
    embed.add_field(name=S.FIELD_SELLWERT,   value=f"**{item['sell_price']:,}** {CURRENCY_EMOJI}", inline=True)

    if item.get("image_url"):
        embed.set_image(url=item["image_url"])

    if kept is True:
        embed.add_field(name=S.FIELD_STATUS, value=S.STATUS_KEPT, inline=False)
    elif sold_for is not None:
        embed.add_field(name=S.FIELD_STATUS, value=S.STATUS_SOLD.format(price=sold_for, CURRENCY_EMOJI=CURRENCY_EMOJI), inline=False)

    return tag_embed(embed, member)


class CaseResultView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member, item: dict):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.member  = member
        self.item    = item
        self._done   = False
        self._sync_buttons()

    def _sync_buttons(self) -> None:
        bal = get_balance(self.user_id)
        can_open_plain  = bal >= CASE_COST
        can_open_sell   = (bal + self.item["sell_price"]) >= CASE_COST
        self.keep_open.disabled = not can_open_plain
        self.sell_open.disabled = not can_open_sell

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(S.NOT_YOUR_CASE, ephemeral=True)
            return False
        return True

    def _disable_all(self) -> None:
        for child in self.children:
            child.disabled = True

    # ── helpers shared between the "& nochmal" buttons ───────────────────────
    def _resolve_keep(self) -> None:
        self._done = True
        add_item(self.user_id, self.item)
        _pending_cases.pop(self.user_id, None)

    def _resolve_sell(self) -> int:
        self._done = True
        price = self.item["sell_price"]
        add_balance(self.user_id, price)
        _pending_cases.pop(self.user_id, None)
        return price

    def _open_next(self) -> dict:
        """Charge for and generate the next case item. Raises ValueError if broke."""
        remove_balance(self.user_id, CASE_COST)
        new_item = create_item()
        _pending_cases[self.user_id] = new_item
        return new_item

    def _reset_for(self, new_item: dict) -> None:
        self.item  = new_item
        self._done = False
        for child in self.children:
            child.disabled = False
        self._sync_buttons()

    # ── 1. Behalten ───────────────────────────────────────────────────────────
    @discord.ui.button(label=S.KEEP_LABEL, style=discord.ButtonStyle.success, emoji="🎒", row=0)
    async def keep(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        self._resolve_keep()
        self._disable_all()
        await interaction.response.edit_message(
            embed=_build_embed(self.item, self.member, kept=True), view=self
        )

    # ── 2. Verkaufen ──────────────────────────────────────────────────────────
    @discord.ui.button(label=S.SELL_LABEL, style=discord.ButtonStyle.danger, emoji="💰", row=0)
    async def sell_btn(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        price = self._resolve_sell()
        self._disable_all()
        await interaction.response.edit_message(
            embed=_build_embed(self.item, self.member, sold_for=price), view=self
        )

    # ── 3. Behalten & Noch mal ────────────────────────────────────────────────
    @discord.ui.button(label=S.KEEP_OPEN_LABEL, style=discord.ButtonStyle.success,
                       emoji="🎁", row=1)
    async def keep_open(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        kept_item = self.item
        self._resolve_keep()
        try:
            new_item = self._open_next()
        except ValueError:
            await interaction.response.send_message(
                S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME, cost=CASE_COST, CURRENCY_EMOJI=CURRENCY_EMOJI),
                ephemeral=True,
            )
            return
        self._reset_for(new_item)
        await interaction.response.edit_message(
            embed=_build_embed(new_item, self.member), view=self
        )

    # ── 4. Verkaufen & Noch mal ───────────────────────────────────────────────
    @discord.ui.button(label=S.SELL_OPEN_LABEL, style=discord.ButtonStyle.danger,
                       emoji="🎁", row=1)
    async def sell_open(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self._done:
            return
        sold_item = self.item
        self._resolve_sell()
        try:
            new_item = self._open_next()
        except ValueError:
            await interaction.response.send_message(
                S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME, cost=CASE_COST, CURRENCY_EMOJI=CURRENCY_EMOJI),
                ephemeral=True,
            )
            return
        self._reset_for(new_item)
        await interaction.response.edit_message(
            embed=_build_embed(new_item, self.member, auto_sold_prev=sold_item), view=self
        )

    # ── timeout ───────────────────────────────────────────────────────────────
    async def on_timeout(self) -> None:
        if not self._done and _pending_cases.get(self.user_id, {}).get("id") == self.item["id"]:
            add_balance(self.user_id, self.item["sell_price"])
            _pending_cases.pop(self.user_id, None)
        self._disable_all()


@command("case", description=S.DESCRIPTION,
         usage="f.case", category="Casino")
async def case_command(message: Message, args: list[str]):
    try:
        remove_balance(message.author.id, CASE_COST)
    except ValueError:
        await message.reply(
            S.BROKE_MSG.format(cost=CASE_COST, CURRENCY_EMOJI=CURRENCY_EMOJI, CURRENCY_NAME=CURRENCY_NAME)
        )
        return

    # Auto-sell any pending unanswered case
    auto_sold = None
    prev = _pending_cases.pop(message.author.id, None)
    if prev:
        add_balance(message.author.id, prev["sell_price"])
        auto_sold = prev

    item = create_item()
    _pending_cases[message.author.id] = item
    embed = _build_embed(item, message.author, auto_sold_prev=auto_sold)
    view  = CaseResultView(message.author.id, message.author, item)
    await message.reply(embed=embed, view=view)
