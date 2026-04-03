"""
strings.py — All user-facing text strings for BesterBot.

Edit this file to change any displayed text without touching logic files.
Each class corresponds to one source module.
"""


# ── Casino / Admin ─────────────────────────────────────────────────────────────

class Admin:
    USAGE = (
        "**Admin-Befehle:**\n"
        "`f.admin setbal @user <amount>` — set exact balance\n"
        "`f.admin addbal @user <amount>` — add to balance\n"
        "`f.admin subbal @user <amount>` — subtract from balance (can go negative)\n"
        "`f.admin removeuser @user` — wipe user from the wallet\n"
        "`f.admin resetall [amount]` — reset everyone (default: starting balance)\n"
        "`f.admin viewbal @user` — check any user's balance\n"
    )
    NO_PERMISSION = "🚫 You don't have permission to use this command."
    UNKNOWN_SUBCOMMAND = "Unbekannter Subcommand `{sub}`.\n\n{usage}"

    # setbal
    SETBAL_USAGE = "Verwendung: `f.admin setbal @user <amount>`"
    SETBAL_TITLE = "✅ Balance Set"
    SETBAL_DESC  = "**{name}** → **{new:,}** {CURRENCY_EMOJI}"

    # addbal
    ADDBAL_USAGE = "Verwendung: `f.admin addbal @user <amount>`"
    ADDBAL_TITLE = "✅ Balance Added"
    ADDBAL_DESC  = "**{name}** +**{amount:,}** → **{new:,}** {CURRENCY_EMOJI}"

    # subbal
    SUBBAL_USAGE = "Verwendung: `f.admin subbal @user <amount>`"
    SUBBAL_TITLE = "✅ Balance Subtracted"
    SUBBAL_DESC  = "**{name}** -**{amount:,}** → **{new:,}** {CURRENCY_EMOJI}"

    # removeuser
    REMOVEUSER_USAGE    = "Verwendung: `f.admin removeuser @user`"
    REMOVEUSER_TITLE    = "🗑️ User Removed"
    REMOVEUSER_DESC     = "**{name}** wurde aus dem Wallet radiert wie ein peinlicher Leak."
    NOTFOUND_TITLE      = "⚠️ User Not Found"
    NOTFOUND_DESC       = "**{name}** hat keinen Wallet-Eintrag. Finanzielle Nichtexistenz."

    # resetall
    RESETALL_TITLE = "♻️ All Balances Reset"
    RESETALL_DESC  = "Jedes Wallet wurde auf **{amount:,}** {CURRENCY_EMOJI} zurechtgestutzt."

    # viewbal
    VIEWBAL_USAGE = "Verwendung: `f.admin viewbal @user`"
    VIEWBAL_TITLE = "👁️ {name}'s Balance"
    VIEWBAL_DESC  = "**{bal:,}** {CURRENCY_EMOJI}"

    DESCRIPTION = "Admin-Kontrolle f?r alles, was nach Geld riecht"


# ── Casino / Balance ───────────────────────────────────────────────────────────

class Balance:
    NOT_YOUR_WALLET = "Das ist nicht dein Wallet. Finger weg, Finanzgremlin."
    WALLET_TITLE    = "{CURRENCY_EMOJI} Wallet"
    WALLET_DESC     = "**{bal:,}** {CURRENCY_NAME}"

    EARN_MENU_LABEL    = "Geldmen?"
    LEADERBOARD_LABEL  = "Bestenliste"

    DESCRIPTION = "Pr?f deinen Kontostand und deine Restw?rde"


# ── Casino / Beg ──────────────────────────────────────────────────────────────

class Beg:
    RESPONSES = [
        "Ein Fremder hatte kurz Mitleid, dann wieder Selbsthass.",
        "Jemand warf Kleingeld aus dem Auto. Vermutlich f?r Ruhe, nicht aus Liebe.",
        "Du hast einen zerknitterten Schein vom Boden gerettet. Er hatte es auch nicht leicht.",
        "Ein Tourist hielt dich f?r Stra?enkunst. Technisch gesehen war's Mitleid mit Kulturbonus.",
        "Deine Leidensgeschichte war so gut, dass selbst du fast dran geglaubt h?ttest.",
        "Eine Oma gab dir ihr Wechselgeld und direkt noch stilles Urteil dazu.",
    ]

    COOLDOWN    = "🙏 People are tired of you. Wait **{m}m {s}s** before begging again."
    TITLE       = "🙏 Begging Complete"
    DESCRIPTION = "{response}\n+**{earned:,}** {CURRENCY_EMOJI}"
    FOOTER      = "Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 4min"

    COMMAND_DESCRIPTION = "Bettel um Kleingeld und ein bisschen Menschenverachtung"


# ── Casino / Bet ──────────────────────────────────────────────────────────────

class Bet:
    NOT_FOR_YOU         = "Diese Wette ist nicht f?r dich. Zuschauen ist kostenlos."
    NOT_ENOUGH_CURRENCY = "Du hast nicht genug {CURRENCY_NAME}. Gro?e Fresse, kleines Wallet."
    CANT_BET_SELF       = "Gegen dich selbst wetten ist selbst hier zu erb?rmlich."
    CANT_BET_BOT        = "Gegen einen Bot wetten ist wie Schach gegen den Toaster verlieren."
    INVALID_AMOUNT      = "Der Betrag muss positiv sein, z. B. `500`, `all` oder `50%`."
    MIN_BET_MSG         = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    TARGET_BROKE        = "**{name}** hat nicht genug {CURRENCY_NAME}. Armut ist Teamarbeit."
    SENDER_BROKE        = "Du hast nicht genug {CURRENCY_NAME}. Das Drama scheitert am Budget."

    RESULT_TITLE = "\U0001f3b2 50:50 Bet \u2014 Result"
    COIN_FLIP_NAME  = "\U0001fa99 M?nzwurf"
    COIN_FLIP_VALUE = (
        "**{winner}** gewinnt **{pot:,}** {CURRENCY_EMOJI}!\n"
        "**{loser}** verliert **{bet:,}** {CURRENCY_EMOJI}."
    )

    DECLINED_TITLE = "\U0001f3b2 50:50-Wette \u2014 Abgelehnt"
    DECLINED_DESC  = "**{name}** hat gekniffen. Einsatz zur?ck, Ehre weg."

    EXPIRED_TITLE = "\U0001f3b2 50:50-Wette \u2014 Abgelaufen"
    EXPIRED_DESC  = "**{name}** hat nicht reagiert. Einsatz zur?ck, Peinlichkeit bleibt."

    CHALLENGE_TITLE = "\U0001f3b2 50:50 Bet Challenge!"
    CHALLENGE_DESC  = (
        "**{challenger}** fordert **{target}** "
        "f?r **{bet:,}** {CURRENCY_EMOJI}!\n\n"
        "{mention}, nimmst du an oder stirbt dein Mut heute auf Raten?"
    )

    ACCEPT_LABEL  = "Annehmen"
    DECLINE_LABEL = "Ablehnen"

    DESCRIPTION = "50:50-Wette gegen einen anderen Spieler"


# ── Casino / Blackjack ────────────────────────────────────────────────────────

class Blackjack:
    NOT_YOUR_GAME = "Das ist nicht dein Spiel!"
    MIN_BET_MSG   = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    NOT_ENOUGH    = "Du hast nicht genug {CURRENCY_NAME}. Das Haus lacht bereits."

    TITLE         = "\U0001f0cf Blackjack \u2014 Bet: {bet:,} {CURRENCY_EMOJI}"
    YOUR_HAND     = "Deine Hand"
    DEALER        = "Dealer"
    RESULT        = "Ergebnis"

    WIN_RESULT     = "\U0001f389 **You win!** +{winnings:,} {CURRENCY_EMOJI}"
    PUSH_RESULT    = "\U0001f91d **Push!** Bet returned."
    DEALER_WIN     = "\U0001f480 **Dealer wins!** -{bet:,} {CURRENCY_EMOJI}"
    BUST_RESULT    = "\U0001f4a5 **Bust!** -{bet:,} {CURRENCY_EMOJI}"
    TIMEOUT_RESULT = "\u23f0 **Timed out!** Bet returned."
    BLACKJACK_RESULT = "\U0001f3b0 **BLACKJACK!** +{winnings:,} {CURRENCY_EMOJI}"

    HIT_LABEL   = "Karte"
    STAND_LABEL = "Stehen"

    DESCRIPTION = "Spiel Blackjack gegen einen Dealer ohne Gewissen"


# ── Casino / Case ─────────────────────────────────────────────────────────────

class Case:
    OPEN_LINES = {
        "lightblue": "Du hast eine Case geöffnet.",
        "blue":       "Nicht schlecht!",
        "purple":     "Nices Drop! 🔥",
        "pink":       "COVERT DROP! 🔥🔥",
        "gold":       "★ GOLD!!! — JACKPOT! 🌟",
    }

    PREV_SOLD_PREFIX = "💰 **{prev_name}** für **{price:,}** {CURRENCY_EMOJI} verkauft.\n\n"

    FIELD_ITEM       = "Item"
    FIELD_FLOAT      = "Float"
    FIELD_PATTERN    = "Pattern"
    FIELD_STATTRAK   = "StatTrak™"
    FIELD_SELLWERT   = "Verkaufswert"
    FIELD_STATUS     = "Status"

    STATUS_KEPT      = "🎒 Ins Inventar hinzugefügt"
    STATUS_SOLD      = "💰 Verkauft für **{price:,}** {CURRENCY_EMOJI}"

    NOT_YOUR_CASE    = "Das ist nicht deine Case!"
    NOT_ENOUGH       = "Nicht genug {CURRENCY_NAME}! (brauchst {cost:,} {CURRENCY_EMOJI})"
    BROKE_MSG        = (
        "Du brauchst mindestens **{cost:,}** {CURRENCY_EMOJI} um eine Case zu öffnen!\n"
        "Aktuell hast du nicht genug {CURRENCY_NAME}."
    )

    KEEP_LABEL       = "Behalten"
    SELL_LABEL       = "Verkaufen"
    KEEP_OPEN_LABEL  = "Behalten & Noch mal"
    SELL_OPEN_LABEL  = "Verkaufen & Noch mal"

    DESCRIPTION = "Öffne eine CS2-Case für 800 Maka"


# ── Casino / Casino ───────────────────────────────────────────────────────────

class Casino:
    OVERVIEW_TITLE       = "🎰 {CURRENCY_NAME} Casino"
    OVERVIEW_DESC        = "All ways to win (and lose) {CURRENCY_EMOJI}.\nClick a button below for details on any game."
    OVERVIEW_FOOTER      = "f.earn for earning commands  •  f.leaderboard for top balances"
    DETAIL_FOOTER        = "← Back to overview"
    NOT_YOUR_MENU        = "Open your own casino menu with `f.casino`."
    BACK_LABEL           = "Back"

    GAMES = [
        {
            "id": "earn",
            "label": "Earn",
            "emoji": "💰",
            "row": 0,
            "ov_name": "💰 Earning  •  `f.earn`",
            "ov_value": "Beg, fish, work, crime, scam, daily\nCooldown-based — no bet required",
            "detail_title": "💰 Ways to Earn {CURRENCY_NAME}",
            "detail_desc": (
                "All passive earning commands bundled into one interactive menu.\n"
                "Each has its own cooldown and some carry a loss risk."
            ),
            "detail_fields": [
                ("Commands", "`f.beg` · `f.fish` · `f.work` · `f.crime` · `f.scam` · `f.daily`", False),
                ("Earn Range", "50 – 10,000 {CURRENCY_EMOJI}", True),
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
            "ov_value": "Flip tiles, avoid 3 mines, cash out anytime\nMultiplier grows with each safe tile",
            "detail_title": "💣 Mines",
            "detail_desc": (
                "A 4×5 grid hides 3 mines. Flip tiles to reveal safe spots — "
                "the multiplier climbs with every one you find. Cash out before you hit a mine."
            ),
            "detail_fields": [
                ("Usage", "`f.mines <bet>`", True),
                ("Grid", "4×5 — 20 tiles, 3 mines", True),
                ("Multiplier", "Grows each safe tile — starts at 1.15x", True),
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
            "ov_value": "53% chance to double your bet\n\"Play Again\" button after each round",
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
            "detail_desc": "Kauf ein Rubbellos, deck 3 Symbole auf und hoff, dass die Statistik kurz schl?ft.",
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

    DESCRIPTION = "Overview of all {CURRENCY_NAME} casino games"


# ── Casino / Crash ────────────────────────────────────────────────────────────

class Crash:
    NOT_YOUR_GAME   = "Das ist nicht dein Spiel!"
    MIN_BET_MSG     = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    NOT_ENOUGH      = "Du hast nicht genug {CURRENCY_NAME}."

    PENDING_TITLE   = "📈 Crash"
    PENDING_DESC    = (
        "Pick your target multiplier below.\n"
        "If the rocket crashes *before* your target — you lose.\n\n"
        "{lines}"
    )
    PENDING_BET     = "Bet"
    PENDING_FOOTER  = "Player edge ~5% — odds are in your favour"

    SAFE_TITLE      = "📈 Crash — 🚀 Safe!"
    SAFE_DESC       = (
        "Rocket crashed at **{crash}x** — your target was **{target}x**.\n"
        "You won **{payout:,}** {CURRENCY_EMOJI} (**+{profit:,}**)."
    )
    CRASHED_TITLE   = "📈 Crash — 💥 Crashed!"
    CRASHED_DESC    = (
        "Rocket crashed at **{crash}x** — before your target of **{target}x**.\n"
        "You lost **{bet:,}** {CURRENCY_EMOJI}."
    )
    FIELD_BET       = "Bet"
    FIELD_TARGET    = "Target"
    FIELD_CRASHED   = "Crashed At"

    DESCRIPTION = "Pick a multiplier target — cash out before the rocket crashes"


# ── Casino / Crime ────────────────────────────────────────────────────────────

class Crime:
    SUCCESS_CRIMES = [
        "robbed a vending machine",
        "pickpocketed a tourist",
        "sold knockoff Gucci bags",
        "hacked a parking meter",
        "ran a shell game on tourists",
        "fenced stolen electronics",
        "forged a concert ticket run",
    ]

    FAIL_CRIMES = [
        "got caught shoplifting and fined",
        "tripped the alarm and had to pay damages",
        "got mugged while trying to mug someone else",
        "the police showed up mid-heist",
        "your accomplice snitched on you",
    ]

    COOLDOWN     = "🚔 Still laying low. Try again in **{time_str}**."
    SUCCESS_TITLE = "🦹 Crime Pays"
    SUCCESS_DESC  = "You {crime} and got away with **{earned:,}** {CURRENCY_EMOJI}."
    FAIL_TITLE    = "🚨 Busted!"
    FAIL_DESC     = "You {crime}. Fined **{lost:,}** {CURRENCY_EMOJI}."
    DEBT_NAME     = "💸 In Debt"
    DEBT_VALUE    = "**{amount:,}** {CURRENCY_EMOJI} in the hole."
    FOOTER        = "Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 20min"

    DESCRIPTION = "Commit a risky crime for big rewards"


# ── Casino / Daily ────────────────────────────────────────────────────────────

class Daily:
    ALREADY_CLAIMED_TITLE = "{CURRENCY_EMOJI} Daily schon abgegriffen"
    ALREADY_CLAIMED_DESC  = "Komm in **{h}h {m}m {s}s** wieder. Der Staat zahlt nur einmal pro Tag."
    REWARD_TITLE          = "{CURRENCY_EMOJI} Daily kassiert!"
    REWARD_DESC           = "+**{amount:,}** {CURRENCY_NAME}\nNeuer Kontostand: **{new_bal:,}** {CURRENCY_EMOJI}"
    REWARD_FOOTER         = "Reset um Mitternacht CET."

    DESCRIPTION = "Hol dir deine t?glichen 30.000 Maka-Flaschen Staatsw?rme"


# ── Casino / Double ───────────────────────────────────────────────────────────

class Double:
    NOT_YOUR_GAME  = "Das ist nicht dein Spiel!"
    NOT_ENOUGH     = "Nicht genug {CURRENCY_NAME} f?r die n?chste dumme Idee."
    MIN_BET_MSG    = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    BROKE_MSG      = "Du hast nicht genug {CURRENCY_NAME}. Selbst dein R?ckfall ist unterfinanziert."

    TITLE          = "\U0001f4b0 Double or Nothing"
    WIN_DESC       = "**\U0001f389 DOUBLE!** You won **{winnings:,}** {CURRENCY_EMOJI}!"
    LOSE_DESC      = "**\U0001f480 NOTHING!** You lost **{bet:,}** {CURRENCY_EMOJI}."
    FOOTER         = "Einsatz: {bet:,}"

    PLAY_AGAIN_LABEL = "Nochmal"
    QUIT_LABEL       = "Raus"

    DESCRIPTION = "Doppelt oder nichts"


# ── Casino / Earn ─────────────────────────────────────────────────────────────

class Earn:
    BEG_RESPONSES = [
        "Ein Fremder hatte kurz Mitleid, dann wieder Selbsthass.",
        "Jemand warf Kleingeld aus dem Auto. Vermutlich f?r Ruhe, nicht aus Liebe.",
        "Du hast einen zerknitterten Schein vom Boden gerettet. Er hatte es auch nicht leicht.",
        "Ein Tourist hielt dich f?r Stra?enkunst. Technisch gesehen war's Mitleid mit Kulturbonus.",
        "Eine Oma gab dir ihr Wechselgeld und direkt noch stilles Urteil dazu.",
    ]

    JOBS = [
        ("🍔", "flipped burgers at McDonalds"),
        ("🚗", "drove Uber for a few hours"),
        ("💻", "fixed someone's printer"),
        ("🛒", "stacked shelves at Lidl"),
        ("📦", "sorted packages at Amazon"),
        ("🎸", "busked at the Hauptbahnhof"),
        ("🚚", "made DHL deliveries"),
        ("🧹", "cleaned an office building"),
    ]

    CATCHES = [
        (1200, 3000, "🐟", "a small sardine"),
        (1500, 3500, "🐠", "a tropical fish"),
        (2000, 4000, "🦐", "a bag of shrimp"),
        (2500, 4500, "🦀", "a crab"),
        (3500, 5500, "🐡", "a pufferfish"),
        (2000, 4000, "🥾", "an old boot (someone paid for the antique)"),
        (4500, 6500, "🦞", "a massive lobster"),
    ]

    SUCCESS_CRIMES = [
        "robbed a vending machine",
        "pickpocketed a tourist",
        "sold knockoff Gucci bags",
        "ran a shell game on tourists",
    ]
    FAIL_CRIMES = [
        "got caught shoplifting and fined",
        "tripped the alarm and had to pay damages",
        "your accomplice snitched on you",
    ]

    SUCCESS_SCAMS = [
        "ran a fake crypto ICO and cashed out",
        "sold an 'AI startup' to a gullible investor",
        "pulled off a Nigerian prince email scheme",
        "listed a non-existent apartment on Airbnb",
    ]
    FAIL_SCAMS = [
        "the mark was an undercover cop",
        "your phishing site got traced back to you",
        "you accidentally scammed a lawyer",
    ]

    FINANZSPRITZE_LINES = [
        "Der Bundeshaushalt wurde 'kreativ' umgeschichtet. Du profitierst.",
        "Scholz hat noch ein vergessenes Sondervermögen gefunden.",
        "Das Finanzministerium sendet Grüße — und 10.000 Trostpflaster.",
        "Dank Schuldenbremse light™ fließen heute Sondermittel.",
        "Die Ampel ist weg, aber die Überweisung kam trotzdem an.",
        "Ein Ausschuss hat beschlossen, dass du das brauchst. Demokratie!",
        "Staatliche Wirtschaftsförderung: Ziel unklar, Geld da.",
        "Haushaltslücke? Welche Haushaltslücke? Hier, nimm das.",
    ]

    # _COMMANDS display text: (gain_str, risk_str, desc)
    COMMANDS_META = [
        ("f.beg",           "500 – 2,500",        "None",                    "Beg strangers for spare change"),
        ("f.fish",          "1,200 – 6,500",      "None",                    "Cast a line and sell your catch"),
        ("f.work",          "2,000 – 5,000",      "None",                    "Pick up a random shift job"),
        ("f.steal",         "15–30% of target",   "45%: lose 20–40% of own", "Pickpocket another player"),
        ("f.crime",         "8,000 – 13,000",     "30%: lose 1,000–2,000",   "Pull off a street-level crime"),
        ("f.scam",          "10,000 – 16,000",    "40%: lose 1,000–2,500",   "Run a high-risk con"),
        ("f.daily",         "30,000",             "None",                    "Collect your daily government handout"),
        ("f.finanzspritze", "10,000",             "None",                    "Claim your hourly government subsidy"),
    ]

    EMBED_TITLE          = "{CURRENCY_EMOJI} Ways to Earn {CURRENCY_NAME}"
    RESULT_FIELD_VALUE   = "{description}\n**Balance: {new_bal:,}** {CURRENCY_EMOJI}"
    AVAILABLE_STATUS     = "🟢 **Available now**"
    COOLDOWN_STATUS      = "🔴 Ready <t:{ready_at}:R>"
    RISK_YES             = "⚠️ {risk}"
    RISK_NO              = "✅ No risk"
    FIELD_VALUE_TEMPLATE = "💰 **{gain}** {CURRENCY_EMOJI}\n{risk_line}\n{status_line}"
    FOOTER               = "Higher risk = higher reward. Steal requires f.steal @user."

    NOT_YOUR_MENU  = "Das ist nicht dein Geld-Men?. Parasit?res Mitschauen reicht nicht."
    STILL_COOLDOWN = "Still on cooldown — ready <t:{ready_at}:R>."

    BEG_TITLE    = "🙏 Begging Complete"
    BEG_DESC     = "{response}\n+**{earned:,}** {CURRENCY_EMOJI}"
    FISH_TITLE   = "{emoji} Fang gemacht!"
    FISH_DESC    = "Du hast **{name}** rausgezogen und f?r **{earned:,}** {CURRENCY_EMOJI} verscherbelt."
    WORK_TITLE   = "{emoji} Schicht beendet"
    WORK_DESC    = "You {desc} and earned **{earned:,}** {CURRENCY_EMOJI}."
    CRIME_SUCCESS_TITLE = "🦹 Crime Pays"
    CRIME_SUCCESS_DESC  = "You {crime} and got away with **{earned:,}** {CURRENCY_EMOJI}."
    CRIME_FAIL_TITLE    = "🚨 Busted!"
    CRIME_FAIL_DESC     = "You {crime}. Fined **{lost:,}** {CURRENCY_EMOJI}."
    SCAM_SUCCESS_TITLE  = "🤑 Scam Successful"
    SCAM_SUCCESS_DESC   = "You {scam}.\n+**{earned:,}** {CURRENCY_EMOJI}"
    SCAM_FAIL_TITLE     = "🚔 Scam Backfired"
    SCAM_FAIL_DESC      = "You {scam}.\n-**{lost:,}** {CURRENCY_EMOJI}"
    DAILY_TITLE         = "{CURRENCY_EMOJI} Daily kassiert!"
    DAILY_DESC          = "+**{amount:,}** {CURRENCY_NAME}"
    FINANZ_TITLE        = "💶 Finanzspritze erhalten!"
    FINANZ_DESC         = "{line}\n+**{amount:,}** {CURRENCY_EMOJI}"

    DESCRIPTION = "Overview of all earning commands"


# ── Casino / Finanzspritze ────────────────────────────────────────────────────

class Finanzspritze:
    RESPONSES = [
        "Der Bundeshaushalt wurde 'kreativ' umgeschichtet. Du profitierst.",
        "Scholz hat noch ein vergessenes Sondervermögen gefunden.",
        "Das Finanzministerium sendet Grüße — und 10.000 Trostpflaster.",
        "Dank Schuldenbremse light™ fließen heute Sondermittel.",
        "Die Ampel ist weg, aber die Überweisung kam trotzdem an.",
        "Ein Ausschuss hat beschlossen, dass du das brauchst. Demokratie!",
        "Staatliche Wirtschaftsförderung: Ziel unklar, Geld da.",
        "Haushaltslücke? Welche Haushaltslücke? Hier, nimm das.",
        "Bürgergeld 2.0: jetzt auch für Leute, die es nicht brauchen.",
        "Das Wirtschaftsministerium hat versehentlich zu viel überwiesen. Wird nicht zurückgefordert.",
        "Subvention genehmigt — Verwendungszweck: 'irgendwas mit Digitalisierung'.",
        "Der Stabilitätspakt wurde mal wieder 'flexibel ausgelegt'.",
    ]

    COOLDOWN    = "💶 Der Haushalt wird gerade neu verhandelt. Nochmal in **{m}m {s}s**."
    TITLE       = "💶 Finanzspritze erhalten!"
    DESCRIPTION = "{response}\n+**{amount:,}** {CURRENCY_EMOJI}"
    FOOTER      = "Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 1h"

    COMMAND_DESCRIPTION = "Stündliche staatliche Finanzspritze"


# ── Casino / Fish ─────────────────────────────────────────────────────────────

class Fish:
    CATCHES = [
        (1200, 3000, "🐟", "a small sardine"),
        (1500, 3500, "🐠", "a tropical fish"),
        (2000, 4000, "🦐", "a bag of shrimp"),
        (2500, 4500, "🦀", "a crab"),
        (3500, 5500, "🐡", "a pufferfish"),
        (3000, 5000, "🐙", "an octopus"),
        (2000, 4000, "🥾", "an old boot (someone paid for the antique)"),
        (4500, 6500, "🦞", "a massive lobster"),
    ]

    COOLDOWN    = "🎣 The fish need time to come back. Try again in **{time_str}**."
    TITLE       = "{emoji} Fang gemacht!"
    DESCRIPTION = "Du hast **{name}** rausgezogen und f?r **{earned:,}** {CURRENCY_EMOJI} verscherbelt."
    FOOTER      = "Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 10min"

    COMMAND_DESCRIPTION = "Geh angeln und monetarisiere Wasserbewohner"


# ── Casino / Inventory ────────────────────────────────────────────────────────

class Inventory:
    TITLE_OWN    = "🎒 Dein Inventar"
    TITLE_OTHER  = "🎒 {name}'s Inventar"
    EMPTY_OWN    = "Dein Inventar ist leer!\nÖffne eine Case mit `f.case` für **800** Maka."
    EMPTY_OTHER  = "**{name}** hat noch keine Items."
    FIELD_WORTH  = "Inventarwert"
    FIELD_ITEMS  = "Items"
    FOOTER       = "Seite {page}/{total}  ·  {count} Items  ·  Sortierung: {sort}{sell_hint}"
    SELL_HINT    = "  ·  f.sell <#> zum Verkaufen"
    NOT_YOURS    = "Nur der Aufrufer kann blättern!"

    SORT_VALUE_LABEL   = "💰 Wert"
    SORT_RARITY_LABEL  = "⭐ Seltenheit"
    SORT_FLOAT_LABEL   = "🔢 Float"

    DESCRIPTION = "Zeige Inventar (eigenes oder von @user)"


# ── Casino / Leaderboard ──────────────────────────────────────────────────────

class Leaderboard:
    TITLE         = "{CURRENCY_EMOJI} {CURRENCY_NAME}-Bestenliste"
    EMPTY         = "Noch keine Spieler. Reichtum braucht offenbar l?nger als gedacht."
    FOOTER        = "Sortiert nach Gesamtverm?gen (Kontostand + Inventar)"
    REFRESH_LABEL = "Aktualisieren"

    DESCRIPTION = "Die reichsten Gestalten auf dem Server"


# ── Casino / Lottery ──────────────────────────────────────────────────────────

class Lottery:
    NOT_YOUR_GAME = "Das ist nicht dein Spiel!"
    NOT_ENOUGH    = "Nicht genug {CURRENCY_NAME} f?r noch ein Los. Die Sucht muss warten."
    MIN_BET_MSG   = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    BROKE_MSG     = "Du hast nicht genug {CURRENCY_NAME}. Selbst Illusionen kosten."

    TITLE         = "\U0001f3b0 Rubbellos"
    YOUR_TICKET   = "Dein Los"
    RESULT        = "Ergebnis"
    JACKPOT       = "\U0001f389 **JACKPOT!** All three match!"
    TWO_MATCH     = "\U0001f31f **Two match!** Nice pull."
    NO_MATCH      = "\U0001f480 **No match.** Better luck next time."
    WIN_SUFFIX    = "\n+**{winnings:,}** {CURRENCY_EMOJI}"
    FOOTER        = "Bet: {bet:,} | 3 match = 10x \u2022 2 match = 3x"

    ANOTHER_TICKET_LABEL = "Noch ein Los"
    QUIT_LABEL           = "Raus"

    DESCRIPTION = "Rubbellos mit kalkulierter Entt?uschung"


# ── Casino / Mines ────────────────────────────────────────────────────────────

class Mines:
    NOT_YOUR_GAME  = "Das ist nicht dein Spiel!"
    MIN_BET_MSG    = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    NOT_ENOUGH     = "Du hast nicht genug {CURRENCY_NAME}."

    BOOM_TITLE         = "💣 Mines — 💥 BOOM!"
    BOOM_DESC_HIT      = (
        "You hit a mine and lost **{bet:,}** {CURRENCY_EMOJI}.\n"
        "You could've cashed out **{payout:,}** {CURRENCY_EMOJI} (**{mult}x**) — so close."
    )
    BOOM_DESC_FIRST    = "You hit a mine on your first click and lost **{bet:,}** {CURRENCY_EMOJI}."
    CASHOUT_TITLE      = "💣 Mines — 💰 Cashed Out!"
    CASHOUT_DESC       = "Walked away with **{payout:,}** {CURRENCY_EMOJI} (**{mult}x**)."
    PLAYING_TITLE      = "💣 Mines"
    PLAYING_DESC_START = (
        "Flip tiles to uncover safe spots. {mines} mines are hidden.\n"
        "First tile pays **{next_payout:,}** {CURRENCY_EMOJI} (**{next_mult}x**)."
    )
    PLAYING_DESC_PROGRESS = (
        "**{safe_found}** safe tile{s} found!\n"
        "Cash out: **{payout:,}** {CURRENCY_EMOJI} (**{mult}x**) "
        "→ Next tile: **{next_payout:,}** {CURRENCY_EMOJI} (**{next_mult}x**)"
    )
    FIELD_BET        = "Bet"
    FIELD_MULTIPLIER = "Multiplier"
    FIELD_MINES      = "Mines"
    MINES_VALUE      = "💣 × {mines}"

    CANCELLED_TITLE  = "💣 Mines — Cancelled"
    CANCELLED_DESC   = "Game cancelled. **{bet:,}** {CURRENCY_EMOJI} refunded."

    GIVE_UP_LABEL  = "Give Up"
    CASH_OUT_LABEL = "Cash Out"

    DESCRIPTION = "Minesweeper — cash out before you hit a mine"


# ── Casino / Pay ──────────────────────────────────────────────────────────────

class Pay:
    CANT_PAY_SELF   = "You can't pay yourself."
    INVALID_AMOUNT  = "Amount must be a positive number."
    NOT_ENOUGH      = "Du hast nicht genug {CURRENCY_NAME}."

    TITLE       = "{CURRENCY_EMOJI} Payment Sent"
    DESCRIPTION = (
        "**{sender}** paid **{amount:,}** {CURRENCY_NAME} "
        "to **{target}**"
    )
    YOUR_BALANCE   = "Your Balance"
    THEIR_BALANCE  = "{name}'s Balance"

    DESCRIPTION_CMD = "Send currency to another player"


# ── Casino / Poker ────────────────────────────────────────────────────────────

class Poker:
    NOT_YOUR_GAME     = "Das ist nicht dein Spiel!"
    MIN_BET_MSG       = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    NOT_ENOUGH        = "Du hast nicht genug {CURRENCY_NAME}."

    TITLE             = "\U0001f3b0 Video Poker \u2014 Bet: {bet:,} {CURRENCY_EMOJI}"
    YOUR_HAND         = "Deine Hand"
    FINAL_HAND        = "Final Hand (replaced {discarded} card{s})"
    RESULT            = "Ergebnis"
    HOW_TO_PLAY_NAME  = "How to Play"
    HOW_TO_PLAY_VALUE = (
        "Select cards to **discard** from the dropdown, then press **Draw**.\n"
        "Leave empty to keep all cards."
    )
    PAYOUTS           = "Payouts"
    WIN_RESULT        = "\U0001f389 **{hand_name}!** +{profit:,} {CURRENCY_EMOJI} profit"
    PUSH_RESULT       = "\U0001f91d **{hand_name}!** Bet returned."
    LOSE_RESULT       = "\U0001f480 **{hand_name}** \u2014 Lost {bet:,} {CURRENCY_EMOJI}"
    TIMEOUT_DESC      = "\u23f0 Timed out \u2014 auto-drew with current hand."
    TIMEOUT_HAND      = "Final Hand"
    TIMEOUT_HAND_NAME = "Hand"

    DISCARD_PLACEHOLDER = "Select cards to DISCARD (or skip to keep all)"
    DRAW_LABEL          = "Draw"

    DESCRIPTION = "Video Poker (5-card draw)"


# ── Casino / Reset ────────────────────────────────────────────────────────────

class Reset:
    BROKE_TITLE  = "💀 EVERYONE IS BROKE"
    BROKE_DESC   = (
        "Every single gambler has hit zero.\n\n"
        "The house shows mercy.\n"
        "**All balances reset to {amount:,} {CURRENCY_EMOJI}**"
    )
    BROKE_FOOTER = "The casino always wins."
    VOICELINE    = (
        "ACHTUNG! Trump hat alle US Staatsfonds in den Irankrieg investiert. "
        "Jeder Gambler ist pleite. "
        "Benjamin Netanyahu hat beschlossen, das Maka verbot aufzuheben und die 15.000 Maka Flaschen zurückzukaufen, um die Wirtschaft zu stabilisieren. "
        "alle Mossad Agenten haben die Casinos infiltriert und die Konten der Spieler auf 15.000 Maka zurückgesetzt. "
        "isreal gewinnt immer. "
    )


# ── Casino / Roulette ─────────────────────────────────────────────────────────

class Roulette:
    NOT_YOUR_GAME  = "Das ist nicht dein Spiel!"
    MIN_BET_MSG    = "Mindesteinsatz sind {MIN_BET} {CURRENCY_EMOJI}"
    NOT_ENOUGH     = "Du hast nicht genug {CURRENCY_NAME}."
    INVALID_CHOICE = "Bet on `red`, `black`, `green`, or a number `0-36`."
    USAGE          = (
        "Usage: `f.roulette <bet> <red|black|green|0-36>`\n"
        "Red/Black pays **2.2x** \u2022 Green pays **40x** \u2022 Number pays **40x**"
    )
    NOT_ENOUGH_SPIN = "Not enough {CURRENCY_NAME}!"

    TITLE         = "\U0001f3b0 Roulette"
    LANDS_ON      = "The wheel lands on\u2026"
    YOUR_BET      = "Your Bet"
    RESULT        = "Ergebnis"
    WIN_DESC      = "\U0001f389 **You win {winnings:,}** {CURRENCY_EMOJI}!"
    LOSE_DESC     = "\U0001f480 **You lose {bet:,}** {CURRENCY_EMOJI}."

    RED_LABEL    = "Red (2.2x)"
    BLACK_LABEL  = "Black (2.2x)"
    GREEN_LABEL  = "Green (40x)"
    SAME_LABEL   = "Same Again"

    DESCRIPTION = "Play Roulette"


# ── Casino / Scam ─────────────────────────────────────────────────────────────

class Scam:
    SUCCESS_SCAMS = [
        "hat die geheimen Aktien von Netanyahu gerugpulled",
        "sold an 'AI startup' to a gullible investor",
        "pulled off a Nigerian prince email scheme",
        "convinced someone their PC had a virus and charged for 'repairs'",
        "listed a non-existent apartment on Airbnb",
        "sold 'premium' tap water as Swiss mineral water",
    ]

    FAIL_SCAMS = [
        "the mark was an undercover cop",
        "your phishing site got reported and traced back to you",
        "you accidentally scammed a lawyer",
        "Interpol froze your accounts",
        "the victim recognised you from a wanted poster",
    ]

    COOLDOWN       = "🕵️ Keep a low profile for **{time_str}** more."
    SUCCESS_TITLE  = "🤑 Scam Successful"
    SUCCESS_DESC   = "You {scam}.\n+**{earned:,}** {CURRENCY_EMOJI}"
    FAIL_TITLE     = "🚔 Scam Backfired"
    FAIL_DESC      = "You {scam}.\n-**{lost:,}** {CURRENCY_EMOJI}"
    DEBT_NAME      = "💸 In Debt"
    DEBT_VALUE     = "**{amount:,}** {CURRENCY_EMOJI} in the hole."
    FOOTER         = "Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 20min"

    DESCRIPTION = "Run a high-risk scam for massive profit"


# ── Casino / Sell ─────────────────────────────────────────────────────────────

class Sell:
    USAGE = (
        "**Verwendung:**\n"
        "`f.sell 3` — Verkaufe Item #3\n"
        "`f.sell 3,5,2` — Verkaufe Items #3, #5 und #2 auf einmal\n"
        "`f.sell all` — Verkaufe alle Items\n"
        "`f.sell all lightblue` — Verkaufe alle Items einer Seltenheit"
    )
    UNKNOWN_RARITY  = "Unbekannte Seltenheit `{rarity}`. Mögliche Werte: `lightblue`, `blue`, `purple`, `pink`, `gold`"
    NO_ITEMS        = "Du hast keine Items{label} im Inventar."
    NO_ITEMS_LABEL  = " mit Seltenheit **{rarity}**"
    NOT_YOUR_DEAL   = "Nicht dein Deal!"
    INVALID_NUMBERS = "Gib Inventarnummern an, z. B. `f.sell 3` oder `f.sell 3,5,2`."
    EMPTY_INV       = "Dein Inventar ist leer."
    INVALID_IDX     = "Ungültige Nummer(n): `{nums}`. Du hast **{count}** Items (#1–#{count})."
    SELL_FAILED     = "Konnte keine Items verkaufen — versuch es nochmal."

    CONFIRM_TITLE   = "💰 Alles verkaufen?"
    CONFIRM_DESC    = (
        "Du willst **{count} Items** für "
        "**{total:,}** {CURRENCY_EMOJI} verkaufen:\n\n"
        "{lines}"
    )
    SOLD_TITLE_SINGLE  = "💰 Item verkauft"
    SOLD_TITLE_MULTI   = "💰 Items verkauft"
    SOLD_DESC_SINGLE   = "{emoji} **{name}**\nVerkauft für **{price:,}** {CURRENCY_EMOJI}"
    SOLD_FIELD_GESAMT  = "Gesamt"
    SOLD_BULK_TITLE    = "💰 Verkauft"
    SOLD_BULK_DESC     = "**{count}** Items für **{total:,}** {CURRENCY_EMOJI} verkauft."
    CANCEL_CONTENT     = "Verkauf abgebrochen."

    CONFIRM_LABEL  = "Bestätigen"
    CANCEL_LABEL   = "Abbrechen"

    DESCRIPTION = "Verkaufe Items: f.sell 3  |  f.sell 3,5,2  |  f.sell all"


# ── Casino / Skinranking ──────────────────────────────────────────────────────

class Skinranking:
    TITLE_RARITY  = "🏆 Seltenste Items auf dem Server"
    TITLE_VALUE   = "💰 Wertvollste Items auf dem Server"
    FOOTER_RARITY = "Sortiert nach Seltenheit · f.skinranking value für Wert-Ranking"
    FOOTER_VALUE  = "Sortiert nach Wert · f.skinranking rarity für Seltenheits-Ranking"
    EMPTY_DESC    = "Noch keine Items auf dem Server. Öffnet Cases mit `f.case`!"

    STATS_NAME  = "Server Stats"
    STATS_VALUE = (
        "📦 **{total}** Items gesamt\n"
        "💎 **{total_value:,}** {CURRENCY_EMOJI} Gesamtwert\n"
        "⭐ **{gold}** Gold · 🌸 **{pink}** Pink"
    )

    VALUE_BTN_LABEL   = "Nach Wert"
    RARITY_BTN_LABEL  = "Nach Seltenheit"

    DESCRIPTION = "Zeige die wertvollsten/seltensten Items auf dem Server"


# ── Casino / Steal ────────────────────────────────────────────────────────────

class Steal:
    CANT_STEAL_SELF  = "You can't steal from yourself."
    CANT_STEAL_BOT   = "Bots don't carry cash."
    COOLDOWN         = "\U0001f6ab You're still laying low. Try again in **{h}h {m}m {s}s**."
    TARGET_BROKE     = "**{name}** is too broke to steal from (< 100 {CURRENCY_EMOJI})."

    SUCCESS_TITLE    = "\U0001f977 Heist Successful!"
    SUCCESS_DESC     = "You pickpocketed **{stolen:,}** {CURRENCY_EMOJI} from **{name}**!"
    YOUR_BALANCE     = "Your Balance"
    TARGET_BALANCE   = "{name}'s Balance"
    CAUGHT_TITLE     = "\U0001f6a8 Caught Red-Handed!"
    CAUGHT_DESC      = (
        "**{name}** caught you stealing and called the cops.\n"
        "You were fined **{penalty:,}** {CURRENCY_EMOJI}."
    )
    DEBT_NAME        = "\U0001f4b8 In Debt"
    DEBT_VALUE       = "You're **{amount:,}** {CURRENCY_EMOJI} in the hole."
    FOOTER           = "5-minute cooldown before your next attempt."

    DESCRIPTION = "Attempt to steal from another player"


# ── Casino / Tradeoffer ───────────────────────────────────────────────────────

class Tradeoffer:
    USAGE = (
        "**Verwendung:** `f.tradeoffer @user <item_nummern>`\n"
        "Beispiel: `f.tradeoffer @Finn 1 3` — bietet Items #1 und #3 an.\n"
        "Sieh dein Inventar mit `f.inventory`."
    )
    NO_ITEMS_GIVEN = (
        "Gib mindestens eine Inventarnummer an.\n"
        "Beispiel: `f.tradeoffer @user 1 3`\n"
        "Sieh dein Inventar mit `f.inventory`."
    )
    CANT_TRADE_SELF = "Du kannst dir selbst kein Angebot schicken."
    CANT_TRADE_BOT  = "Du kannst keinem Bot ein Angebot schicken."
    INVALID_NUMBERS = "Ungültige Nummern: `{nums}`. Du hast **{count}** Items."

    EMBED_TITLE     = "🔁 Trade Angebot"
    NOTHING         = "*(nichts)*"
    FROM_OFFERS     = "📤 {name} bietet:"
    COUNTER_OFFER   = "📥 Gegenangebot:"
    STATUS          = "Status"
    FOOTER          = "Trade-ID: {trade_id}  ·  Läuft in 5 Min ab"
    OFFER_DESC      = "{mention}, du hast ein Trade-Angebot von **{name}** erhalten!"

    NOT_FOR_YOU     = "Dieses Angebot ist nicht für dich!"
    EXPIRED         = "❌ Trade abgelaufen oder nicht mehr vorhanden."
    TRADE_FAILED    = "❌ Trade fehlgeschlagen — Items nicht mehr vorhanden."
    ACCEPTED_STATUS = "✅ Trade angenommen von **{name}**!"
    DECLINED_STATUS = "❌ Trade abgelehnt von **{name}**."
    DECLINED_CONTENT = "❌ **{name}** hat das Trade-Angebot abgelehnt."
    TRADE_GONE      = "Trade nicht mehr vorhanden."
    COUNTER_NONE_SELECTED = "Keine Items ausgewählt."
    COUNTER_INVALID_NUMS  = "Ungültige Nummern: `{nums}`. Du hast **{count}** Items."
    COUNTER_SENT_STATUS   = (
        "🔄 **{to_name}** hat ein Gegenangebot geschickt!\n"
        "**{from_mention}**, akzeptiere mit `f.accepttrade {trade_id}`"
        " oder lehne ab mit `f.declinetrade {trade_id}`."
    )

    ACCEPT_LABEL   = "Annehmen"
    COUNTER_LABEL  = "Gegenangebot"
    DECLINE_LABEL  = "Ablehnen"

    COUNTER_MODAL_TITLE   = "Gegenangebot — Item-Nummern"
    COUNTER_INPUT_LABEL   = "Deine Item-Nummern (komma- oder leerzeichengetrennt)"
    COUNTER_PLACEHOLDER   = "z. B.: 1 4 7  oder  2,5"

    NOT_YOUR_TRADE_COUNTER  = "Nicht dein Trade!"
    ACCEPT_COUNTER_LABEL    = "Gegenangebot annehmen"
    TRADE_EXPIRED_COUNTER   = "Trade abgelaufen."
    COUNTER_DECLINED_CONTENT = "❌ Gegenangebot abgelehnt."
    COUNTER_FAILED           = "❌ Trade fehlgeschlagen — Items nicht mehr vorhanden."
    TRADE_DONE_STATUS        = "✅ Trade abgeschlossen zwischen **{from_name}** und **{to_name}**!"

    # accepttrade / declinetrade commands
    ACCEPT_USAGE             = "Verwendung: `f.accepttrade <trade_id>`"
    DECLINE_USAGE            = "Verwendung: `f.declinetrade <trade_id>`"
    NOT_FOUND                = "Trade nicht gefunden oder bereits abgelaufen."
    NOT_YOUR_TRADE           = "Das ist nicht dein Trade."
    NO_COUNTER_YET           = "Der andere Spieler hat noch kein Gegenangebot gemacht."
    CONFIRM_COUNTER_STATUS   = "Bestätige das Gegenangebot:"
    DECLINED_AND_REMOVED     = "Trade `{trade_id}` abgelehnt und entfernt."

    DESCRIPTION_TRADEOFFER   = "Sende ein Trade-Angebot: f.tradeoffer @user <item_nummern...>"
    DESCRIPTION_ACCEPTTRADE  = "Gegenangebot akzeptieren"
    DESCRIPTION_DECLINETRADE = "Gegenangebot ablehnen"


# ── Casino / Tradeup ──────────────────────────────────────────────────────────

class Tradeup:
    NOT_YOUR_TRADEUP  = "Nicht dein Trade Up!"
    MISSING_ITEMS     = "❌ Einige Items wurden zwischenzeitlich entfernt. Trade Up abgebrochen."
    INVALID_RARITY    = "Ungültige Seltenheit. Mögliche Werte: `lightblue`, `blue`, `purple`, `pink`\n(Gold kann nicht geupgradet werden)"
    NOT_ENOUGH_ITEMS  = (
        "Du brauchst mindestens **{count}** "
        "{emoji} {label} Items. "
        "Aktuell hast du **{have}**."
    )

    SUCCESS_TITLE   = "⬆️ Trade Up erfolgreich!"
    SUCCESS_DESC    = "10× {from_emoji} {from_label} → {to_emoji} **{to_label}**"
    FIELD_ERHALTEN  = "Erhalten"
    FIELD_FLOAT     = "Float"
    FIELD_PATTERN   = "Pattern"
    FIELD_STATTRAK  = "StatTrak™"
    FIELD_SELL      = "Verkaufswert"

    OVERVIEW_TITLE  = "⬆️ Trade Up Contract"
    OVERVIEW_DESC   = (
        "Tausche **10 Items** gleicher Seltenheit gegen **1 Item** der nächsten Stufe.\n"
        "Die 10 günstigsten Items werden automatisch ausgewählt.\n\n"
        "{lines}"
    )
    OVERVIEW_FOOTER = "f.tradeup <lightblue|blue|purple|pink>"

    CONFIRM_TITLE   = "⬆️ Trade Up Contract"
    CONFIRM_DESC    = (
        "Diese **10** {from_emoji} {from_label} Items "
        "(Gesamtwert: **{total_in:,}** {CURRENCY_EMOJI}) werden getauscht gegen\n"
        "**1** {to_emoji} {to_label} Item:"
    )
    FIELD_ITEMS_IN  = "Einzutauschende Items"
    CANCEL_CONTENT  = "Trade Up abgebrochen."

    CONFIRM_LABEL   = "Trade Up!"
    CANCEL_LABEL    = "Abbrechen"

    DESCRIPTION = "Tausche 10 Items einer Seltenheit für 1 Item der nächsten Stufe"


# ── Casino / Work ─────────────────────────────────────────────────────────────

class Work:
    JOBS = [
        ("🍔", "hat die fritten in die Tütte bei MCs gepackt"),
        ("🚗", "hat ein paar Obdachlose rumgefahren"),
        ("💻", "fixed someone's printer"),
        ("🛒", "stacked shelves at Lidl"),
        ("📦", "sorted packages at Amazon"),
        ("🔧", "fixed a leaky pipe"),
        ("🎸", "busked at the Hauptbahnhof"),
        ("🚚", "made DHL deliveries"),
        ("🧹", "cleaned an office building"),
        ("📱", "did customer support calls"),
    ]

    COOLDOWN    = "😴 You're still tired. Back to work in **{m}m {s}s**."
    TITLE       = "{emoji} Schicht beendet"
    DESCRIPTION = "You {desc} and earned **{earned:,}** {CURRENCY_EMOJI}."
    FOOTER      = "Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 10min"

    COMMAND_DESCRIPTION = "Work a shift for steady income"


# ── Help ──────────────────────────────────────────────────────────────────────

class Help:
    EMBED_TITLE     = "📖 Available Commands"
    PAGE_FOOTER     = "Page {page}/{total}"
    CAT_CONT_SUFFIX = " (cont.)"

    DESCRIPTION = "Zeig alle verf?gbaren Befehle"


# ── Games / Map ───────────────────────────────────────────────────────────────

class Map:
    REPLY       = "🗺️ Next map: **{chosen_map}**"
    DESCRIPTION = "Get a random map"


# ── Games / Roles ─────────────────────────────────────────────────────────────

class Roles:
    ROLES = {
        "AWP": "Missing every sit-shot but hitting the flick of a lifetime.",
        "Entry Fragger": "Dying in 2 seconds so the team can trade (hopefully).",
        "IGL": "Calling a strat that everyone will ignore anyway.",
        "Support": "Blinding your own teammates with 'perfect' flashes.",
        "Lurker": "Being on the other side of the map while the team dies.",
    }

    HEADER      = "🎭 **The Squad is Ready:**\n"
    DESCRIPTION = "Assign random CS2 roles"


# ── Games / Site ──────────────────────────────────────────────────────────────

class Site:
    REPLY       = "📍 Go **{site}**!"
    DESCRIPTION = "Randomly choose A, B, or Mid"


# ── Games / Strat ─────────────────────────────────────────────────────────────

class Strat:
    BUYS = [
        "Full glass-cannon: 5 Scouts and no armor",
        "4 SMGs and 1 Bait-Negev",
        "All 5 buy Deagles and 2 Flashbangs each",
    ]

    EXECUTIONS = [
        "perform a fake-out on one site and rotate through spawn",
        "execute a heavy smoke-wall and walk through the gaps",
        "rush without stopping, ignore all utility",
        "play for picks for 60 seconds then hit the weakest link",
        "split the team 2-3 and pinch the site from two angles",
    ]

    LOCATIONS = ["A Site", "B Site", "Mid to A", "Mid to B"]

    DYNAMIC_BUYS = [
        "{num_rifles} Rifles and {num_other} AWPs",
        "3 Shotguns for close-quarters and {num_other} Galils/Famas",
    ]

    STRAT_LINE   = "💰 **Buy:** {buy}\n🏃 **Plan:** {execution} at **{location}**.\n"
    EMBED_TITLE  = "🧠 Tactical Overlord Strategy"
    DESCRIPTION  = "Get a random team strategy"


# ── Faceit / Match ────────────────────────────────────────────────────────────

class FaceitMatch:
    PLAYER_NOT_FOUND  = "Player `{name}` not found."
    NOT_IN_MATCH      = "**{name}** is not currently in a match."
    LIVE_TITLE        = "🔴  {name} is in a live match"
    MAP_FIELD         = "🗺️ Map"
    ELAPSED_FIELD     = "⏱️ Elapsed"
    MATCH_ID_FIELD    = "🆔 Match"
    OUR_TEAM_LABEL    = "🟢 Your Team"
    OPPONENTS_LABEL   = "🔴 Opponents"

    DESCRIPTION = "Zeig Details zu einem Live-Match"


# ── Faceit / User ─────────────────────────────────────────────────────────────

class FaceitUser:
    PLAYER_NOT_FOUND  = "Player `{name}` not found."
    VERIFIED_YES      = "Yes"
    VERIFIED_NO       = "No"
    COUNTRY_UNKNOWN   = "Unknown"
    STEAM_PROFILE     = "Profile"
    FOOTER            = "FACEIT ID: {player_id}  •  Joined {activated}"
    ZERO_WIDTH        = "\u200b"

    FIELD_ELO         = "⚡ ELO"
    FIELD_LEVEL       = "🏅 Level"
    FIELD_MATCHES     = "🎮 Matches"
    FIELD_WIN_RATE    = "🏆 Win Rate"
    FIELD_KD          = "💀 Avg K/D"
    FIELD_HS          = "🎯 Avg HS%"
    FIELD_ADR         = "💥 ADR"
    FIELD_WIN_STREAK  = "🔥 Win Streak"
    FIELD_COUNTRY     = "🌍 Country"
    FIELD_MEMBERSHIP  = "💎 Membership"
    FIELD_VERIFIED    = "✅ Verified"
    FIELD_STEAM       = "🔗 Steam"
    FIELD_BANS        = "⛔ Active Bans"

    DESCRIPTION = "Show Faceit stats"


# ── Media / Play ──────────────────────────────────────────────────────────────

class Play:
    NO_VOICE_CHANNEL = "Du musst in einem Voice-Channel sein, sonst rede ich nur mit der Leere."
    NO_ATTACHMENT    = "H?ng eine Audiodatei an, sonst soll ich hier Luft auflegen."
    DESCRIPTION      = "Spiel eine angeh?ngte Audiodatei ab"


# ── Media / Stop ──────────────────────────────────────────────────────────────

class Stop:
    STOPPED         = "⏹️ Audio stopped and disconnected."
    NOT_IN_CHANNEL  = "Ich bin in keinem Voice-Channel."
    DESCRIPTION     = "Stoppe Audio und trenn die Verbindung"


# ── Media / TTS ───────────────────────────────────────────────────────────────

class TTS:
    NO_VOICE_CHANNEL = "Du musst in einem Voice-Channel sein, sonst rede ich nur mit der Leere."
    DESCRIPTION      = "Text zu Sprache im Voice-Channel"


# ── Media / YTPlay ────────────────────────────────────────────────────────────

class YTPlay:
    NO_VOICE_CHANNEL  = "Du musst in einem Voice-Channel sein, wenn wir gemeinsam Geh?rsch?den wollen."
    NO_QUERY          = "Gib eine Suche oder einen YouTube-Link an."
    SEARCHING         = "🔍 Searching for `{query}`..."
    ERROR             = "❌ Could not find or play track: {error}"
    NOW_PLAYING       = "🎵 **Now Playing (70% Vol):** [{title}](<{url}>)"
    DESCRIPTION       = "Spiel YouTube-Audio ab"
