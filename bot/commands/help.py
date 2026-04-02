import discord
from discord import Message

from bot.commands import command
from bot.commands.registry import get_commands_by_category

_EMBED_COLOUR = 0x5865F2
_MAX_FIELD_VALUE = 1024
_MAX_FIELDS = 25
_MAX_EMBEDS = 10


def _build_embeds(categories: dict) -> list[discord.Embed]:
    """Build one or more embeds that fit Discord limits."""
    embeds: list[discord.Embed] = []
    current = discord.Embed(title="📖 Available Commands", colour=_EMBED_COLOUR)
    field_count = 0

    for cat_name, cmds in sorted(categories.items()):
        lines: list[str] = []
        for cmd in sorted(cmds, key=lambda c: c.name):
            usage = cmd.usage or f"f.{cmd.name}"
            desc = f" — {cmd.description}" if cmd.description else ""
            lines.append(f"`{usage}`{desc}")

        # Split oversized categories across multiple fields
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_len = 0
        for line in lines:
            if current_len + len(line) + 1 > _MAX_FIELD_VALUE:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_len = len(line)
            else:
                current_chunk.append(line)
                current_len += len(line) + 1
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        for i, chunk in enumerate(chunks):
            name = f"__**{cat_name}**__" if i == 0 else f"__**{cat_name} (cont.)**__"

            # Start a new embed if this one is full
            if field_count >= _MAX_FIELDS:
                embeds.append(current)
                current = discord.Embed(colour=_EMBED_COLOUR)
                field_count = 0

            current.add_field(name=name, value=chunk, inline=False)
            field_count += 1

    if field_count > 0 or not embeds:
        embeds.append(current)

    # Number pages if more than one
    if len(embeds) > 1:
        for i, embed in enumerate(embeds):
            embed.set_footer(text=f"Page {i + 1}/{len(embeds)}")

    return embeds[:_MAX_EMBEDS]


@command(
    "help",
    description="Show all available commands",
    usage="f.help",
    category="General",
)
async def help_command(message: Message, args: list[str]):
    categories = get_commands_by_category()
    embeds = _build_embeds(categories)
    # Send all embeds in a single API call (Discord allows up to 10 per message)
    await message.channel.send(embeds=embeds)
