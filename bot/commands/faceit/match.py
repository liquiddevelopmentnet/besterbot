import discord
from discord import Message
from datetime import datetime, timezone
from faceit.exceptions import APIError

from bot.commands import command
from bot.commands.faceit.client import data, LEVEL_BARS, get_ongoing_match
from bot.strings import FaceitMatch as S


def format_elapsed(started_at: int) -> str:
    delta = int(datetime.now(timezone.utc).timestamp() - started_at)
    h, rem = divmod(delta, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"


def build_team_embed(team: dict, label: str, target_id: str, color: int) -> discord.Embed:
    embed = discord.Embed(title=f"{label}  —  {team.get('nickname', '?')}", color=color)

    lines = []
    for p in team.get("players", []):
        lvl = p.get("skill_level", "?")
        bar = LEVEL_BARS.get(lvl, "??????????")
        nick = p.get("nickname", "?")
        url = p.get("faceit_url", "").replace("{lang}", "en")
        pointer = " ◄" if p.get("player_id") == target_id else ""
        lines.append(f"[{nick}]({url})  `lv.{lvl}`{pointer}")

    embed.description = "\n".join(lines) or "—"
    return embed


def build_match_overview_embed(match: dict, player_name: str, started_at: int) -> discord.Embed:
    voting = match.get("voting") or {}
    map_pick = (voting.get("map") or {}).get("pick") or []
    map_name = map_pick[0].replace("de_", "").capitalize() if map_pick else "Unknown"

    embed = discord.Embed(
        title=S.LIVE_TITLE.format(name=player_name),
        url=match.get("faceit_url", "").replace("{lang}", "en"),
        color=0xFF5500,
        description=(
            f"**{match.get('competition_name', '—')}** ·  "
            f"{match.get('game_mode', '—')}  ·  "
            f"Region: `{match.get('region', '—')}`"
        ),
    )

    embed.add_field(name=S.MAP_FIELD,     value=f"`{map_name}`",                      inline=True)
    embed.add_field(name=S.ELAPSED_FIELD, value=format_elapsed(started_at),           inline=True)
    embed.add_field(name=S.MATCH_ID_FIELD, value=f"`{match.get('match_id', '—')}`",   inline=True)

    return embed


@command(
    "match",
    description=S.DESCRIPTION,
    usage="f.match <name>",
    category="Faceit",
)
async def match_command(message: Message, args: list[str]):
    if len(args) != 1:
        await message.reply("Usage: `f.match <name>`")
        return

    try:
        player = data.raw_players.get(args[0])
    except APIError:
        await message.reply(S.PLAYER_NOT_FOUND.format(name=args[0]))
        return

    player_id = player["player_id"]
    player_name = player["nickname"]

    match = get_ongoing_match(player_id)
    if not match:
        await message.reply(S.NOT_IN_MATCH.format(name=player_name))
        return

    started_at = match.get("started_at", 0)
    teams = match.get("teams", {})
    faction1 = teams.get("faction1", {})
    faction2 = teams.get("faction2", {})

    f1_ids = {p["player_id"] for p in faction1.get("players", [])}
    if player_id in f1_ids:
        our_team, their_team = faction1, faction2
    else:
        our_team, their_team = faction2, faction1

    embeds = [
        build_match_overview_embed(match, player_name, started_at),
        build_team_embed(our_team, S.OUR_TEAM_LABEL, player_id, 0x57F287),
        build_team_embed(their_team, S.OPPONENTS_LABEL, player_id, 0xED4245),
    ]

    await message.channel.send(embeds=embeds)
