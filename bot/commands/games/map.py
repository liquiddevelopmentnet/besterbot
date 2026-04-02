import random

from discord import Message

from bot.commands import command

MAPS = ["Mirage", "Inferno", "Nuke", "Overpass", "Vertigo", "Anubis", "Ancient"]


@command(
    "map",
    description="Get a random map",
    usage="f.map",
    category="Games",
)
async def map_command(message: Message, args: list[str]):
    chosen_map = random.choice(MAPS)
    await message.reply(f"🗺️ Next map: **{chosen_map}**")
