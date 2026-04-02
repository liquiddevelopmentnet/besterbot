import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    transfer, tag_embed, CURRENCY_NAME, CURRENCY_EMOJI,
)


@command("pay", description="Send currency to another player", usage="f.pay @user <amount>", category="Casino")
async def pay_command(message: Message, args: list[str]):
    if len(args) < 2 or not message.mentions:
        await message.reply("Usage: `f.pay @user <amount>`")
        return

    target = message.mentions[0]
    if target.id == message.author.id:
        await message.reply("You can't pay yourself.")
        return

    # Amount is the last arg (mention takes the first)
    raw_amount = args[-1]
    if not raw_amount.isdigit() or int(raw_amount) <= 0:
        await message.reply("Amount must be a positive number.")
        return

    amount = int(raw_amount)
    try:
        sender_bal, receiver_bal = transfer(message.author.id, target.id, amount)
    except ValueError:
        await message.reply(f"You don't have enough {CURRENCY_NAME}!")
        return

    embed = tag_embed(discord.Embed(
        title=f"{CURRENCY_EMOJI} Payment Sent",
        description=(
            f"**{message.author.display_name}** paid **{amount:,}** {CURRENCY_NAME} "
            f"to **{target.display_name}**"
        ),
        color=0x2ECC71,
    ), message.author)
    embed.add_field(name="Your Balance", value=f"{sender_bal:,}", inline=True)
    embed.add_field(name=f"{target.display_name}'s Balance", value=f"{receiver_bal:,}", inline=True)
    await message.reply(embed=embed)
