import random

import discord
from discord import Message

from bot.commands import command

BUYS = [
    "Full glass-cannon: 5 Scouts and no armor",
    "4 SMGs and 1 Bait-Negev",
    "All 5 buy Deagles and 2 Flashbangs each",
]

EXECUTIONS = [
    "perform a fake-out on one site and rotate through spawn",
    "execute a heavy smoke-wall and walk through the gaps",
    "rush without stopping, ignore all utility",
    "play for picks for 60 seconds then hit the weakest link",
    "split the team 2-3 and pinch the site from two angles",
]

LOCATIONS = ["A Site", "B Site", "Mid to A", "Mid to B"]


@command(
    "strat",
    description="Get a random team strategy",
    usage="f.strat",
    category="Games",
)
async def strat_command(message: Message, args: list[str]):
    num_rifles = random.randint(1, 4)
    num_other = 5 - num_rifles

    dynamic_buys = [
        f"{num_rifles} Rifles and {num_other} AWPs",
        f"3 Shotguns for close-quarters and {num_other} Galils/Famas",
    ]

    strat = (
        f"💰 **Buy:** {random.choice(dynamic_buys + BUYS)}\n"
        f"🏃 **Plan:** {random.choice(EXECUTIONS)} at **{random.choice(LOCATIONS)}**.\n"
    )

    embed = discord.Embed(title="🧠 Tactical Overlord Strategy", description=strat, color=0x3498DB)
    await message.reply(embed=embed)
