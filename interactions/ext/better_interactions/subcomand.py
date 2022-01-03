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
from loguru import logger


def _subcommand(
    self,
    *,
    base: Optional[str] = None,
    subcommand_group: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
    options: Optional[List[Option]] = None,
) -> Callable[..., Any]:
    """
    A decorator for registering a subcommand group to the Discord API,
    as well as being able to listen for ``INTERACTION_CREATE`` dispatched
    gateway events.
    The structure of a subcommand:
    .. code-block:: python
        @subcommand(
            base="base",
            subcommand_group="sub_command_group",
            name="sub_command",
            description="this is a subcommand group.",
        )
        async def subcommand_name(ctx, sub_command_group, sub_command):  # the last 2 are required to avoid error
            ...
    The ``scope`` kwarg field may also be used to designate the command in question
    applicable to a guild or set of guilds.
    The ``subcommand_group`` kwarg is optional.
    :param base: The base of the application command. This *is* required but kept optional to follow kwarg rules.
    :type base: Optional[str]
    :param subcommand_group: The subcommand group of the application command. This is optional.
    :type subcommand_group: Optional[str]
    :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
    :type name: Optional[str]
    :param description: The description of the application command. This *is* required but kept optional to follow kwarg rules.
    :type description: Optional[str]
    :param scope?: The "scope"/applicable guilds the application command applies to.
    :type scope: Optional[Union[int, Guild, List[int], List[Guild]]]
    :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
    :type default_permission: Optional[bool]
    :param options?: The options of the application command.
    :type options: Optional[List[Option]]
    :return: A callable response.
    :rtype: Callable[..., Any]
    """

    def decorator(coro: Coroutine) -> Callable[..., Any]:
        if not base and name:
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
        if options:
            if (len(coro.__code__.co_varnames) + 1) < len(options):
                raise InteractionException(
                    11,
                    message="You must have the same amount of arguments as the options of the command.",
                )

        if subcommand_group:
            commands: List[ApplicationCommand] = command(
                type=ApplicationCommandType.CHAT_INPUT,
                name=base,
                description=description,
                scope=scope,
                options=[
                    Option(
                        type=OptionType.SUB_COMMAND_GROUP,
                        name=subcommand_group,
                        description=description,
                        options=[
                            Option(
                                type=OptionType.SUB_COMMAND,
                                name=name,
                                description=description,
                                options=options,
                            )
                        ],
                    )
                ],
                default_permission=default_permission,
            )
        else:
            commands: List[ApplicationCommand] = command(
                type=ApplicationCommandType.CHAT_INPUT,
                name=base,
                description=description,
                scope=scope,
                options=[
                    Option(
                        type=OptionType.SUB_COMMAND,
                        name=name,
                        description=description,
                        options=options,
                    )
                ],
                default_permission=default_permission,
            )
        if self.automate_sync:
            [
                self.loop.run_until_complete(self.synchronize(command))
                for command in commands
            ]

        async def inner(ctx, *args, sub_command_group=None, sub_command=None, **kwargs):
            if sub_command_group == sub_command_group and sub_command == name:
                return await coro(ctx, *args, **kwargs)

        return self.event(inner, name=f"command_{base}")

    return decorator


# START OF NEW CODE


class Group:
    def __init__(
        self,
        group: str,
        description: str,
    ):
        self.group: str = group
        self.description: str = description
        self.subcommands: List[Subcommand] = []
        self._options: Option = Option(
            type=OptionType.SUB_COMMAND_GROUP,
            name=group,
            description=description,
            options=[subcommand._options for subcommand in self.subcommands]
            if self.subcommands
            else None,
        )


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
        print("subcommand called")

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
            if options:
                if (len(coro.__code__.co_varnames) + 1) < len(options):
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
                    self.groups[group] = Group(group, description)
                self.groups[group].subcommands.append(
                    Subcommand(name, description, coro, options)
                )
            else:
                self.subcommands[name] = Subcommand(name, description, coro, options)

            return coro

        return decorator

    # @logger.catch
    def finish(self):
        print("finish called")
        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.description,
            scope=self.scope,
            options=[group._options for group in self.groups.values()].extend(
                subcommand._options for subcommand in self.subcommands.values()
            ),
        )
        print(commands[0]._json)

        if self.client.automate_sync:
            [
                self.client.loop.run_until_complete(self.synchronize(command))
                for command in commands
            ]

        async def inner(ctx, *args, sub_command_group=None, sub_command=None, **kwargs):
            if sub_command_group:
                group = self.groups[sub_command_group]
                subcommand = group.subcommands[sub_command]
                original_coro = subcommand.coro
                return await original_coro(ctx, *args, **kwargs)
            else:
                subcommand = self.subcommands[sub_command]
                original_coro = subcommand.coro
                return await original_coro(ctx, *args, **kwargs)

        return self.client.event(inner, name=f"command_{self.base}")


def base(self: Client, base: str):
    return SubcommandSetup(self, base)
