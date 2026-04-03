import asyncio

import discord
from discord import Message

from bot.commands import command
from bot.commands.media import voice
from bot.strings import Play as S

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}


@command(
    "play",
    description=S.DESCRIPTION,
    usage="f.play <file>",
    category="Media",
)
async def play_command(message: Message, args: list[str]):
    if not message.author.voice:
        await message.reply(S.NO_VOICE_CHANNEL)
        return

    if len(message.attachments) == 0:
        await message.reply(S.NO_ATTACHMENT)
        return

    attachment = message.attachments[0]

    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()

    channel = message.author.voice.channel
    voice.vc = await channel.connect()

    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(attachment.url, **FFMPEG_OPTIONS)
    )
    source.volume = 0.7

    voice.vc.play(source, after=lambda e: print('Finished', e))

    while voice.vc.is_playing():
        await asyncio.sleep(1)

    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()
