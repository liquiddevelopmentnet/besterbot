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

# ── Auth ──────────────────────────────────────────────────────────────────────

def _admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "")
    return {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}


def _is_admin(user_id: int) -> bool:
    return user_id in _admin_ids()


# ── Subcommand dispatch ───────────────────────────────────────────────────────

_USAGE = (
    "**Admin commands:**\n"
    "`f.admin setbal @user <amount>` — set exact balance\n"
    "`f.admin addbal @user <amount>` — add to balance\n"
    "`f.admin subbal @user <amount>` — subtract from balance (can go negative)\n"
    "`f.admin removeuser @user` — wipe user from the wallet\n"
    "`f.admin resetall [amount]` — reset everyone (default: starting balance)\n"
    "`f.admin viewbal @user` — check any user's balance\n"
)


async def _setbal(message: Message, args: list[str]):
    if not message.mentions or len(args) < 2 or not args[-1].lstrip("-").isdigit():
        await message.reply("Usage: `f.admin setbal @user <amount>`")
        return
    target = message.mentions[0]
    amount = int(args[-1])
    new = set_balance(target.id, amount)
    embed = tag_embed(discord.Embed(
        title=f"✅ Balance Set",
        description=f"**{target.display_name}** → **{new:,}** {CURRENCY_EMOJI}",
        color=0x2ECC71,
    ), message.author)
    await message.reply(embed=embed)


async def _addbal(message: Message, args: list[str]):
    if not message.mentions or len(args) < 2 or not args[-1].lstrip("-").isdigit():
        await message.reply("Usage: `f.admin addbal @user <amount>`")
        return
    target = message.mentions[0]
    amount = int(args[-1])
    new = add_balance(target.id, amount)
    embed = tag_embed(discord.Embed(
        title=f"✅ Balance Added",
        description=f"**{target.display_name}** +**{amount:,}** → **{new:,}** {CURRENCY_EMOJI}",
        color=0x2ECC71,
    ), message.author)
    await message.reply(embed=embed)


async def _subbal(message: Message, args: list[str]):
    if not message.mentions or len(args) < 2 or not args[-1].lstrip("-").isdigit():
        await message.reply("Usage: `f.admin subbal @user <amount>`")
        return
    target = message.mentions[0]
    amount = int(args[-1])
    new = force_remove_balance(target.id, amount)
    embed = tag_embed(discord.Embed(
        title=f"✅ Balance Subtracted",
        description=f"**{target.display_name}** -**{amount:,}** → **{new:,}** {CURRENCY_EMOJI}",
        color=0xE67E22,
    ), message.author)
    await message.reply(embed=embed)


async def _removeuser(message: Message, args: list[str]):
    if not message.mentions:
        await message.reply("Usage: `f.admin removeuser @user`")
        return
    target = message.mentions[0]
    existed = delete_user(target.id)
    if existed:
        embed = tag_embed(discord.Embed(
            title="🗑️ User Removed",
            description=f"**{target.display_name}** has been wiped from the wallet.",
            color=0xE74C3C,
        ), message.author)
    else:
        embed = tag_embed(discord.Embed(
            title="⚠️ User Not Found",
            description=f"**{target.display_name}** has no wallet entry.",
            color=0x95A5A6,
        ), message.author)
    await message.reply(embed=embed)


async def _resetall(message: Message, args: list[str]):
    amount = STARTING_BALANCE
    if args and args[-1].lstrip("-").isdigit():
        amount = int(args[-1])
    reset_all_balances(amount)
    embed = tag_embed(discord.Embed(
        title="♻️ All Balances Reset",
        description=f"Every wallet has been set to **{amount:,}** {CURRENCY_EMOJI}.",
        color=0x3498DB,
    ), message.author)
    await message.reply(embed=embed)


async def _viewbal(message: Message, args: list[str]):
    if not message.mentions:
        await message.reply("Usage: `f.admin viewbal @user`")
        return
    target = message.mentions[0]
    bal = get_balance(target.id)
    embed = tag_embed(discord.Embed(
        title=f"👁️ {target.display_name}'s Balance",
        description=f"**{bal:,}** {CURRENCY_EMOJI}",
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

@command("admin", description="Admin casino controls", usage="f.admin <subcommand>", category="Casino")
async def admin_command(message: Message, args: list[str]):
    if not _is_admin(message.author.id):
        await message.reply("🚫 You don't have permission to use this command.")
        return

    if not args:
        await message.reply(_USAGE)
        return

    sub = args[0].lower()
    handler = _SUBCOMMANDS.get(sub)
    if handler is None:
        await message.reply(f"Unknown subcommand `{sub}`.\n\n{_USAGE}")
        return

    await handler(message, args[1:])
