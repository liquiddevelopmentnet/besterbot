import random

from discord import Message

from bot.commands import command
from bot.strings import Map as S

MAPS = ["Mirage", "Inferno", "Nuke", "Overpass", "Vertigo", "Anubis", "Ancient"]


@command(
    "map",
    description=S.DESCRIPTION,
    usage="f.map",
    category="Games",
)
async def map_command(message: Message, args: list[str]):
    chosen_map = random.choice(MAPS)
    await message.reply(S.REPLY.format(chosen_map=chosen_map))
