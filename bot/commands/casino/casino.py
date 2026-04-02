import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import tag_embed, CURRENCY_EMOJI, CURRENCY_NAME

# ── Game catalogue ────────────────────────────────────────────────────────────
# Each entry: id, label, emoji, button row, overview value, detail embed data

_GAMES = [
    {
        "id": "earn",
        "label": "Earn",
        "emoji": "💰",
        "row": 0,
        "ov_name": f"💰 Earning  •  `f.earn`",
        "ov_value": "Beg, fish, work, crime, scam, daily\nCooldown-based — no bet required",
        "detail_title": f"💰 Ways to Earn {CURRENCY_NAME}",
        "detail_desc": (
            "All passive earning commands bundled into one interactive menu.\n"
            "Each has its own cooldown and some carry a loss risk."
        ),
        "detail_fields": [
            ("Commands", "`f.beg` · `f.fish` · `f.work` · `f.crime` · `f.scam` · `f.daily`", False),
            ("Earn Range", f"50 – 10,000 {CURRENCY_EMOJI}", True),
            ("Risk", "Crime (30%) and Scam (40%) can lose you coins", True),
            ("Access", "`f.earn` — opens button menu", True),
        ],
    },
    {
        "id": "mines",
        "label": "Mines",
        "emoji": "💣",
        "row": 0,
        "ov_name": "💣 Mines  •  `f.mines <bet>`",
        "ov_value": f"Flip tiles, avoid 3 mines, cash out anytime\nMultiplier grows with each safe tile",
        "detail_title": "💣 Mines",
        "detail_desc": (
            "A 4×5 grid hides 3 mines. Flip tiles to reveal safe spots — "
            "the multiplier climbs with every one you find. Cash out before you hit a mine."
        ),
        "detail_fields": [
            ("Usage", "`f.mines <bet>`", True),
            ("Grid", "4×5 — 20 tiles, 3 mines", True),
            ("Multiplier", f"Grows each safe tile — starts at 1.15x", True),
            ("Risk", "Hit a mine = lose your bet", True),
            ("Edge", "5% player-favourable RTP", True),
        ],
    },
    {
        "id": "double",
        "label": "Double",
        "emoji": "🎲",
        "row": 0,
        "ov_name": "🎲 Double or Nothing  •  `f.double <bet>`",
        "ov_value": f"53% chance to double your bet\n\"Play Again\" button after each round",
        "detail_title": "🎲 Double or Nothing",
        "detail_desc": "Simple flip — win and you double your bet, lose and it's gone.",
        "detail_fields": [
            ("Usage", "`f.double <bet>`", True),
            ("Win Chance", "53%", True),
            ("Payout", "2× bet on win", True),
            ("RTP", "~106%", True),
        ],
    },
    {
        "id": "blackjack",
        "label": "Blackjack",
        "emoji": "🃏",
        "row": 0,
        "ov_name": "🃏 Blackjack  •  `f.bj <bet>`",
        "ov_value": "Classic 21 — Hit or Stand buttons\nNatural blackjack pays 3×",
        "detail_title": "🃏 Blackjack",
        "detail_desc": (
            "Classic card game. Get closer to 21 than the dealer without busting. "
            "Natural blackjack (dealt 21) pays a bonus."
        ),
        "detail_fields": [
            ("Usage", "`f.blackjack <bet>` or `f.bj <bet>`", True),
            ("Natural BJ", "3× bet", True),
            ("Regular Win", "2.1× bet", True),
            ("RTP", "~106%", True),
            ("Controls", "Hit / Stand buttons", True),
        ],
    },
    {
        "id": "roulette",
        "label": "Roulette",
        "emoji": "🎡",
        "row": 0,
        "ov_name": "🎡 Roulette  •  `f.roulette <bet> <choice>`",
        "ov_value": "Bet on red/black/green or a number 0–36\nGreen & numbers pay 40×",
        "detail_title": "🎡 Roulette",
        "detail_desc": "Spin the wheel — bet on a colour or pick an exact number.",
        "detail_fields": [
            ("Usage", "`f.roulette <bet> <red|black|green|0-36>`", False),
            ("Red / Black", "2.2× — ~107% RTP", True),
            ("Green (0)", "40× — ~108% RTP", True),
            ("Number (0–36)", "40× — ~108% RTP", True),
        ],
    },
    {
        "id": "crash",
        "label": "Crash",
        "emoji": "🚀",
        "row": 1,
        "ov_name": "🚀 Crash  •  `f.crash <bet>`",
        "ov_value": "Pick a target multiplier before the rocket crashes\nHigher target = lower chance to hit",
        "detail_title": "🚀 Crash",
        "detail_desc": (
            "Choose a target multiplier (1.5× – 25×). "
            "A crash point is drawn — if it's ≥ your target you win, otherwise you lose."
        ),
        "detail_fields": [
            ("Usage", "`f.crash <bet>`", True),
            ("Targets", "1.5× · 2× · 3× · 5× · 10× · 25×", False),
            ("RTP", "~105%", True),
            ("Max Crash", "100×", True),
        ],
    },
    {
        "id": "lottery",
        "label": "Lottery",
        "emoji": "🎰",
        "row": 1,
        "ov_name": "🎰 Lottery  •  `f.lottery <bet>`",
        "ov_value": "Scratch-off ticket — match 3 symbols for 10×\nMatch 2 for 3×",
        "detail_title": "🎰 Lottery Scratch-Off",
        "detail_desc": "Buy a scratch-off ticket and reveal 3 symbols. Match them to win.",
        "detail_fields": [
            ("Usage", "`f.lottery <bet>`", True),
            ("3 Matches", "10× bet", True),
            ("2 Matches", "3× bet", True),
            ("No Match", "Lose bet", True),
            ("Replay", "\"Another Ticket\" button after each spin", False),
        ],
    },
    {
        "id": "poker",
        "label": "Poker",
        "emoji": "♠️",
        "row": 1,
        "ov_name": "♠️ Video Poker  •  `f.poker <bet>`",
        "ov_value": "5-card draw — hold cards, redraw the rest\nPayout scales with hand rank",
        "detail_title": "♠️ Video Poker",
        "detail_desc": (
            "You're dealt 5 cards. Choose which to keep, then draw replacements. "
            "Your final hand rank determines the payout."
        ),
        "detail_fields": [
            ("Usage", "`f.poker <bet>`", True),
            ("Controls", "Dropdown to select cards to discard", False),
            ("Best Hand", "Royal Flush — highest multiplier", True),
            ("Min Hand", "Pair — smallest payout", True),
        ],
    },
    {
        "id": "bet",
        "label": "Challenge",
        "emoji": "🤝",
        "row": 1,
        "ov_name": "🤝 1v1 Bet  •  `f.bet @user <amount>`",
        "ov_value": "Challenge another player to a 50:50 coin flip\nLoser pays the winner",
        "detail_title": "🤝 1v1 Bet",
        "detail_desc": "Challenge any server member to a direct coin-flip bet. They must accept within 60 seconds.",
        "detail_fields": [
            ("Usage", "`f.bet @user <amount>`", True),
            ("Win Chance", "50 / 50", True),
            ("Payout", "Win = +bet, Lose = −bet", True),
            ("Timeout", "60 s to accept", True),
        ],
    },
]

_GAME_BY_ID = {g["id"]: g for g in _GAMES}

# ── Embed builders ────────────────────────────────────────────────────────────

def _build_overview_embed(member: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        title=f"🎰 {CURRENCY_NAME} Casino",
        description=(
            f"All ways to win (and lose) {CURRENCY_EMOJI}.\n"
            "Click a button below for details on any game."
        ),
        color=0xF1C40F,
    )
    for game in _GAMES:
        embed.add_field(name=game["ov_name"], value=game["ov_value"], inline=False)
    embed.set_footer(text="f.earn for earning commands  •  f.leaderboard for top balances")
    return tag_embed(embed, member)


def _build_detail_embed(game_id: str, member: discord.Member) -> discord.Embed:
    g = _GAME_BY_ID[game_id]
    embed = discord.Embed(
        title=g["detail_title"],
        description=g["detail_desc"],
        color=0xF1C40F,
    )
    for name, value, inline in g["detail_fields"]:
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_footer(text="← Back to overview")
    return tag_embed(embed, member)

# ── View ──────────────────────────────────────────────────────────────────────

class CasinoView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=300)
        self.member      = member
        self._detail_mode = False
        self._build_buttons()

    def _build_buttons(self, *, show_back: bool = False):
        self.clear_items()

        for game in _GAMES:
            btn = discord.ui.Button(
                label=game["label"],
                emoji=game["emoji"],
                style=discord.ButtonStyle.primary,
                row=game["row"],
            )
            btn.callback = self._make_game_cb(game["id"])
            self.add_item(btn)

        if show_back:
            back = discord.ui.Button(
                label="Back",
                emoji="◀️",
                style=discord.ButtonStyle.secondary,
                row=2,
            )
            back.callback = self._do_back
            self.add_item(back)

    def _make_game_cb(self, game_id: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.member.id:
                await interaction.response.send_message(
                    "Open your own casino menu with `f.casino`.", ephemeral=True
                )
                return
            self._build_buttons(show_back=True)
            embed = _build_detail_embed(game_id, self.member)
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _do_back(self, interaction: discord.Interaction):
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                "Open your own casino menu with `f.casino`.", ephemeral=True
            )
            return
        self._build_buttons(show_back=False)
        embed = _build_overview_embed(self.member)
        await interaction.response.edit_message(embed=embed, view=self)

# ── Command ───────────────────────────────────────────────────────────────────

@command("casino", description=f"Overview of all {CURRENCY_NAME} casino games", usage="f.casino", category="Casino")
async def casino_command(message: Message, args: list[str]):
    view  = CasinoView(message.author)
    embed = _build_overview_embed(message.author)
    await message.channel.send(embed=embed, view=view)
