import random

from discord import Message

from bot.commands import command
from bot.strings import Site as S


@command(
    "site",
    description=S.DESCRIPTION,
    usage="f.site",
    category="Games",
)
async def site_command(message: Message, args: list[str]):
    site = random.choice(["A", "B", "Mid"])
    await message.reply(S.REPLY.format(site=site))
