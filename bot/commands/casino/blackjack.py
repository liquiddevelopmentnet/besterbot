import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, log_earning, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)
from bot.commands.casino.cards import Deck, bj_total, hand_str
from bot.strings import Blackjack as S


class BlackjackView(discord.ui.View):
    def __init__(self, player_id: int, member: discord.Member, bet: int,
                 deck: Deck, player_hand: list, dealer_hand: list):
        super().__init__(timeout=60)
        self.player_id = player_id
        self.member = member
        self.bet = bet
        self.deck = deck
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.player_id:
            await interaction.response.send_message(S.NOT_YOUR_GAME, ephemeral=True)
            return False
        return True

    def build_embed(self, reveal_dealer=False, result_text=None, color=0x3498DB):
        p_val = bj_total(self.player_hand)

        if reveal_dealer:
            d_line = f"{hand_str(self.dealer_hand)} (Value: **{bj_total(self.dealer_hand)}**)"
        else:
            d_line = f"`{self.dealer_hand[0]}` `??`"

        embed = tag_embed(discord.Embed(
            title=S.TITLE.format(bet=self.bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=color,
        ), self.member)
        embed.add_field(
            name=S.YOUR_HAND,
            value=f"{hand_str(self.player_hand)} (Value: **{p_val}**)",
            inline=False,
        )
        embed.add_field(name=S.DEALER, value=d_line, inline=False)
        if result_text:
            embed.add_field(name=S.RESULT, value=result_text, inline=False)
        return embed

    async def _finish(self, interaction: discord.Interaction,
                      result_text: str, color: int):
        for item in self.children:
            item.disabled = True
        embed = self.build_embed(reveal_dealer=True, result_text=result_text, color=color)
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def _dealer_play(self, interaction: discord.Interaction):
        while bj_total(self.dealer_hand) < 17:
            self.dealer_hand.extend(self.deck.deal(1))

        p_val = bj_total(self.player_hand)
        d_val = bj_total(self.dealer_hand)

        if d_val > 21 or p_val > d_val:
            winnings = int(self.bet * 2.1)  # 2.1x → ~106% RTP on regular wins
            add_balance(self.player_id, winnings)
            log_earning(self.player_id, winnings)
            await self._finish(interaction,
                               S.WIN_RESULT.format(winnings=winnings, CURRENCY_EMOJI=CURRENCY_EMOJI),
                               0x2ECC71)
        elif p_val == d_val:
            add_balance(self.player_id, self.bet)
            await self._finish(interaction,
                               S.PUSH_RESULT,
                               0xF39C12)
        else:
            await self._finish(interaction,
                               S.DEALER_WIN.format(bet=self.bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
                               0xE74C3C)

    @discord.ui.button(label=S.HIT_LABEL, style=discord.ButtonStyle.primary, emoji="\U0001f0cf")
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player_hand.extend(self.deck.deal(1))
        p_val = bj_total(self.player_hand)

        if p_val > 21:
            await self._finish(interaction,
                               S.BUST_RESULT.format(bet=self.bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
                               0xE74C3C)
        elif p_val == 21:
            await self._dealer_play(interaction)
        else:
            embed = self.build_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=S.STAND_LABEL, style=discord.ButtonStyle.secondary, emoji="\u270b")
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._dealer_play(interaction)

    async def on_timeout(self):
        add_balance(self.player_id, self.bet)
        for item in self.children:
            item.disabled = True
        embed = self.build_embed(
            reveal_dealer=True,
            result_text=S.TIMEOUT_RESULT,
            color=0x95A5A6,
        )
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.NotFound:
                pass


@command("blackjack", description=S.DESCRIPTION, usage="f.blackjack <bet>", category="Casino")
@command("bj", description=S.DESCRIPTION, usage="f.bj <bet>", category="Casino")
async def blackjack_command(message: Message, args: list[str]):
    if not args:
        await message.reply("Usage: `f.bj <bet>`  (e.g. `f.bj 500`, `f.bj all`, `f.bj 50%`)")
        return

    bet = resolve_bet(args[0], message.author.id)
    if bet is None:
        await message.reply("Usage: `f.bj <bet>`  (e.g. `f.bj 500`, `f.bj all`, `f.bj 50%`)")
        return
    if bet < MIN_BET:
        await message.reply(S.MIN_BET_MSG.format(MIN_BET=MIN_BET, CURRENCY_EMOJI=CURRENCY_EMOJI))
        return

    try:
        remove_balance(message.author.id, bet)
    except ValueError:
        await message.reply(S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    deck = Deck()
    player_hand = deck.deal(2)
    dealer_hand = deck.deal(2)

    # Natural blackjack
    if bj_total(player_hand) == 21:
        winnings = int(bet * 3)  # 3x natural → extra reward for lucky deal
        add_balance(message.author.id, winnings)
        log_earning(message.author.id, winnings)
        embed = tag_embed(discord.Embed(
            title=S.TITLE.format(bet=bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=0xFFD700,
        ), message.author)
        embed.add_field(name=S.YOUR_HAND, value=f"{hand_str(player_hand)} (Value: **21**)", inline=False)
        embed.add_field(name=S.DEALER, value=f"{hand_str(dealer_hand)} (Value: **{bj_total(dealer_hand)}**)", inline=False)
        embed.add_field(name=S.RESULT, value=S.BLACKJACK_RESULT.format(winnings=winnings, CURRENCY_EMOJI=CURRENCY_EMOJI), inline=False)
        await message.channel.send(embed=embed)
        return

    view = BlackjackView(message.author.id, message.author, bet, deck, player_hand, dealer_hand)
    embed = view.build_embed()
    msg = await message.channel.send(embed=embed, view=view)
    view.message = msg
