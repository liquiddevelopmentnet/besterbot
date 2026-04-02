import asyncio
import os
import random

import discord
from discord import Message
from dotenv import load_dotenv
from gtts import gTTS

from bot.db import init_db
from bot.commands.casino.wallet import get_balance
from bot.commands.registry import load_commands, get_command
from bot.commands.casino.reset import check_broke_reset, _most_populated_vc

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    allowed_channels = [int(cid.strip()) for cid in os.getenv('DISCORD_CHANNEL_ID', '').split(',') if cid.strip()]
    if message.channel.id not in allowed_channels:
        print(f'Ignoring message from channel {message.channel.id}')
        return

    if message.content.startswith('nigger?'):
        black = random.random()
        if black > 0.5:
            await message.reply(f'Du bist zu {black*100:.2f}% schwarz, du NIGGER!')
        else:
            await message.reply(f'Zum glück nur zu {black*100:.2f}% schwarz, good boy')

    if message.content.startswith('respektlos'):
        guild = message.guild
        vc_channel = _most_populated_vc(guild)
        if vc_channel is None:
            return

        bal = get_balance(message.author.id)
        if bal == 0:
            tts = gTTS(
                text=f"du fettes opfer {message.author.display_name}, imagine man hat keine maka flaschen nigger",
                lang="de")
        else:
            tts = gTTS(
                text=f"du fettes opfer {message.author.display_name}, imagine man hat nur noch {bal} maka flaschen nigger",
                lang="de")
        tts.save("voiceline.mp3")

        vc = None
        try:
            vc = await vc_channel.connect()
            vc.play(discord.FFmpegPCMAudio("voiceline.mp3"))
            while vc.is_playing():
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"[reset] voice error: {e}")
        finally:
            if vc and vc.is_connected():
                await vc.disconnect()
            if os.path.exists("voiceline.mp3"):
                os.remove("voiceline.mp3")

    if message.content.startswith('f.') or message.content.startswith('.'):
        raw = message.content.split(" ")
        cmd_name = raw[0][2:] if message.content.startswith('f.') else raw[0][1:]
        args = raw[1:]
        print(f"cmd={cmd_name} args={args}")

        cmd = get_command(cmd_name)
        if cmd:
            await cmd.handler(message, args)
            if cmd.category == "Casino":
                await check_broke_reset(message)
        else:
            await message.reply(f"`{cmd_name}` ist kein befehl ni")


init_db()
load_commands()
client.run(os.getenv('DISCORD_TOKEN'))
