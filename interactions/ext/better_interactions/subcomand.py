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


def subcommand(
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
        if self.websocket.dispatch.events.get(f"command_{base}"):
            print(self.websocket.dispatch.events.get(f"command_{base}"))
        elif self.automate_sync:
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


class SubCommand:
    def __init__(self, base: str):
        self.base = base
        self.group_names: Dict[str, dict] = {}
        self.description: str = None

        self.scope = None
        self.default_permission = None
        self.coros = {}

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
            if options:
                if (len(coro.__code__.co_varnames) + 1) < len(options):
                    raise InteractionException(
                        11,
                        message="You must have the same amount of arguments as the options of the command.",
                    )
            try:
                self.group_names[group] = {}
            except:
                pass

            def try_except(key, value):
                try:
                    self.group_names[group][key].append(value)
                except KeyError:
                    self.group_names[group][key] = [value]

            try_except("names", name)
            try_except("descriptions", description)
            try_except("options", options)
            coro.__origin__ = f"{self.base}_{group}_{name}"

            self.description = description
            self.scope = scope
            self.default_permission = default_permission
            self.coros[f"{self.base}_{group}_{name}"] = coro

            return coro

        return decorator

    @logger.catch
    def finish(self, client: Client):
        all_options: List[Option] = []
        for group in self.group_names:
            group_options = []
            _names = self.group_names[group]["names"]
            _descriptions = self.group_names[group]["descriptions"]
            _options = self.group_names[group]["options"]
            for n, d, o in zip(_names, _descriptions, _options):
                group_options.append(
                    Option(
                        type=OptionType.SUB_COMMAND, name=n, description=d, options=o
                    )
                )
            all_options.append(
                Option(
                    type=OptionType.SUB_COMMAND_GROUP,
                    name=group,
                    description=self.group_names[group]["descriptions"][0],
                    options=group_options,
                )
            )

        # for group, name, description, option in zip(
        #     self.groups, self.names, self.descriptions, self.options
        # ):
        #     if group:
        #         options.append(
        #             Option(
        #                 type=OptionType.SUB_COMMAND_GROUP,
        #                 name=group,
        #                 description=description,
        #                 options=[
        #                     Option(
        #                         type=OptionType.SUB_COMMAND,
        #                         name=n,
        #                         description=description,
        #                         options=o,
        #                     )
        #                     for n, o in zip(name, option)
        #                 ],
        #             )
        #         )
        #     else:
        #         options.append(
        #             Option(
        #                 type=OptionType.SUB_COMMAND,
        #                 name=name,
        #                 description=description,
        #                 options=option,
        #             )
        #         )
        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.group_names[group]["descriptions"][0],
            scope=self.scope,
            options=all_options,
            default_permission=self.default_permission,
        )
        # print(commands[0]._json)
        print(all_options)
        if client.automate_sync:
            [
                client.loop.run_until_complete(client.synchronize(command))
                for command in commands
            ]

        async def inner(ctx, *args, sub_command_group=None, sub_command=None, **kwargs):
            try:
                origin = f"{self.base}_{sub_command_group}_{sub_command}"
                return await self.coros[origin](ctx, *args, **kwargs)
            except Exception:
                raise

        return client.event(inner, name=f"command_{self.base}")


def base(self, base: str):
    return SubCommand(base)
