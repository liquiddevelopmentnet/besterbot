from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import Callable, Awaitable

from discord import Message

CommandHandler = Callable[[Message, list[str]], Awaitable[None]]

_registry: dict[str, Command] = {}


@dataclass
class Command:
    name: str
    handler: CommandHandler
    description: str = ""
    usage: str = ""
    category: str = ""


def command(
    name: str,
    *,
    description: str = "",
    usage: str = "",
    category: str = "",
) -> Callable[[CommandHandler], CommandHandler]:
    """Decorator that registers a command handler."""

    def decorator(func: CommandHandler) -> CommandHandler:
        _registry[name] = Command(
            name=name,
            handler=func,
            description=description,
            usage=usage,
            category=category,
        )
        return func

    return decorator


def get_command(name: str) -> Command | None:
    return _registry.get(name)


def get_all_commands() -> dict[str, Command]:
    return dict(_registry)


def get_commands_by_category() -> dict[str, list[Command]]:
    categories: dict[str, list[Command]] = {}
    for cmd in _registry.values():
        categories.setdefault(cmd.category, []).append(cmd)
    return categories


def load_commands() -> None:
    """Import all subpackages of bot.commands to trigger @command decorators."""
    import bot.commands as pkg

    for _, module_name, is_pkg in pkgutil.walk_packages(
        pkg.__path__, prefix=pkg.__name__ + "."
    ):
        importlib.import_module(module_name)
