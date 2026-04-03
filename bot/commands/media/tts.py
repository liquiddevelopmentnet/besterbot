import asyncio
import os

import discord
from discord import Message
from gtts import gTTS

from bot.commands import command
from bot.commands.media import voice
from bot.strings import TTS as S


@command(
    "tts",
    description=S.DESCRIPTION,
    usage="f.tts <text>",
    category="Media",
)
async def tts_command(message: Message, args: list[str]):
    if not message.author.voice:
        await message.reply(S.NO_VOICE_CHANNEL)
        return

    text = " ".join(args)
    channel = message.author.voice.channel

    tts = gTTS(text=text, lang='de')
    filename = "temp_speech.mp3"
    tts.save(filename)

    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()

    voice.vc = await channel.connect()
    voice.vc.play(discord.FFmpegPCMAudio(filename), after=lambda e: print('Finished', e))

    while voice.vc.is_playing():
        await asyncio.sleep(1)

    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()

    if os.path.exists(filename):
        os.remove(filename)
