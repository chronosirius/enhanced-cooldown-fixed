from interactions import (
    ApplicationCommand,
    ApplicationCommandType,
    Client,
    Extension,
    Guild,
    InteractionException,
    Option,
    OptionType,
    MISSING,
)
from interactions.decor import command
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union
from inspect import getdoc, signature, _empty

from .command_models import BetterOption


class Subcommand:
    def __init__(
        self,
        name: str,
        description: str,
        coro: Coroutine,
        options: List[Option] = None,
    ):
        """
        A class that represents a subcommand.

        DO NOT INITIALIZE THIS CLASS DIRECTLY.

        :param str name: The name of the subcommand.
        :param str description: The description of the subcommand.
        :param Coroutine coro: The coroutine that will be executed when the subcommand is called.
        :param List[Option] options: The options of the subcommand.
        """
        self.name: str = name
        self.description: str = description
        self.coro: Coroutine = coro
        self.options: List[Option] = options
        if options:
            self._options: Option = Option(
                type=OptionType.SUB_COMMAND,
                name=name,
                description=description,
                options=options,
            )
        else:
            self._options: Option = Option(
                type=OptionType.SUB_COMMAND,
                name=name,
                description=description,
            )


class Group:
    def __init__(self, group: str, description: str, subcommand: Subcommand):
        """
        A class that represents a subcommand group.

        DO NOT INITIALIZE THIS CLASS DIRECTLY.

        :param str group: The name of the subcommand group.
        :param str description: The description of the subcommand group.
        :param Subcommand subcommand: The initial subcommand.
        """
        self.group: str = group
        self.description: str = description
        self.subcommands: List[Subcommand] = [subcommand]

    @property
    def _options(self) -> Option:
        """
        Returns the subcommand group as an option.

        The subcommands of the group are in the ``options=`` field of the option.
        """
        return Option(
            type=OptionType.SUB_COMMAND_GROUP,
            name=self.group,
            description=self.description,
            options=[subcommand._options for subcommand in self.subcommands],
        )


class SubcommandSetup:
    """
    A class you get when using ``base_var = client.base("base_name", ...)``

    Use this class to create subcommands by using the ``@base_name.subcommand(...)`` decorator.

    :param Client client: The client that the subcommand belongs to.
    :param str base: The base name of the subcommand.
    :param str description: The description of the subcommand.
    :param Union[int, Guild, List[int], List[Guild]] scope: The scope of the subcommand.
    :param bool default_permission: The default permission of the subcommand.
    """

    def __init__(
        self,
        client: Client,
        base: str,
        description: Optional[str] = "No description",
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        default_permission: Optional[bool] = None,
    ):
        self.client: Client = client
        self.base: str = base
        self.description: str = description
        self.scope: Union[int, Guild, List[int], List[Guild]] = scope
        self.default_permission: bool = default_permission

        self.groups: Dict[str, Group] = {}
        self.subcommands: Dict[str, Subcommand] = {}

    def subcommand(
        self,
        *,
        group: Optional[str] = MISSING,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
    ) -> Callable[..., Any]:
        """
        Decorator that creates a subcommand for the corresponding base.

        All arguments are optional.
        ```py
        @base_var.subcommand(
            group="group_name",
            name="subcommand_name",
            description="subcommand_description",
            options=[...]
        )
        ```
        :param str group: The group of the subcommand.
        :param str name: The name of the subcommand.
        :param str description: The description of the subcommand.
        :param List[Option] options: The options of the subcommand.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            _name = coro.__name__ if name is MISSING else name
            _description = (
                (getdoc(coro) or "No description")
                if description is MISSING
                else description
            )
            _options = []

            params = signature(coro).parameters

            if not len(coro.__code__.co_varnames):
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            if options is MISSING and len(params) > 1:
                context = True
                for __name, param in params.items():
                    if context:
                        context = False
                        continue
                    typehint: BetterOption = param.annotation
                    if typehint is _empty or not isinstance(typehint, BetterOption):
                        raise TypeError(
                            "You must typehint with `BetterOption` or specify `options=[]` in the decorator!"
                        )
                    _options.append(
                        Option(
                            type=typehint.type,
                            name=__name if not typehint.name else typehint.name,
                            description=typehint.description,
                            required=param.default is _empty,
                            choices=typehint.choices,
                            channel_types=typehint.channel_types,
                            min_value=typehint.min_value,
                            max_value=typehint.max_value,
                            autocomplete=typehint.autocomplete,
                            focused=typehint.focused,
                            value=typehint.value,
                        )
                    )

            _options = _options if options is MISSING and len(params) > 1 else options
            _options = None if _options is MISSING else _options

            if group:
                if group not in self.groups:
                    self.groups[group] = Group(
                        group,
                        description,
                        subcommand=Subcommand(_name, _description, coro, _options),
                    )
                else:
                    subcommands = self.groups[group].subcommands
                    subcommands.append(Subcommand(_name, _description, coro, _options))
            else:
                self.subcommands[_name] = Subcommand(
                    _name, _description, coro, _options
                )

            return coro

        return decorator

    def finish(self) -> Callable[..., Any]:
        """
        Function that finishes the setup of the base command.

        Use this when you are done creating subcommands for a specified base.
        ```py
        base_var.finish()
        ```
        """
        group_options = (
            [group._options for group in self.groups.values()] if self.groups else []
        )
        subcommand_options = (
            [subcommand._options for subcommand in self.subcommands.values()]
            if self.subcommands
            else []
        )
        options = (group_options + subcommand_options) or None
        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.description,
            scope=self.scope,
            options=options,
        )

        if self.client._automate_sync:
            if self.client._loop.is_running():
                [
                    self.client._loop.create_task(self.client._synchronize(command))
                    for command in commands
                ]
            else:
                [
                    self.client._loop.run_until_complete(
                        self.client._synchronize(command)
                    )
                    for command in commands
                ]

        if self.scope is not None:
            if isinstance(self.scope, list):
                [
                    self.client._scopes.add(_ if isinstance(_, int) else _.id)
                    for _ in self.scope
                ]
            else:
                self.client._scopes.add(
                    self.scope if isinstance(self.scope, int) else self.scope.id
                )

        async def inner(
            ctx, *args, sub_command_group=None, sub_command=None, **kwargs
        ) -> None:
            if sub_command_group:
                group = self.groups[sub_command_group]
                subcommand = next(
                    (sub for sub in group.subcommands if sub.name == sub_command), None
                )
            else:
                subcommand = self.subcommands[sub_command]

            return await subcommand.coro(ctx, *args, **kwargs)

        return self.client.event(inner, name=f"command_{self.base}")


class NonSynchronizedCommand:
    """
    A class that represents a non-synchronized command inside extensions.

    DO NOT INITIALIZE THIS CLASS DIRECTLY.

    :param str commands: The raw commands data.
    :param str description: The base of the command.
    """

    def __init__(self, commands: List[ApplicationCommand], base: str = None):
        self.__need_sync__ = True
        self.commands = commands
        self.base = base


class ExternalSubcommandSetup(SubcommandSetup):
    """
    A class you get when using ``base_var = extension_base("base_name", ...)``

    Use this class to create subcommands by using the ``@base_name.subcommand(...)`` decorator.

    :param str base: The base name of the subcommand.
    :param str description: The description of the subcommand.
    :param Union[int, Guild, List[int], List[Guild]] scope: The scope of the subcommand.
    :param bool default_permission: The default permission of the subcommand.
    """

    def __init__(
        self,
        base: str,
        description: Optional[str] = "No description",
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        default_permission: Optional[bool] = None,
    ):
        super().__init__(
            client=None,
            base=base,
            description=description,
            scope=scope,
            default_permission=default_permission,
        )
        self.raw_commands = None
        self.full_command = None

    def subcommand(
        self,
        *,
        group: Optional[str] = MISSING,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
    ) -> Callable[..., Any]:
        """
        Decorator that creates a subcommand for the corresponding base.

        All arguments are optional.
        ```py
        @base_var.subcommand(
            group="group_name",
            name="subcommand_name",
            description="subcommand_description",
            options=[...]
        )
        ```
        :param str group: The group of the subcommand.
        :param str name: The name of the subcommand.
        :param str description: The description of the subcommand.
        :param List[Option] options: The options of the subcommand.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            coro.__subcommand__ = True
            coro.__base__ = self.base
            coro.__data__ = self

            super(ExternalSubcommandSetup, self).subcommand(
                group=group, name=name, description=description, options=options
            )

            return coro

        return decorator

    def finish(self) -> Callable[..., Any]:
        """
        Function that finishes the setup of the base command inside extensions.

        Use this when you are done creating subcommands for a specified base.
        ```py
        base_var.finish()
        ```
        """
        group_options = (
            [group._options for group in self.groups.values()] if self.groups else []
        )
        subcommand_options = (
            [subcommand._options for subcommand in self.subcommands.values()]
            if self.subcommands
            else []
        )
        options = (group_options + subcommand_options) or None
        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.description,
            scope=self.scope,
            options=options,
        )
        self.raw_commands = commands
        self.full_command = NonSynchronizedCommand(commands, self.base)

    def inner(
        self, ctx, *args, sub_command_group=None, sub_command=None, **kwargs
    ) -> None:
        if sub_command_group:
            group = self.groups[sub_command_group]
            subcommand = next(
                (sub for sub in group.subcommands if sub.name == sub_command), None
            )

        else:
            subcommand = self.subcommands[sub_command]

        return subcommand.coro(self, ctx, *args, **kwargs)


def base(
    self: Client,
    base: str,
    *,
    description: Optional[str] = "No description",
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
) -> SubcommandSetup:
    """
    Use this function to initialize a base for future subcommands.
    Kwargs are optional.

    To use this function without loading the extension, pass in the client as the first argument.
    ```py
    base_name = client.base(
        "base_name",
        description="Description of the base",
        scope=123456789,
        default_permission=True
    )
    ```
    :param Client self: The client. This is only used if you do not load the extension.
    :param str base: The base name.
    :param str description: The description of the base.
    :param Union[int, Guild, List[int], List[Guild]] scope: The scope of the base.
    :param bool default_permission: The default permission of the base.
    """
    return SubcommandSetup(self, base, description, scope, default_permission)


def extension_base(
    base: str,
    *,
    description: Optional[str] = "No description",
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
) -> ExternalSubcommandSetup:
    """
    Use this function to initialize a base for future subcommands inside of extensions.
    Kwargs are optional.

    ```py
    base_name = extension_base(
        "base_name",
        description="Description of the base",
        scope=123456789,
        default_permission=True
    )
    ```
    :param str base: The base name.
    :param str description: The description of the base.
    :param Union[int, Guild, List[int], List[Guild]] scope: The scope of the base.
    :param bool default_permission: The default permission of the base.
    """
    return ExternalSubcommandSetup(base, description, scope, default_permission)
