import random

from discord import Message

from bot.commands import command


@command(
    "site",
    description="Randomly choose A, B, or Mid",
    usage="f.site",
    category="Games",
)
async def site_command(message: Message, args: list[str]):
    site = random.choice(["A", "B", "Mid"])
    await message.reply(f"📍 Go **{site}**!")
