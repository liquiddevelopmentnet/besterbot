import asyncio

import discord
import yt_dlp
from discord import Message

from bot.commands import command
from bot.commands.media import voice
from bot.strings import YTPlay as S

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


@command(
    "ytplay",
    description=S.DESCRIPTION,
    usage="f.ytplay <query>",
    category="Media",
)
async def ytplay_command(message: Message, args: list[str]):
    if not message.author.voice:
        await message.reply(S.NO_VOICE_CHANNEL)
        return

    query = " ".join(args)
    if not query:
        await message.reply(S.NO_QUERY)
        return

    status_msg = await message.reply(S.SEARCHING.format(query=query))
    loop = asyncio.get_running_loop()

    try:
        info = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
    except Exception as e:
        await status_msg.edit(content=S.ERROR.format(error=e))
        return

    if 'entries' in info:
        info = info['entries'][0]

    song_url = info['url']
    song_title = info.get('title', 'Unknown Title')
    webpage_url = info.get('webpage_url', '')

    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()

    channel = message.author.voice.channel
    voice.vc = await channel.connect()

    audio_source = discord.FFmpegPCMAudio(song_url, **FFMPEG_OPTIONS)
    source = discord.PCMVolumeTransformer(audio_source)
    source.volume = 0.7

    voice.vc.play(source, after=lambda e: print(f'Finished/Error: {e}') if e else None)

    await status_msg.edit(content=S.NOW_PLAYING.format(title=song_title, url=webpage_url))

    while voice.vc.is_playing():
        await asyncio.sleep(1)

    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()
