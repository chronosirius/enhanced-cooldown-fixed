from inspect import getdoc, signature
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.decor import command

from interactions import (
    MISSING,
    ApplicationCommand,
    ApplicationCommandType,
    Client,
    Extension,
    Guild,
    InteractionException,
    Option,
    OptionType,
)

from ._logging import get_logger
from .command_models import EnhancedOption, parameters_to_options

log = get_logger("subcommand")


class Subcommand:
    """
    A class that represents a subcommand.

    DO NOT INITIALIZE THIS CLASS DIRECTLY.

    Parameters:

    * `name: str`: The name of the subcommand.
    * `description: str`: The description of the subcommand.
    * `coro: Coroutine`: The coroutine to run when the subcommand is called.
    * `options: dict`: The options of the subcommand.

    Attributes other than above:

    * `_options: Option`: The subcommand as an `Option`.
    """

    def __init__(
        self,
        name: str,
        description: str,
        coro: Coroutine,
        options: List[Option] = MISSING,
    ):
        log.debug(f"Subcommand.__init__: {name=}")
        self.name: str = name
        self.description: str = description
        self.coro: Coroutine = coro
        self.options: List[Option] = options
        if options is MISSING:
            self._options: Option = Option(
                type=OptionType.SUB_COMMAND,
                name=name,
                description=description,
            )
        else:
            self._options: Option = Option(
                type=OptionType.SUB_COMMAND,
                name=name,
                description=description,
                options=options,
            )


class Group:
    """
    A class that represents a subcommand group.

    DO NOT INITIALIZE THIS CLASS DIRECTLY.

    Parameters:

    * `group: str`: The name of the subcommand group.
    * `description: str`: The description of the subcommand group.
    * `subcommand: Subcommand`: The initial subcommand in the group.

    Properties:

    * `_options: Option`: The subcommand group as an `Option`.
    """

    def __init__(self, group: str, description: str, subcommand: Subcommand):
        log.debug(f"Group.__init__: {group=}, {subcommand=}")
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
    A class you get when using `base_var = client.base("base_name", ...)`

    Use this class to create subcommands by using the `@base_name.subcommand(...)` decorator.

    Parameters:

    * `(?)client: Client`: The client that the subcommand belongs to. *Not required if you load the extension.*
    * `base: str`: The base name of the subcommand.
    * `?description: str`: The description of the subcommand. Defaults to `"No description"`.
    * `?scope: int | Guild | list[int] | list[Guild]`: The scope of the subcommand.
    * `?default_permission: bool`: The default permission of the subcommand.
    """

    def __init__(
        self,
        client: Client,
        base: str,
        description: Optional[str] = "No description",
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        default_permission: Optional[bool] = None,
    ):
        log.debug(f"SubcommandSetup.__init__: {base=}")
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

        `name` is required.

        ```py
        @base_var.subcommand(
            group="group_name",
            name="subcommand_name",
            description="subcommand_description",
            options=[...]
        )
        ```

        Parameters:

        * `?group: str`: The group of the subcommand.
        * `name: str`: The name of the subcommand.
        * `?description: str`: The description of the subcommand.
        * `?options: list[Option]`: The options of the subcommand.
        """
        log.debug(f"SubcommandSetup.subcommand: {self.base=}, {group=}, {name=}")

        def decorator(coro: Coroutine) -> Coroutine:
            _name = coro.__name__ if name is MISSING else name
            _description = (
                (getdoc(coro) or "No description") if description is MISSING else description
            ).split("\n")[0]
            if len(_description) > 100:
                raise ValueError("Description must be less than 100 characters.")

            params = signature(coro).parameters
            if options is MISSING and any(
                isinstance(param.annotation, EnhancedOption) for _, param in params.items()
            ):
                _options = parameters_to_options(params)
            else:
                _options = options

            if not params:
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            if group is MISSING:
                self.subcommands[_name] = Subcommand(_name, _description, coro, _options)
            elif group not in self.groups:
                self.groups[group] = Group(
                    group,
                    description,
                    subcommand=Subcommand(_name, _description, coro, _options),
                )
            else:
                self.groups[group].subcommands.append(
                    Subcommand(_name, _description, coro, _options)
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
        log.debug(f"SubcommandSetup.finish: {self.base=}")
        group_options = [group._options for group in self.groups.values()] if self.groups else []
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
                    self.client._loop.run_until_complete(self.client._synchronize(command))
                    for command in commands
                ]

        if self.scope is not MISSING:
            if isinstance(self.scope, list):
                [self.client._scopes.add(_ if isinstance(_, int) else _.id) for _ in self.scope]
            else:
                self.client._scopes.add(
                    self.scope if isinstance(self.scope, int) else self.scope.id
                )

        async def inner(ctx, *args, sub_command_group=None, sub_command=None, **kwargs) -> None:
            if sub_command_group:
                group = self.groups[sub_command_group]
                subcommand = next(
                    (sub for sub in group.subcommands if sub.name == sub_command), None
                )
            else:
                subcommand = self.subcommands[sub_command]

            return await subcommand.coro(ctx, *args, **kwargs)

        return self.client.event(inner, name=f"command_{self.base}")


class ExternalSubcommandSetup(SubcommandSetup):
    """
    A class you get when using `base_var = extension_base("base_name", ...)`

    Use this class to create subcommands by using the `@base_name.subcommand(...)` decorator.

    Parameters:

    * `base: str`: The base name of the subcommand.
    * `?description: str`: The description of the subcommand.
    * `?scope: int | Guild | list[int] | list[Guild]`: The scope of the subcommand.
    * `?default_permission: bool`: The default permission of the subcommand.
    """

    def __init__(
        self,
        base: str,
        description: Optional[str] = "No description",
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        default_permission: Optional[bool] = MISSING,
    ):
        log.debug(f"ExternalSubcommandSetup.__init__: {base=}")
        super().__init__(
            client=None,
            base=base,
            description=description,
            scope=scope,
            default_permission=default_permission,
        )
        self.raw_commands = None
        self.full_command = None
        self.__self = None

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

        `name` is required.

        ```py
        @base_var.subcommand(
            group="group_name",
            name="subcommand_name",
            description="subcommand_description",
            options=[...]
        )
        ```

        Parameters:

        * `?group: str`: The group of the subcommand.
        * `name: str`: The name of the subcommand.
        * `?description: str`: The description of the subcommand.
        * `?options: list[Option]`: The options of the subcommand.
        """
        log.debug(f"ExternalSubcommandSetup.subcommand: {self.base=}, {group=}, {name=}")

        def decorator(coro: Coroutine) -> Coroutine:
            coro.__subcommand__ = True
            coro.__base__ = self.base
            coro.__data__ = self

            _name = coro.__name__ if name is MISSING else name
            _description = (
                (getdoc(coro) or "No description") if description is MISSING else description
            ).split("\n")[0]
            if len(_description) > 100:
                raise ValueError("Description must be less than 100 characters.")

            params = signature(coro).parameters
            if options is MISSING and any(
                isinstance(param.annotation, EnhancedOption) for _, param in params.items()
            ):
                _options = parameters_to_options(params)
            else:
                _options = options

            if not params:
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            if group is MISSING:
                self.subcommands[_name] = Subcommand(_name, _description, coro, _options)
            elif group not in self.groups:
                self.groups[group] = Group(
                    group,
                    description,
                    subcommand=Subcommand(_name, _description, coro, _options),
                )
            else:
                self.groups[group].subcommands.append(
                    Subcommand(_name, _description, coro, _options)
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
        log.debug(f"ExternalSubcommandSetup.finish: {self.base=}")
        group_options = [group._options for group in self.groups.values()] if self.groups else []
        subcommand_options = (
            [subcommand._options for subcommand in self.subcommands.values()]
            if self.subcommands
            else []
        )
        options = (group_options + subcommand_options) or MISSING
        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.description,
            scope=self.scope,
            options=options,
        )
        self.raw_commands = commands

    async def inner(self, ctx, *args, sub_command_group=None, sub_command=None, **kwargs) -> None:
        if sub_command_group:
            group = self.groups[sub_command_group]
            subcommand = next((sub for sub in group.subcommands if sub.name == sub_command), None)
        else:
            subcommand = self.subcommands[sub_command]

        return await subcommand.coro(self.__self, ctx, *args, **kwargs)

    def set_self(self, __self: Extension) -> None:
        """
        Allows ability to access Extension attributes

        :param Extension __self: The extension
        """
        self.__self = __self


def subcommand_base(
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
    # or
    from interactions.ext.enhanced import subcommand_base
    base_name = subcommand_base(
        client,
        "base_name",
        description="Description of the base",
        scope=123456789,
        default_permission=True
    )
    ```

    Parameters:

    * `(?)self: Client`: The client that the base belongs to. *Not needed if you load the extension and use `client.base(...)`.*
    * `base: str`: The base name of the base.
    * `?description: str`: The description of the base.
    * `?scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
    * `?default_permission: bool`: The default permission of the base.
    """
    log.debug(f"base: {base=}")
    return SubcommandSetup(self, base, description, scope, default_permission)


def ext_subcommand_base(
    base: str,
    *,
    description: Optional[str] = "No description",
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
) -> ExternalSubcommandSetup:
    """
    Use this function to initialize a base for future subcommands inside extensions.

    Kwargs are optional.

    ```py
    base_name = ext_subcommand_base(
        "base_name",
        description="Description of the base",
        scope=123456789,
        default_permission=True
    )
    ```

    Parameters:

    * `base: str`: The base name of the base.
    * `?description: str`: The description of the base.
    * `?scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
    * `?default_permission: bool`: The default permission of the base.
    """
    log.debug(f"extension_base: {base=}")
    return ExternalSubcommandSetup(base, description, scope, default_permission)
