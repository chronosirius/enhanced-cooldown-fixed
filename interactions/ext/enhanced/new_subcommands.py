from inspect import getdoc, signature
from typing import Any, Callable, Coroutine, Dict, List, Optional, Type, Union

from interactions.client.decor import command

from interactions import (
    MISSING,
    Client,
    CommandContext,
    Extension,
    Guild,
    InteractionException,
    Option,
    OptionType,
)

from ._logging import get_logger
from .command_models import parameters_to_options

log = get_logger("subcommand")


class StopCommand:
    """
    A class that when returned from a command, the command chain is stopped.

    Usage:
    ```py
    @bot.command()
    async def foo(ctx):
        ... # do something
        return StopCommand  # does not execute `bar`
        # or `return StopCommand()`

    @foo.subcommand()
    async def bar(ctx): ...
    ```
    """


class BaseResult:
    """
    The result from a base command.

    To get the result from this object, access the `result` attribute or call it.

    Attributes:

    * `result`: The result from the base command.
    """

    __slots__ = ("result",)

    def __init__(self, result: Any) -> None:
        self.result = result

    def __getattr__(self, name: str) -> Any:
        if name == "parent":
            raise AttributeError("There is no parent for the base command result!")
        return super().__getattr__(name)

    def __call__(self) -> Any:
        return self.result

    def __repr__(self) -> str:
        return f"<BaseResult result={self.result}>"

    __str__ = __repr__


class GroupResult:
    """
    The result from a group command.

    To get the result from this object, access the `result` attribute or call it.

    To get the parent result, access the `parent` attribute.

    Attributes:

    * `result`: The result from the group command.
    * `parent: BaseResult`: The `BaseResult` object from the base command.
    """

    __slots__ = ("result", "parent")

    def __init__(self, result: Any, parent: BaseResult) -> None:
        self.result = result
        self.parent = parent

    def __call__(self) -> Any:
        return self.result

    def __repr__(self) -> str:
        return f"<GroupResult result={self.result}, parent={self.parent}>"

    __str__ = __repr__


class SubcommandManager:
    """Manages the subcommand creation from a command."""

    __slots__ = ("m",)

    def __init__(self, manager: "Manager") -> None:
        self.m = manager

    def __call__(
        self,
        _coro: Optional[Coroutine] = MISSING,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
    ) -> Callable[..., Any]:
        """
        Creates a subcommand.

        ```py
        @bot.command()
        async def base(ctx): ...

        @base.subcommand()
        async def subcommand(ctx): ...
        ```

        Parameters:

        * `?name: str`: The name of the subcommand. Defaults to the name of the function.
        * `?description: str`: The description of the subcommand. Defaults to the docstring of the function.
        * `?options: List[Option]`: The options of the subcommand.
        """

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
                else parameters_to_options(params[1:-1])
                if options is MISSING
                and (len(params) > 3 if params.get("self") else len(params) > 2)
                else None
                if options is MISSING
                else options
            )

            if not params:
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            self.m.data.append(
                Option(
                    type=OptionType.SUB_COMMAND,
                    name=_name,
                    description=_description,
                    options=_options,
                )._json
            )
            self.m.coroutines[_name] = coro
            self.m.sync_client_commands()

            return coro

        if _coro is not MISSING:
            return decorator(_coro)
        return decorator


class GroupManager:
    """Manages the group creation in a command."""

    __slots__ = ("m", "group")

    def __init__(self, manager: "Manager") -> None:
        self.m = manager
        self.group: Optional[str] = None

    def __call__(
        self,
        _coro: Optional[Coroutine] = MISSING,
        *,
        group: Optional[str] = MISSING,
    ) -> Callable[..., Any]:
        """
        Creates a group.

        ```py
        @bot.command()
        async def base(ctx): ...

        @base.group()
        async def group(ctx): ...
        ```

        Parameters:

        * `?group: str`: The name of the group. Defaults to the name of the function.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            self.group = coro.__name__ if group is MISSING else group
            self.m.data.append(
                Option(
                    type=OptionType.SUB_COMMAND_GROUP,
                    name=self.group,
                    description=(getdoc(coro) or "No description").split("\n")[0],
                )._json
            )
            self.m.groups.append(self.group)
            self.m.coroutines[self.group] = coro

            coro.subcommand = self.subcommand
            self.m.sync_client_commands()

            return coro

        if _coro is not MISSING:
            return decorator(_coro)
        return decorator

    def subcommand(
        self,
        _coro: Optional[Coroutine] = MISSING,
        *,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        options: Optional[List[Option]] = MISSING,
    ) -> Callable[..., Any]:
        """
        Creates a subcommand in the group.

        ```py
        @bot.command()
        async def base(ctx): ...

        @base.group()
        async def group(ctx): ...

        @group.subcommand()
        async def subcommand(ctx): ...
        ```

        Parameters:

        * `?name: str`: The name of the subcommand. Defaults to the name of the function.
        * `?description: str`: The description of the subcommand. Defaults to the docstring of the function.
        * `?options: List[Option]`: The options of the subcommand.
        """

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
                else parameters_to_options(params[1:-1])
                if options is MISSING
                and (len(params) > 3 if params.get("self") else len(params) > 2)
                else None
                if options is MISSING
                else options
            )

            if not params:
                raise InteractionException(
                    11,
                    message="Your command needs at least one argument to return context.",
                )

            if not self.group:
                raise InteractionException(
                    11,
                    message="You must call `group` before calling `subcommand`.",
                )

            group = next(
                group
                for group in self.m.data
                if group["type"] == OptionType.SUB_COMMAND_GROUP and group["name"] == self.group
            )
            group_index = self.m.data.index(group)

            if group.get("options"):
                self.m.data[group_index]["options"].append(
                    Option(
                        type=OptionType.SUB_COMMAND,
                        name=_name,
                        description=_description,
                        options=_options,
                    )._json
                )
            else:
                self.m.data[group_index]["options"] = [
                    Option(
                        type=OptionType.SUB_COMMAND,
                        name=_name,
                        description=_description,
                        options=_options,
                    )._json
                ]

            self.m.coroutines[f"{self.group} {_name}"] = coro

            self.m.sync_client_commands()

            return coro

        if _coro is not MISSING:
            return decorator(_coro)
        return decorator


class Manager:
    """The internal manager of the subcommands and groups."""

    __slots__ = (
        "base",
        "description",
        "scope",
        "default_permission",
        "debug_scope",
        "client",
        "_self",
        "groups",
        "data",
        "base_coroutine",
        "coroutines",
        "subcommand",
        "group",
    )

    def __init__(
        self,
        coro: Coroutine,
        base: str,
        description: Optional[Union[str, Type[MISSING]]],
        scope: Union[int, Guild, List[int], List[Guild]],
        default_permission: bool,
        debug_scope: bool,
        client: Optional[Client] = None,
        _self: Optional[Extension] = None,
    ) -> None:
        self.base = base
        self.description = (
            "No description" if description is MISSING or description is None else description
        )
        self.scope = scope
        self.default_permission = default_permission
        self.debug_scope = debug_scope
        self.client = client
        self._self = _self

        self.groups: List[str] = []
        self.data: List[dict] = []
        self.base_coroutine: Coroutine = coro
        self.coroutines: Dict[str, Coroutine] = {}

        self.subcommand = SubcommandManager(self)
        self.group = GroupManager(self)

    @property
    def full_data(self) -> Union[dict, List[dict]]:
        """Returns the command in JSON format."""
        return command(
            name=self.base,
            description=self.description,
            options=self.data,
            scope=self.scope,
            default_permission=self.default_permission,
        )

    def sync_client_commands(self) -> None:
        """Synchronizes the commands with the client."""
        if not self.client:
            return

        if not self.client._command_data:
            self.client._command_data = [self.full_data]
        elif any(cmd["name"] == self.base for cmd in self.client._command_data):
            for i, cmd in enumerate(self.client._command_data):
                if cmd["name"] == self.base:
                    self.client._command_data[i] = self.full_data
                    break
        else:
            self.client._command_data.append(self.full_data)

        if not hasattr(self.client, "_command_coros") or not self.client._command_coros:
            self.client._command_coros = {self.base: self.subcommand_caller}
        else:
            self.client._command_coros[self.base] = self.subcommand_caller

    def set_self(self, _self: Extension) -> None:
        """Sets the `self` of the `Extension`."""
        self._self = _self

    async def subcommand_caller(
        self,
        ctx: CommandContext,
        *args,
        sub_command_group: Optional[str] = None,
        sub_command: Optional[str] = None,
        **kwargs,
    ) -> Optional[Any]:
        """Calls all of the coroutines of the subcommand."""
        base_coro = self.base_coroutine
        if self._self:
            base_res = BaseResult(await base_coro(self._self, ctx, *args, **kwargs))
            if base_res() is StopCommand or isinstance(base_res(), StopCommand):
                return
            if self.data:
                if sub_command_group:
                    group_coro = self.coroutines[sub_command_group]
                    subcommand_coro = self.coroutines[f"{sub_command_group} {sub_command}"]
                    group_res = GroupResult(
                        await group_coro(self._self, ctx, base_res, *args, **kwargs), base_res
                    )
                    if group_res() is StopCommand or isinstance(group_res(), StopCommand):
                        return
                    return await subcommand_coro(self._self, ctx, group_res, *args, **kwargs)
                else:
                    subcommand_coro = self.coroutines[sub_command]
                    return await subcommand_coro(self._self, ctx, base_res, *args, **kwargs)
            return base_res
        base_res = BaseResult(await base_coro(ctx, *args, **kwargs))
        if base_res() is StopCommand or isinstance(base_res(), StopCommand):
            return
        if self.data:
            if sub_command_group:
                group_coro = self.coroutines[sub_command_group]
                subcommand_coro = self.coroutines[f"{sub_command_group} {sub_command}"]
                group_res = GroupResult(await group_coro(ctx, base_res, *args, **kwargs), base_res)
                if group_res() is StopCommand or isinstance(group_res(), StopCommand):
                    return
                return await subcommand_coro(ctx, group_res, *args, **kwargs)
            else:
                subcommand_coro = self.coroutines[sub_command]
                return await subcommand_coro(ctx, base_res, *args, **kwargs)
        return base_res
