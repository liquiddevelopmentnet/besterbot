import random

import discord
from discord import Message

from bot.commands import command
from bot.strings import Strat as S


@command(
    "strat",
    description=S.DESCRIPTION,
    usage="f.strat",
    category="Games",
)
async def strat_command(message: Message, args: list[str]):
    num_rifles = random.randint(1, 4)
    num_other = 5 - num_rifles

    dynamic_buys = [
        S.DYNAMIC_BUYS[0].format(num_rifles=num_rifles, num_other=num_other),
        S.DYNAMIC_BUYS[1].format(num_other=num_other),
    ]

    strat = S.STRAT_LINE.format(
        buy=random.choice(dynamic_buys + S.BUYS),
        execution=random.choice(S.EXECUTIONS),
        location=random.choice(S.LOCATIONS),
    )

    embed = discord.Embed(title=S.EMBED_TITLE, description=strat, color=0x3498DB)
    await message.reply(embed=embed)
