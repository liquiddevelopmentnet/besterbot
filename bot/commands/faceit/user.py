import discord
from discord import Message
from faceit import GameID
from faceit.exceptions import APIError

from bot.commands import command
from bot.commands.faceit.client import data, LEVEL_COLORS, LEVEL_BARS


def build_faceit_embed(player: dict, stats: dict | None = None) -> discord.Embed:
    cs2 = player.get("games", {}).get("cs2", {})
    level = cs2.get("skill_level", 1)
    elo = cs2.get("faceit_elo", 0)
    name = player.get("nickname", "Unknown")

    embed = discord.Embed(
        title=name,
        url=player.get("faceit_url", "").replace("{lang}", "en"),
        color=LEVEL_COLORS.get(level, 0xFF5500),
    )

    if player.get("avatar"):
        embed.set_thumbnail(url=player["avatar"])

    embed.add_field(name="⚡ ELO", value=f"**{elo:,}**", inline=True)
    embed.add_field(name="🏅 Level", value=f"**{level}**/10\n`{LEVEL_BARS[level]}`", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    if stats:
        lt = stats.get("lifetime", {})

        kd = float(lt.get("Average K/D Ratio", 0))
        wr = int(lt.get("Win Rate %", 0))
        kd_color = "🟢" if kd >= 1.2 else ("🟡" if kd >= 0.9 else "🔴")
        wr_color = "🟢" if wr >= 55 else ("🟡" if wr >= 45 else "🔴")

        embed.add_field(name="🎮 Matches", value=f"**{int(lt.get('Matches', 0)):,}**", inline=True)
        embed.add_field(name="🏆 Win Rate", value=f"{wr_color} **{wr}%**", inline=True)
        embed.add_field(name="💀 Avg K/D", value=f"{kd_color} **{kd:.2f}**", inline=True)
        embed.add_field(name="🎯 Avg HS%", value=f"**{lt.get('Average Headshots %', '—')}%**", inline=True)
        embed.add_field(name="💥 ADR", value=f"**{float(lt.get('ADR', 0)):.1f}**", inline=True)
        embed.add_field(name="🔥 Win Streak", value=f"**{lt.get('Current Win Streak', '—')}**", inline=True)

    country = player.get("country", "")
    flag = f":flag_{country.lower()}:" if country else "Unknown"
    membership = player.get("membership_type") or (player.get("memberships") or ["free"])[0]
    verified = player.get("verified", False)

    embed.add_field(name="🌍 Country", value=flag, inline=True)
    embed.add_field(name="💎 Membership", value=membership.capitalize(), inline=True)
    embed.add_field(name="✅ Verified", value="Yes" if verified else "No", inline=True)

    steam_url = player.get("platforms", {}).get("steam")
    if steam_url and steam_url.startswith("http"):
        embed.add_field(name="🔗 Steam", value=f"[Profile]({steam_url})", inline=True)

    bans = player.get("infractions", {}).get("bans") or []
    if bans:
        ban_lines = "\n".join(f"• `{b['type']}` — {b['reason']}" for b in bans)
        embed.add_field(name="⛔ Active Bans", value=ban_lines, inline=False)

    activated = player.get("activated_at", "")[:10]
    embed.set_footer(text=f"FACEIT ID: {player['player_id']}  •  Joined {activated}")
    return embed


@command(
    "user",
    description="Show Faceit stats",
    usage="f.user <name>",
    category="Faceit",
)
async def user_command(message: Message, args: list[str]):
    if len(args) != 1:
        await message.reply("Usage: `f.user <name>`")
        return

    try:
        player = data.raw_players.get(args[0])
    except APIError:
        await message.reply(f"Player `{args[0]}` not found.")
        return

    try:
        stats = data.raw_players.stats(player["player_id"], GameID.CS2)
    except Exception:
        stats = None

    await message.channel.send(embed=build_faceit_embed(player, stats))
