from typing import Union, Coroutine, Optional, List, Dict, Any, Callable
from interactions import (
    ApplicationCommandType,
    Client,
    Guild,
    Option,
    InteractionException,
    ApplicationCommand,
    OptionType,
)
from interactions.decor import command


class Subcommand:
    def __init__(
        self,
        name: str,
        description: str,
        coro: Coroutine,
        options: List[Option] = None,
    ):
        self.name: str = name
        self.description: str = description
        self.coro: Coroutine = coro
        self.options: List[Option] = options
        self._options: Option = Option(
            type=OptionType.SUB_COMMAND,
            name=name,
            description=description,
            options=options,
        )


class Group:
    def __init__(
        self, group: str, description: str, subcommand: Optional[Subcommand] = None
    ):
        self.group: str = group
        self.description: str = description
        self.subcommands: List[Subcommand] = [] if not subcommand else [subcommand]

    @property
    def _options(self) -> Option:
        return Option(
            type=OptionType.SUB_COMMAND_GROUP,
            name=self.group,
            description=self.description,
            options=[subcommand._options for subcommand in self.subcommands]
            if self.subcommands
            else None,
        )


class SubcommandSetup:
    def __init__(self, client: Client, base: str):
        self.client: Client = client
        self.base: str = base
        self.groups: Dict[str, Group] = {}
        self.subcommands: Dict[str, Subcommand] = {}

        self.scope: Union[int, Guild, List[int], List[Guild]] = None
        self.default_permission: bool = None
        self.description: str = None

    def subcommand(
        self,
        *,
        group: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        default_permission: Optional[bool] = None,
        options: Optional[List[Option]] = None,
    ):
        def decorator(coro: Coroutine):
            if not name:
                raise InteractionException(
                    11, message="Your command must have a base and name."
                )

            if not description:
                raise InteractionException(
                    11, message="Chat-input commands must have a description."
                )

            if not len(coro.__code__.co_varnames):
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )
            if options and (len(coro.__code__.co_varnames) + 1) < len(options):
                raise InteractionException(
                    11,
                    message="You must have the same amount of arguments as the options of the command.",
                )
            if not self.scope:
                self.scope = scope
            if not self.default_permission:
                self.default_permission = default_permission
            if not self.description:
                self.description = description

            if group:
                if group not in self.groups:
                    self.groups[group] = Group(
                        group,
                        description,
                        subcommand=Subcommand(name, description, coro, options),
                    )
                else:
                    subcommands = self.groups[group].subcommands
                    subcommands.append(Subcommand(name, description, coro, options))
            else:
                self.subcommands[name] = Subcommand(name, description, coro, options)

            return coro

        return decorator

    def finish(self):
        options = (
            [group._options for group in self.groups.values()]
            + [subcommand._options for subcommand in self.subcommands.values()]
        ) or None
        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.description,
            scope=self.scope,
            options=options,
        )

        if self.client.automate_sync:
            [
                self.client.loop.run_until_complete(self.client.synchronize(command))
                for command in commands
            ]

        async def inner(ctx, *args, sub_command_group=None, sub_command=None, **kwargs):
            if sub_command_group:
                group = self.groups[sub_command_group]
                for subcommand in group.subcommands:
                    if subcommand.name == sub_command:
                        break
            else:
                subcommand = self.subcommands[sub_command]

            original_coro = subcommand.coro
            return await original_coro(ctx, *args, **kwargs)

        return self.client.event(inner, name=f"command_{self.base}")


def base(self: Client, base: str):
    return SubcommandSetup(self, base)
