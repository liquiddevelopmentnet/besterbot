import random
import time

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    add_balance, get_cooldown, set_cooldown, tag_embed,
    CURRENCY_EMOJI, CURRENCY_NAME,
)

_KEY = "last_finanzspritze"
_COOLDOWN = 3600  # 1 hour
_AMOUNT = 10_000

_RESPONSES = [
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


@command("finanzspritze", description="Stündliche staatliche Finanzspritze", usage="f.finanzspritze", category="Casino")
async def finanzspritze_command(message: Message, args: list[str]):
    last = get_cooldown(message.author.id, _KEY)
    if last:
        remaining = _COOLDOWN - (time.time() - last)
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            await message.reply(f"💶 Der Haushalt wird gerade neu verhandelt. Nochmal in **{m}m {s}s**.")
            return

    new_bal = add_balance(message.author.id, _AMOUNT)
    set_cooldown(message.author.id, _KEY, time.time())

    embed = tag_embed(discord.Embed(
        title="💶 Finanzspritze erhalten!",
        description=f"{random.choice(_RESPONSES)}\n+**{_AMOUNT:,}** {CURRENCY_EMOJI}",
        color=0xF1C40F,
    ), message.author)
    embed.set_footer(text=f"Balance: {new_bal:,} {CURRENCY_EMOJI} • Cooldown: 1h")
    await message.reply(embed=embed)
