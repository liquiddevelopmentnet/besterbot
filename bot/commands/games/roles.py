import random

from discord import Message

from bot.commands import command
from bot.strings import Roles as S


@command(
    "roles",
    description=S.DESCRIPTION,
    usage="f.roles @p1 @p2 @p3 @p4 @p5",
    category="Games",
)
async def roles_command(message: Message, args: list[str]):
    if len(args) != 5:
        await message.reply("Usage: `f.roles @p1 @p2 @p3 @p4 @p5`")
        return

    players = list(args)
    random.shuffle(players)

    response = S.HEADER
    for i, (role, desc) in enumerate(S.ROLES.items()):
        response += f"**{role}**: {players[i]} — *\"{desc}\"*\n"

    await message.channel.send(response)
