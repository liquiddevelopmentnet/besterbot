from discord import Message

from bot.commands import command
from bot.commands.media import voice
from bot.strings import Stop as S


@command(
    "stop",
    description=S.DESCRIPTION,
    usage="f.stop",
    category="Media",
)
async def stop_command(message: Message, args: list[str]):
    if voice.vc and voice.vc.is_connected():
        await voice.vc.disconnect()
        await message.reply(S.STOPPED)
    else:
        await message.reply(S.NOT_IN_CHANNEL)
