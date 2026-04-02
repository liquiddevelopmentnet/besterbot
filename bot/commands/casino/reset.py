"""Broke-detection and dramatic balance-reset sequence."""

from __future__ import annotations

import asyncio
import os

import discord
from discord import Message
from gtts import gTTS

from bot.commands.casino.wallet import (
    everyone_broke, reset_all_balances, CURRENCY_EMOJI,
)

_RESET_AMOUNT = 5_000
_VOICELINE = (
    "ACHTUNG! Trump hat alle US Staatsfonds in den Irankrieg investiert. "
    "Jeder Gambler ist pleite. "
    "Benjamin Netanyahu hat beschlossen, das Maka verbot aufzuheben und die 15.000 Maka Flaschen zurückzukaufen, um die Wirtschaft zu stabilisieren. "
    "alle Mossad Agenten haben die Casinos infiltriert und die Konten der Spieler auf 15.000 Maka zurückgesetzt. "
    "isreal gewinnt immer. "
)
_TTS_FILE = "reset_voiceline.mp3"


def _most_populated_vc(guild: discord.Guild) -> discord.VoiceChannel | None:
    populated = [vc for vc in guild.voice_channels if len(vc.members) > 0]
    if not populated:
        return None
    return max(populated, key=lambda vc: len(vc.members))


async def check_broke_reset(message: Message) -> None:
    check_broke_reset_disabled = True
    if check_broke_reset_disabled:
        return
    """Call after every Casino command. Triggers the reset sequence if everyone is broke."""
    if not everyone_broke():
        return

    guild = message.guild
    vc_channel = _most_populated_vc(guild)

    # ── Announcement embed ────────────────────────────────────────
    embed = discord.Embed(
        title="💀 EVERYONE IS BROKE",
        description=(
            f"Every single gambler has hit zero.\n\n"
            f"The house shows mercy.\n"
            f"**All balances reset to {_RESET_AMOUNT:,} {CURRENCY_EMOJI}**"
        ),
        color=0xFF0000,
    )
    embed.set_footer(text="The casino always wins.")
    await message.channel.send(embed=embed)

    reset_all_balances(_RESET_AMOUNT)

    # ── Voice announcement ────────────────────────────────────────
    return
    if vc_channel is None:
        return

    tts = gTTS(text=_VOICELINE, lang="de")
    tts.save(_TTS_FILE)

    vc = None
    try:
        vc = await vc_channel.connect()
        vc.play(discord.FFmpegPCMAudio(_TTS_FILE))
        while vc.is_playing():
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"[reset] voice error: {e}")
    finally:
        if vc and vc.is_connected():
            await vc.disconnect()
        if os.path.exists(_TTS_FILE):
            os.remove(_TTS_FILE)
