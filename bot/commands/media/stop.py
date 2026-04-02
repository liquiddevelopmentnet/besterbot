from discord import Message

from bot.commands import command
from bot.commands.media import voice


@command(
    "stop",
    description="Stop audio and disconnect",
    usage="f.stop",
    category="Media",
)
async def stop_command(message: Message, args: list[str]):
    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()
        await message.reply("⏹️ Audio stopped and disconnected.")
    else:
        await message.reply("I'm not in a voice channel.")
