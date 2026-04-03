"""Cumulative gambling earnings graph — f.bip / f.bip all / f.bip @user"""
import io
from datetime import datetime, timezone

import discord
from discord import Message

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from bot.commands import command
from bot.commands.casino.wallet import (
    get_earnings_history, get_all_earnings_history, CURRENCY_EMOJI, CURRENCY_NAME,
)

# ── Palette for multi-user mode ────────────────────────────────────────────────
_COLORS = [
    "#5865F2",  # Discord blurple
    "#57F287",  # green
    "#FEE75C",  # yellow
    "#ED4245",  # red
    "#EB459E",  # pink
    "#2C9EAB",  # teal
    "#F9602E",  # orange
    "#B5BAC1",  # grey
]

_BG     = "#1E2124"
_AX_BG  = "#282B30"
_GRID   = "#36393F"
_TEXT   = "#DCDDDE"


def _cumulative(events: list[tuple[float, int]]) -> tuple[list, list]:
    """Convert [(ts, amount), …] → ([datetime, …], [cumulative, …])."""
    times, values = [], []
    total = 0
    for ts, amount in events:
        total += amount
        times.append(datetime.fromtimestamp(ts, tz=timezone.utc))
        values.append(total)
    return times, values


def _make_chart(
    series: dict[str, tuple[list, list]],
    *,
    title: str,
) -> io.BytesIO:
    """Generate the chart and return a PNG BytesIO."""
    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_AX_BG)

    for i, (name, (times, values)) in enumerate(series.items()):
        color = _COLORS[i % len(_COLORS)]
        if times:
            # Prepend origin so the line starts at 0
            origin = times[0].replace(hour=0, minute=0, second=0, microsecond=0)
            ax.plot([origin] + times, [0] + values, color=color, linewidth=2,
                    label=name, marker="o", markersize=3)
        else:
            ax.plot([], [], color=color, label=name)

    ax.set_title(title, color=_TEXT, fontsize=13, pad=10)
    ax.set_xlabel("Datum", color=_TEXT, fontsize=10)
    ax.set_ylabel(f"Gesamteinnahmen ({CURRENCY_EMOJI})", color=_TEXT, fontsize=10)
    ax.tick_params(colors=_TEXT, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(_GRID)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{int(x):,}")
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.grid(color=_GRID, linewidth=0.5)
    fig.autofmt_xdate()

    if len(series) > 1:
        leg = ax.legend(
            facecolor=_AX_BG, labelcolor=_TEXT, edgecolor=_GRID, fontsize=9
        )

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(), dpi=130)
    buf.seek(0)
    plt.close(fig)
    return buf


def _stats_field(events: list[tuple[float, int]]) -> str:
    if not events:
        return "Keine Daten"
    total = sum(a for _, a in events)
    count = len(events)
    return f"**{total:,}** {CURRENCY_EMOJI} in **{count}** Events"


@command("bip", description="Zeige den kumulativen Gambling-Verdienst als Graph",
         usage="f.bip / f.bip all / f.bip @user", category="Casino")
async def bip_command(message: Message, args: list[str]):
    show_all = args and args[0].lower() == "all"
    mentioned = message.mentions[0] if message.mentions else None

    # ── Resolve what to show ──────────────────────────────────────────────────
    if show_all:
        raw = get_all_earnings_history()
        if not raw:
            await message.reply("Noch keine Gambling-Einnahmen aufgezeichnet.")
            return

        # Resolve display names
        series: dict[str, tuple] = {}
        stats:  dict[str, list]  = {}
        for uid, events in raw.items():
            member = message.guild.get_member(int(uid)) if message.guild else None
            name = member.display_name if member else f"#{uid[:6]}"
            # Deduplicate names
            base, n = name, 1
            while name in series:
                n += 1
                name = f"{base} ({n})"
            times, values = _cumulative(events)
            series[name] = (times, values)
            stats[name]  = events

        chart_title = "📈 Gambling Einnahmen — Alle Spieler"
        embed = discord.Embed(title=chart_title, color=0x5865F2)
        for name, events in stats.items():
            embed.add_field(name=name, value=_stats_field(events), inline=True)

    elif mentioned:
        events = get_earnings_history(mentioned.id)
        if not events:
            await message.reply(f"**{mentioned.display_name}** hat noch keine Gambling-Einnahmen.")
            return
        times, values = _cumulative(events)
        series = {mentioned.display_name: (times, values)}
        chart_title = f"📈 Gambling Einnahmen — {mentioned.display_name}"
        embed = discord.Embed(title=chart_title, color=0x5865F2)
        embed.add_field(name="Gesamt", value=_stats_field(events), inline=True)
        embed.add_field(
            name="Letztes Event",
            value=f"<t:{int(events[-1][0])}:R>",
            inline=True,
        )
        embed.set_author(
            name=mentioned.display_name,
            icon_url=str(mentioned.display_avatar.url),
        )

    else:
        # Own stats
        events = get_earnings_history(message.author.id)
        if not events:
            await message.reply("Du hast noch keine Gambling-Einnahmen. Spiel erstmal was!")
            return
        times, values = _cumulative(events)
        series = {message.author.display_name: (times, values)}
        chart_title = f"📈 Gambling Einnahmen — {message.author.display_name}"
        embed = discord.Embed(title=chart_title, color=0x5865F2)
        embed.add_field(name="Gesamt", value=_stats_field(events), inline=True)
        embed.add_field(
            name="Letztes Event",
            value=f"<t:{int(events[-1][0])}:R>",
            inline=True,
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=str(message.author.display_avatar.url),
        )

    # ── Generate and send chart ───────────────────────────────────────────────
    buf = _make_chart(series, title=chart_title)
    file = discord.File(fp=buf, filename="bip.png")
    embed.set_image(url="attachment://bip.png")
    embed.set_footer(text="Brutto-Einnahmen · Verluste nicht abgezogen")
    await message.reply(embed=embed, file=file)
