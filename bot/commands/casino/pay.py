import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    transfer, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI,
)
from bot.strings import Pay as S


@command("pay", description=S.DESCRIPTION_CMD, usage="f.pay @user <amount>", category="Casino")
async def pay_command(message: Message, args: list[str]):
    if len(args) < 2 or not message.mentions:
        await message.reply("Usage: `f.pay @user <amount>`")
        return

    target = message.mentions[0]
    if target.id == message.author.id:
        await message.reply(S.CANT_PAY_SELF)
        return

    # Amount is the last arg (mention takes the first)
    raw_amount = args[-1]
    if not raw_amount.isdigit() or int(raw_amount) <= 0:
        await message.reply(S.INVALID_AMOUNT)
        return

    amount = int(raw_amount)
    try:
        sender_bal, receiver_bal = transfer(message.author.id, target.id, amount)
    except ValueError:
        await message.reply(S.NOT_ENOUGH.format(CURRENCY_NAME=CURRENCY_NAME))
        return

    embed = tag_embed(discord.Embed(
        title=S.TITLE.format(CURRENCY_EMOJI=CURRENCY_EMOJI),
        description=S.DESCRIPTION.format(sender=message.author.display_name, amount=amount, CURRENCY_NAME=CURRENCY_NAME, target=target.display_name),
        color=0x2ECC71,
    ), message.author)
    embed.add_field(name=S.YOUR_BALANCE, value=f"{sender_bal:,}", inline=True)
    embed.add_field(name=S.THEIR_BALANCE.format(name=target.display_name), value=f"{receiver_bal:,}", inline=True)
    await message.reply(embed=embed)
