import random

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, tag_embed,
    CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET, resolve_bet,
)
from bot.strings import Mines as S

_TOTAL   = 20   # 4 rows × 5 cols
_MINES   = 3
_EDGE    = 1.05  # 5% player edge to encourage long-term play


def _multiplier(safe_found: int) -> float:
    """Probability-based multiplier with house edge applied."""
    if safe_found == 0:
        return 1.0
    prob = 1.0
    for i in range(safe_found):
        prob *= ((_TOTAL - _MINES) - i) / (_TOTAL - i)
    return round(_EDGE / prob, 2)


def _build_embed(
    member: discord.Member,
    bet: int,
    safe_found: int,
    *,
    hit_mine: bool = False,
    cashed_out: bool = False,
) -> discord.Embed:
    mult        = _multiplier(safe_found)
    payout      = int(bet * mult)
    next_mult   = _multiplier(safe_found + 1)
    next_payout = int(bet * next_mult)

    if hit_mine:
        title = S.BOOM_TITLE
        if safe_found > 0:
            desc = S.BOOM_DESC_HIT.format(bet=bet, CURRENCY_EMOJI=CURRENCY_EMOJI, payout=payout, mult=mult)
        else:
            desc = S.BOOM_DESC_FIRST.format(bet=bet, CURRENCY_EMOJI=CURRENCY_EMOJI)
        color = 0xE74C3C

    elif cashed_out:
        title = S.CASHOUT_TITLE
        desc  = S.CASHOUT_DESC.format(payout=payout, CURRENCY_EMOJI=CURRENCY_EMOJI, mult=mult)
        color = 0x2ECC71

    else:
        title = S.PLAYING_TITLE
        if safe_found == 0:
            desc = S.PLAYING_DESC_START.format(mines=_MINES, next_payout=next_payout, CURRENCY_EMOJI=CURRENCY_EMOJI, next_mult=next_mult)
        else:
            s_suffix = "s" if safe_found != 1 else ""
            desc = S.PLAYING_DESC_PROGRESS.format(
                safe_found=safe_found, s=s_suffix,
                payout=payout, CURRENCY_EMOJI=CURRENCY_EMOJI, mult=mult,
                next_payout=next_payout, next_mult=next_mult,
            )
        color = 0x3498DB

    embed = discord.Embed(title=title, description=desc, color=color)
    embed.add_field(name=S.FIELD_BET,        value=f"{bet:,} {CURRENCY_EMOJI}", inline=True)
    embed.add_field(name=S.FIELD_MULTIPLIER, value=f"{mult}x",                  inline=True)
    embed.add_field(name=S.FIELD_MINES,      value=S.MINES_VALUE.format(mines=_MINES), inline=True)

    return tag_embed(embed, member)


class MinesView(discord.ui.View):
    def __init__(self, user_id: int, member: discord.Member, bet: int):
        super().__init__(timeout=180)
        self.user_id        = user_id
        self.member         = member
        self.bet            = bet
        self.mine_positions = set(random.sample(range(_TOTAL), _MINES))
        self.safe_found     = 0
        self.revealed       = set()
        self.game_over      = False
        self._message: discord.Message | None = None

        # 4 rows of 5 tile buttons
        self._tiles: list[discord.ui.Button] = []
        for i in range(_TOTAL):
            btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                emoji="🟦",
                row=i // 5,
                custom_id=f"mines_tile_{i}_{user_id}",
            )
            btn.callback = self._make_tile_cb(i)
            self.add_item(btn)
            self._tiles.append(btn)

        # Row 4 — single action button (Give Up → Cash Out after first safe tile)
        self._action_btn = discord.ui.Button(
            label=S.GIVE_UP_LABEL,
            style=discord.ButtonStyle.danger,
            emoji="🏳️",
            row=4,
            custom_id=f"mines_action_{user_id}",
        )
        self._action_btn.callback = self._do_action
        self.add_item(self._action_btn)

    # ------------------------------------------------------------------ helpers

    def _lock_board(self):
        for btn in self._tiles:
            btn.disabled = True
        self._action_btn.disabled = True

    def _reveal_mines(self, exploded: int | None = None):
        """Red reveal — used when the player hits a mine."""
        for m in self.mine_positions:
            if m == exploded:
                continue
            self._tiles[m].emoji    = discord.PartialEmoji(name="💣")
            self._tiles[m].style    = discord.ButtonStyle.danger
            self._tiles[m].disabled = True

    def _reveal_mines_safe(self):
        """Grey reveal — used on cash out so the player can see where mines were."""
        for m in self.mine_positions:
            if m in self.revealed:
                continue
            self._tiles[m].emoji    = discord.PartialEmoji(name="💣")
            self._tiles[m].style    = discord.ButtonStyle.secondary
            self._tiles[m].disabled = True

    def _promote_action_btn(self):
        """Switch the action button from Give Up to Cash Out after first safe tile."""
        self._action_btn.label = S.CASH_OUT_LABEL
        self._action_btn.style = discord.ButtonStyle.success
        self._action_btn.emoji = discord.PartialEmoji(name="💰")

    # --------------------------------------------------------------- callbacks

    def _make_tile_cb(self, idx: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(S.NOT_YOUR_GAME, ephemeral=True)
                return
            if self.game_over or idx in self.revealed:
                await interaction.response.defer()
                return

            self.revealed.add(idx)
            btn = self._tiles[idx]

            if idx in self.mine_positions:
                self.game_over = True
                btn.style      = discord.ButtonStyle.danger
                btn.emoji      = discord.PartialEmoji(name="💥")
                btn.disabled   = True
                self._reveal_mines(exploded=idx)
                self._lock_board()
                embed = _build_embed(self.member, self.bet, self.safe_found, hit_mine=True)
                self.stop()
            else:
                self.safe_found += 1
                btn.style        = discord.ButtonStyle.success
                btn.emoji        = discord.PartialEmoji(name="✅")
                btn.disabled     = True

                if self.safe_found == 1:
                    self._promote_action_btn()

                # All safe tiles found — automatic win
                if self.safe_found == _TOTAL - _MINES:
                    self.game_over = True
                    payout = int(self.bet * _multiplier(self.safe_found))
                    add_balance(self.user_id, payout)
                    self._reveal_mines_safe()
                    self._lock_board()
                    embed = _build_embed(self.member, self.bet, self.safe_found, cashed_out=True)
                    self.stop()
                else:
                    embed = _build_embed(self.member, self.bet, self.safe_found)

            await interaction.response.edit_message(embed=embed, view=self)

        return callback

    async def _do_action(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(S.NOT_YOUR_GAME, ephemeral=True)
            return
        if self.game_over:
            await interaction.response.defer()
            return

        self.game_over = True
        self._lock_board()

        if self.safe_found == 0:
            # Give Up — no tiles flipped, full refund
            add_balance(self.user_id, self.bet)
            embed = tag_embed(discord.Embed(
                title=S.CANCELLED_TITLE,
                description=S.CANCELLED_DESC.format(bet=self.bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
                color=0x95A5A6,
            ), self.member)
        else:
            # Cash Out
            payout = int(self.bet * _multiplier(self.safe_found))
            add_balance(self.user_id, payout)
            self._reveal_mines_safe()
            embed = _build_embed(self.member, self.bet, self.safe_found, cashed_out=True)

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        self.game_over = True
        if self.safe_found > 0:
            payout = int(self.bet * _multiplier(self.safe_found))
            add_balance(self.user_id, payout)
            self._reveal_mines_safe()
        else:
            add_balance(self.user_id, self.bet)
        self._lock_board()
        if self._message:
            try:
                embed = _build_embed(
                    self.member, self.bet, self.safe_found,
                    cashed_out=self.safe_found > 0,
                )
                await self._message.edit(embed=embed, view=self)
            except Exception:
                pass


@command("mines", description=S.DESCRIPTION, usage="f.mines <bet>", category="Casino")
async def mines_command(message: Message, args: list[str]):
    if not args:
        await message.reply("Usage: `f.mines <bet>`  (e.g. `f.mines 500`, `f.mines all`, `f.mines 50%`)")
        return

    bet = resolve_bet(args[0], message.author.id)
    if bet is None:
        await message.reply("Usage: `f.mines <bet>`  (e.g. `f.mines 500`, `f.mines all`, `f.mines 50%`)")
        return
    if bet < MIN_BET:
        await message.reply(S.MIN_BET_MSG.format(MIN_BET=MIN_BET, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    view  = MinesView(message.author.id, message.author, bet)
    embed = _build_embed(message.author, bet, 0)
    msg   = await message.reply(embed=embed, view=view)
    view._message = msg
