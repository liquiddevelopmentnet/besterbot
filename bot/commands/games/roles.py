import random

from discord import Message

from bot.commands import command

ROLES = {
    "AWP": "Missing every sit-shot but hitting the flick of a lifetime.",
    "Entry Fragger": "Dying in 2 seconds so the team can trade (hopefully).",
    "IGL": "Calling a strat that everyone will ignore anyway.",
    "Support": "Blinding your own teammates with 'perfect' flashes.",
    "Lurker": "Being on the other side of the map while the team dies.",
}


@command(
    "roles",
    description="Assign random CS2 roles",
    usage="f.roles @p1 @p2 @p3 @p4 @p5",
    category="Games",
)
async def roles_command(message: Message, args: list[str]):
    if len(args) != 5:
        await message.reply("Usage: `f.roles @p1 @p2 @p3 @p4 @p5`")
        return

    players = list(args)
    random.shuffle(players)

    response = "🎭 **The Squad is Ready:**\n"
    for i, (role, desc) in enumerate(ROLES.items()):
        response += f"**{role}**: {players[i]} — *\"{desc}\"*\n"

    await message.channel.send(response)
