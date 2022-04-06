from inspect import getdoc, signature
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.client.decor import command
from typing_extensions import _AnnotatedAlias

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
    Snowflake,
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


class GroupSetup:
    """
    A class that allows a shortcut to creating a group subcommand in the original `SubcommandSetup`.

    ```py
    base_var: SubcommandSetup = client.subcommand_base("base_name", ...)
    group_var: GroupSetup = base_var.group("group_name")

    group_var.subcommand(...)
    async def group_subcommand(ctx, ...):
        ...
    ```

    Parameters:

    * `group: str`: The name of the subcommand group.
    * `subcommand_setup: SubcommandSetup`: The `SubcommandSetup` to add the group subcommand to.
    """

    def __init__(self, group: str, subcommand_setup: "SubcommandSetup"):
        log.debug(f"GroupSetup.__init__: {group=}, {subcommand_setup=}")
        self.group: str = group
        self.subcommand_setup: "SubcommandSetup" = subcommand_setup

    def subcommand(
        self,
        _coro: Optional[Coroutine] = MISSING,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
    ) -> Callable[..., Any]:
        """
        Creates a subcommand with the specified group and parameters.

        ```py
        base_var: SubcommandSetup = client.subcommand_base("base_name", ...)
        group_var: GroupSetup = base_var.group("group_name")

        group_var.subcommand(...)
        async def group_subcommand(ctx, ...):
            ...
        ```

        Parameters:

        * `?name: str`: The name of the subcommand.
        * `?description: str`: The description of the subcommand.
        * `?options: List[Option]`: The options of the subcommand.
        """

        def decorator(coro):
            self.subcommand_setup.subcommand(
                group=self.group,
                name=name,
                description=description,
                options=options,
            )(coro)
            return coro

        if _coro is not MISSING:
            return decorator(_coro)
        return decorator


class SubcommandSetup:
    """
    A class you get when using `base_var = client.subcommand_base("base_name", ...)`

    Use this class to create subcommands by using the `@base_name.subcommand(...)` decorator.

    Parameters:

    * `(?)client: Client`: The client that the subcommand belongs to. *Not required if you load the extension.*
    * `base: str`: The base name of the subcommand.
    * `?description: str`: The description of the subcommand. Defaults to `"No description"`.
    * `?scope: int | Guild | list[int] | list[Guild]`: The scope of the subcommand.
    * `?default_permission: bool`: The default permission of the subcommand.
    * `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.
    """

    def __init__(
        self,
        client: Client,
        base: str,
        description: Optional[str] = "No description",
        scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
        default_permission: Optional[bool] = MISSING,
        debug_scope: Optional[bool] = True,
    ):
        log.debug(f"SubcommandSetup.__init__: {base=}")
        self.client: Client = client
        self.base: str = base
        self.description: str = description
        self.scope: Union[int, Guild, List[int], List[Guild]] = (
            getattr(client, "__debug_scope")
            if scope is MISSING and hasattr(client, "__debug_scope") and debug_scope
            else scope
        )
        self.default_permission: bool = default_permission

        self.groups: Dict[str, Group] = {}
        self.subcommands: Dict[str, Subcommand] = {}
        self.commands: List[ApplicationCommand] = MISSING

    def group(self, group: str) -> GroupSetup:
        """
        Function to get a `GroupSetup` object, a shortcut to creating group subcommands.

        This is also in `ExternalSubcommandSetup`.

        ```py
        base_var: SubcommandSetup = client.subcommand_base("base_name", ...)
        group_var: GroupSetup = base_var.group("group_name")
        ```

        Parameters:

        * `group: str`: The name of the group.

        Returns:

        `GroupSetup`
        """
        return GroupSetup(group=group, subcommand_setup=self)

    def subcommand(
        self,
        _coro: Optional[Coroutine] = MISSING,
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
            _options = (
                getattr(coro, "__decor_options")
                if hasattr(coro, "__decor_options")
                else parameters_to_options(params)
                if options is MISSING and len(params) > 1
                else options
            )

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
                    _description,
                    subcommand=Subcommand(_name, _description, coro, _options),
                )
            else:
                self.groups[group].subcommands.append(
                    Subcommand(_name, _description, coro, _options)
                )
            return coro

        if _coro is not MISSING:
            return decorator(_coro)
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
        self.commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.description,
            scope=self.scope,
            options=options,
            default_permission=self.default_permission,
        )

        if self.client._automate_sync:
            if self.client._loop.is_running():
                [
                    self.client._loop.create_task(self.client._synchronize(command))
                    for command in self.commands
                ]
            else:
                [
                    self.client._loop.run_until_complete(self.client._synchronize(command))
                    for command in self.commands
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

    def autocomplete(self, option: str) -> Callable[..., Any]:
        """
        Decorator for building autocomplete for options in the current base.

        **IMPORTANT**: You must `base_var.finish()` before using this decorator.

        Example:

        ```py
        base = client.subcommand_base("base_name", ...)

        @base.subcommand()
        @option("auto", autocomplete=True)
        async def subcommand(ctx, auto: str):
            ...

        ...
        base.finish()

        @base.autocomplete("auto")
        async def auto_complete(ctx, user_input: str = ""):
            await ctx.populate([
                interactions.Choice(...),
                interactions.Choice(...),
                ...
            ])
        ```

        Parameters:

        * `option: str`: The option to build autocomplete for.
        """

        def decorator(coro: Coroutine) -> Callable[..., Any]:
            if self.commands is MISSING:
                raise RuntimeError(
                    "You must `base_var.finish()` the setup of the subcommands before providing autocomplete."
                )
            command: str = self.base
            _command_obj: ApplicationCommand = self.client._http.cache.interactions.get(command)
            if not _command_obj or not _command_obj.id:
                if getattr(_command_obj, "guild_id", None) or self.client._automate_sync:
                    _application_commands: List[
                        ApplicationCommand
                    ] = self.client._loop.run_until_complete(
                        self.client._http.get_application_commands(
                            application_id=self.me.id,
                            guild_id=_command_obj.guild_id
                            if hasattr(_command_obj, "guild_id")
                            else None,
                        )
                    )

                    _command_obj: ApplicationCommand = self.client._find_command(
                        _application_commands, command
                    )
                else:
                    for _scope in self.client._scopes:
                        _application_commands: List[
                            ApplicationCommand
                        ] = self.client._loop.run_until_complete(
                            self.client._http.get_application_commands(
                                application_id=self.client.me.id, guild_id=_scope
                            )
                        )
                        _command_obj: ApplicationCommand = self.client._find_command(
                            _application_commands, command
                        )
            _command: Union[Snowflake, int] = int(_command_obj.id)
            return self.client.event(coro, name=f"autocomplete_{_command}_{option}")

        return decorator


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
        self._autocomplete_options: Dict[str, Callable] = {}

    def subcommand(
        self,
        _coro: Optional[Coroutine] = MISSING,
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
            _options = (
                getattr(coro, "__decor_options")
                if hasattr(coro, "__decor_options")
                else parameters_to_options(params)
                if options is MISSING
                and len(params) > 1
                and any(
                    isinstance(param.annotation, (EnhancedOption, _AnnotatedAlias))
                    for _, param in params.items()
                )
                else options
            )

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

        if _coro is not MISSING:
            return decorator(_coro)
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
        self.commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.CHAT_INPUT,
            name=self.base,
            description=self.description,
            scope=self.scope,
            options=options,
            default_permission=self.default_permission,
        )
        self.raw_commands = self.commands

    def autocomplete(self, option: str) -> Callable[..., Any]:
        """
        Decorator for building autocomplete for options in the current base.

        **IMPORTANT**: You must `base_var.finish()` before using this decorator.

        Example:

        ```py
        base = client.subcommand_base("base_name", ...)

        @base.subcommand()
        @option("auto", autocomplete=True)
        async def subcommand(ctx, auto: str):
            ...

        ...
        base.finish()

        @base.autocomplete("auto")
        async def auto_complete(ctx, user_input: str = ""):
            await ctx.populate([
                interactions.Choice(...),
                interactions.Choice(...),
                ...
            ])
        ```

        Parameters:

        * `option: str`: The option to build autocomplete for.
        """

        def decorator(coro: Coroutine) -> Callable[..., Any]:
            if self.commands is MISSING:
                raise RuntimeError(
                    "You must `base_var.finish()` the setup of the subcommands before providing autocomplete."
                )
            self._autocomplete_options[option] = coro
            return coro

        return decorator

    def _super_autocomplete(self, client: Client):
        self.client = client
        if not self._autocomplete_options:
            return
        for option, coro in self._autocomplete_options.items():

            async def new_coro(*args, **kwargs):
                return await coro(self.__self, *args, **kwargs)

            super().autocomplete(option)(new_coro)

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
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
    default_permission: Optional[bool] = MISSING,
    debug_scope: Optional[bool] = True,
) -> SubcommandSetup:
    """
    Use this function to initialize a base for future subcommands.

    Kwargs are optional.

    To use this function without loading the extension, pass in the client as the first argument.

    ```py
    base_name = client.subcommand_base(
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
    * `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.
    """
    log.debug(f"base: {base=}")
    return SubcommandSetup(self, base, description, scope, default_permission, debug_scope)


def ext_subcommand_base(
    base: str,
    *,
    description: Optional[str] = "No description",
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
    default_permission: Optional[bool] = MISSING,
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
