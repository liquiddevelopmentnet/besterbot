import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    remove_balance, add_balance, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, MIN_BET,
    resolve_bet,
)
from bot.commands.casino.cards import Deck, hand_str, evaluate_poker, POKER_PAYOUTS
from bot.strings import Poker as S


class CardSelect(discord.ui.Select):
    def __init__(self, hand):
        options = [
            discord.SelectOption(
                label=str(card),
                value=str(i),
                description=f"Card {i + 1}",
            )
            for i, card in enumerate(hand)
        ]
        super().__init__(
            placeholder=S.DISCARD_PLACEHOLDER,
            min_values=0,
            max_values=5,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.to_discard = [int(v) for v in self.values]
        await interaction.response.defer()


class PokerView(discord.ui.View):
    def __init__(self, player_id: int, member: discord.Member, bet: int, deck: Deck, hand: list):
        super().__init__(timeout=60)
        self.player_id = player_id
        self.member = member
        self.bet = bet
        self.deck = deck
        self.hand = hand
        self.to_discard: list[int] = []
        self.message: discord.Message | None = None
        self.add_item(CardSelect(hand))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.player_id:
            await interaction.response.send_message(S.NOT_YOUR_GAME, ephemeral=True)
            return False
        return True

    def _payout_table(self) -> str:
        lines = []
        for key in sorted(POKER_PAYOUTS.keys(), reverse=True):
            mult, name = POKER_PAYOUTS[key]
            if mult > 0:
                lines.append(f"`{name:<18}` **{mult}x**")
        return "\n".join(lines)

    @discord.ui.button(label=S.DRAW_LABEL, style=discord.ButtonStyle.primary, emoji="\U0001f0cf", row=2)
    async def draw_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Replace discarded cards
        for i in self.to_discard:
            self.hand[i] = self.deck.deal(1)[0]

        rank_key, hand_name = evaluate_poker(self.hand)
        multiplier, _ = POKER_PAYOUTS[rank_key]

        if multiplier > 0:
            winnings = self.bet * multiplier
            add_balance(self.player_id, winnings)
            profit = winnings - self.bet
            if profit > 0:
                result = S.WIN_RESULT.format(hand_name=hand_name, profit=profit, CURRENCY_EMOJI=CURRENCY_EMOJI)
            else:
                result = S.PUSH_RESULT.format(hand_name=hand_name)
            color = 0x2ECC71 if profit > 0 else 0xF39C12
        else:
            result = S.LOSE_RESULT.format(hand_name=hand_name, bet=self.bet, CURRENCY_EMOJI=CURRENCY_EMOJI)
            color = 0xE74C3C

        embed = tag_embed(discord.Embed(
            title=S.TITLE.format(bet=self.bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
            color=color,
        ), self.member)
        discarded = len(self.to_discard)
        embed.add_field(
            name=S.FINAL_HAND.format(discarded=discarded, s="s" if discarded != 1 else ""),
            value=hand_str(self.hand),
            inline=False,
        )
        embed.add_field(name=S.RESULT, value=result, inline=False)

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        # Auto-draw keeping all cards
        rank_key, hand_name = evaluate_poker(self.hand)
        multiplier, _ = POKER_PAYOUTS[rank_key]

        if multiplier > 0:
            add_balance(self.player_id, self.bet * multiplier)

        for item in self.children:
            item.disabled = True
        embed = tag_embed(discord.Embed(
            title=S.TITLE.format(bet=self.bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
            description=S.TIMEOUT_DESC,
            color=0x95A5A6,
        ), self.member)
        embed.add_field(name=S.TIMEOUT_HAND, value=hand_str(self.hand), inline=False)
        embed.add_field(name=S.TIMEOUT_HAND_NAME, value=hand_name, inline=False)
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.NotFound:
                pass


@command("poker", description=S.DESCRIPTION, usage="f.poker <bet>", category="Casino")
async def poker_command(message: Message, args: list[str]):
    if not args:
        await message.reply("Usage: `f.poker <bet>`  (e.g. `f.poker 500`, `f.poker all`, `f.poker 50%`)")
        return

    bet = resolve_bet(args[0], message.author.id)
    if bet is None:
        await message.reply("Usage: `f.poker <bet>`  (e.g. `f.poker 500`, `f.poker all`, `f.poker 50%`)")
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
    hand = deck.deal(5)

    view = PokerView(message.author.id, message.author, bet, deck, hand)

    embed = tag_embed(discord.Embed(
        title=S.TITLE.format(bet=bet, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x3498DB,
    ), message.author)
    embed.add_field(name=S.YOUR_HAND, value=hand_str(hand), inline=False)
    embed.add_field(
        name=S.HOW_TO_PLAY_NAME,
        value=S.HOW_TO_PLAY_VALUE,
        inline=False,
    )
    embed.add_field(name=S.PAYOUTS, value=view._payout_table(), inline=False)

    msg = await message.channel.send(embed=embed, view=view)
    view.message = msg
