"""Admin-only casino commands — restricted to ADMIN_IDS in .env."""

import os

import discord
from discord import Message

from bot.commands import command
from bot.commands.casino.wallet import (
    get_balance, set_balance, add_balance, force_remove_balance,
    delete_user, reset_all_balances, get_leaderboard,
    tag_embed, CURRENCY_NAME, CURRENCY_EMOJI, STARTING_BALANCE,
)
from bot.strings import Admin as S

# ── Auth ──────────────────────────────────────────────────────────────────────

def _admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "")
    return {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}


def _is_admin(user_id: int) -> bool:
    return user_id in _admin_ids()


# ── Subcommand dispatch ───────────────────────────────────────────────────────



async def _setbal(message: Message, args: list[str]):
    if not message.mentions or len(args) < 2 or not args[-1].lstrip("-").isdigit():
        await message.reply(S.SETBAL_USAGE)
        return
    target = message.mentions[0]
    amount = int(args[-1])
    new = set_balance(target.id, amount)
    embed = tag_embed(discord.Embed(
        title=S.SETBAL_TITLE,
        description=S.SETBAL_DESC.format(name=target.display_name, new=new, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x2ECC71,
    ), message.author)
    await message.reply(embed=embed)


async def _addbal(message: Message, args: list[str]):
    if not message.mentions or len(args) < 2 or not args[-1].lstrip("-").isdigit():
        await message.reply(S.ADDBAL_USAGE)
        return
    target = message.mentions[0]
    amount = int(args[-1])
    new = add_balance(target.id, amount)
    embed = tag_embed(discord.Embed(
        title=S.ADDBAL_TITLE,
        description=S.ADDBAL_DESC.format(name=target.display_name, amount=amount, new=new, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x2ECC71,
    ), message.author)
    await message.reply(embed=embed)


async def _subbal(message: Message, args: list[str]):
    if not message.mentions or len(args) < 2 or not args[-1].lstrip("-").isdigit():
        await message.reply(S.SUBBAL_USAGE)
        return
    target = message.mentions[0]
    amount = int(args[-1])
    new = force_remove_balance(target.id, amount)
    embed = tag_embed(discord.Embed(
        title=S.SUBBAL_TITLE,
        description=S.SUBBAL_DESC.format(name=target.display_name, amount=amount, new=new, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0xE67E22,
    ), message.author)
    await message.reply(embed=embed)


async def _removeuser(message: Message, args: list[str]):
    if not message.mentions:
        await message.reply(S.REMOVEUSER_USAGE)
        return
    target = message.mentions[0]
    existed = delete_user(target.id)
    if existed:
        embed = tag_embed(discord.Embed(
            title=S.REMOVEUSER_TITLE,
            description=S.REMOVEUSER_DESC.format(name=target.display_name),
            color=0xE74C3C,
        ), message.author)
    else:
        embed = tag_embed(discord.Embed(
            title=S.NOTFOUND_TITLE,
            description=S.NOTFOUND_DESC.format(name=target.display_name),
            color=0x95A5A6,
        ), message.author)
    await message.reply(embed=embed)


async def _resetall(message: Message, args: list[str]):
    amount = STARTING_BALANCE
    if args and args[-1].lstrip("-").isdigit():
        amount = int(args[-1])
    reset_all_balances(amount)
    embed = tag_embed(discord.Embed(
        title=S.RESETALL_TITLE,
        description=S.RESETALL_DESC.format(amount=amount, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0x3498DB,
    ), message.author)
    await message.reply(embed=embed)


async def _viewbal(message: Message, args: list[str]):
    if not message.mentions:
        await message.reply(S.VIEWBAL_USAGE)
        return
    target = message.mentions[0]
    bal = get_balance(target.id)
    embed = tag_embed(discord.Embed(
        title=S.VIEWBAL_TITLE.format(name=target.display_name),
        description=S.VIEWBAL_DESC.format(bal=bal, CURRENCY_EMOJI=CURRENCY_EMOJI),
        color=0xF1C40F,
    ), message.author)
    await message.reply(embed=embed)


_SUBCOMMANDS = {
    "setbal":     _setbal,
    "addbal":     _addbal,
    "subbal":     _subbal,
    "removeuser": _removeuser,
    "resetall":   _resetall,
    "viewbal":    _viewbal,
}


# ── Entry point ───────────────────────────────────────────────────────────────

@command("admin", description=S.DESCRIPTION, usage="f.admin <subcommand>", category="Casino")
async def admin_command(message: Message, args: list[str]):
    if not _is_admin(message.author.id):
        await message.reply(S.NO_PERMISSION)
        return

    if not args:
        await message.reply(S.USAGE)
        return

    sub = args[0].lower()
    handler = _SUBCOMMANDS.get(sub)
    if handler is None:
        await message.reply(S.UNKNOWN_SUBCOMMAND.format(sub=sub, usage=S.USAGE))
        return

    await handler(message, args[1:])
